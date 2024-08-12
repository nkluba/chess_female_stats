import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_html(url):
    """Fetches HTML content from the given URL."""
    response = requests.get(url)
    return response.content


def parse_table(html_content):
    """Parses HTML content and extracts table data."""
    soup = BeautifulSoup(html_content, "html.parser")
    title = soup.title.string.strip()
    print(title)
    table = soup.find("table", class_="CRs1")
    headers = [header.text.strip() for header in table.find_all("th")]
    headers.insert(5, "Link")
    data = []
    for row in table.find_all("tr"):
        row_data = []
        for cell in row.find_all(["td", "th"]):
            if cell.find("a"):  # If cell contains a link
                link = cell.find("a")["href"]
                row_data.append(cell.text.strip())
                row_data.append(link)
            else:
                row_data.append(cell.text.strip())
        if row_data:
            data.append(row_data)
    return headers, data, title


def extract_info_from_html(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    profile_info = soup.find('div', class_='profile-top-info')

    federation = profile_info.find_all('div', class_='profile-top-info__block__row__data')[1].text.strip()
    b_year = profile_info.find_all('div', class_='profile-top-info__block__row__data')[3].text.strip()
    sex = profile_info.find_all('div', class_='profile-top-info__block__row__data')[4].text.strip()
    fide_title = profile_info.find_all('div', class_='profile-top-info__block__row__data')[5].text.strip()
    world_rank = profile_info.find('div', class_='profile-top-info__block__row__data').text.strip()
    print(federation, b_year, sex, fide_title, world_rank)
    return federation, b_year, sex, fide_title, world_rank


def parse_fide_data(df):
    df[['Federation', 'B-Year', 'Sex', 'FIDE Title', 'World Rank']] = df['Link'].apply(lambda x: pd.Series(extract_info_from_html(x)))
    return df


def create_dataframe(headers, data):
    """Creates a DataFrame from table headers and data."""
    return pd.DataFrame(data, columns=headers).iloc[1: , :]


def process_url(url, save_path = "processed_data"):
    html_content = get_html(url)
    headers, table_data, title = parse_table(html_content)
    df = parse_fide_data(create_dataframe(headers, table_data))
    filename = f"{title.replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)


def main():
    process_url("https://chess-results.com/tnr178566.aspx?lan=1")


if __name__ == "__main__":
    main()
