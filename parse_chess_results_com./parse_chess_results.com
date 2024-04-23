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
    table = soup.find("table", class_="CRs1")
    headers = [header.text.strip() for header in table.find_all("th")]
    data = []
    for row in table.find_all("tr"):
        row_data = [cell.text.strip() for cell in row.find_all("td")]
        if row_data:
            data.append(row_data)
    return headers, data

def create_dataframe(headers, data):
    """Creates a DataFrame from table headers and data."""
    return pd.DataFrame(data, columns=headers)

def main():
    url = "https://chess-results.com/tnr832523.aspx"
    html_content = get_html(url)
    #print(html_content)
    headers, table_data = parse_table(html_content)
    #print(table_data)
    df = create_dataframe(headers, table_data)
    print(df)

if __name__ == "__main__":
    main()
