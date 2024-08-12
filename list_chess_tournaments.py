from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime


def get_player_html(url):
    """Fetches HTML content from the given URL."""
    response = requests.get(url)
    return response.content


def fix_headers(headers):
    """Fixes headers by adding the 'Link' column."""
    if "Link" not in headers:
        index_to_insert = next(
            (i for i, header in enumerate(headers) if "FideID" in header), None
        )
        if index_to_insert is not None:
            headers.insert(index_to_insert + 1, "Link")
    return headers


def extract_year_from_title(title):
    """Extracts the year from the title string if present."""
    match = re.search(r'\d{4}', title)
    if match:
        return int(match.group(0))
    return None


def extract_date_from_update(text):
    """Extracts the date from the last update text."""
    match = re.search(r'Last update (\d{2}\.\d{2}\.\d{4})', text)
    if match:
        return datetime.strptime(match.group(1), "%d.%m.%Y").date()
    return None


def get_tournament_date(soup, title):
    """Get the tournament date from the title or last update date."""
    year = extract_year_from_title(title)
    if year:
        return datetime(year, 1, 1).date()

    last_update_text = soup.find("p", class_="CRsmall")
    if last_update_text:
        return extract_date_from_update(last_update_text.text)

    return None  # If no date could be extracted


def click_show_tournament_data(driver):
    """Clicks 'Show tournament data' if the button exists."""
    try:
        show_data_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Show tournament data"))
        )
        show_data_button.click()
    except Exception as e:
        print("No 'Show tournament data' button found:", e)


def click_show_tournament_details(driver):
    """Clicks 'Show tournament details' and returns the HTML."""
    try:
        show_details_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "Show tournament details"))
        )

        html_pages = []
        for link in show_details_links:
            link.click()
            time.sleep(2)  # Waiting for the details page to load
            html_pages.append(driver.page_source)
            driver.back()  # Going back to the previous page
            time.sleep(2)

        return html_pages

    except Exception as e:
        print("No 'Show tournament details' links found or error occurred:", e)
        return []


def extract_info_from_html(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    profile_info = soup.find("div", class_="profile-top-info")

    if profile_info is not None:
        federation = profile_info.find_all(
            "div", class_="profile-top-info__block__row__data"
        )[1].text.strip()
        b_year = profile_info.find_all(
            "div", class_="profile-top-info__block__row__data"
        )[3].text.strip()
        sex = profile_info.find_all("div", class_="profile-top-info__block__row__data")[
            4
        ].text.strip()
        fide_title = profile_info.find_all(
            "div", class_="profile-top-info__block__row__data"
        )[5].text.strip()
        world_rank = profile_info.find(
            "div", class_="profile-top-info__block__row__data"
        ).text.strip()
        print(federation, b_year, sex, fide_title, world_rank)
        return federation, b_year, sex, fide_title, world_rank
    else:
        return None, None, None, None, None


def parse_fide_data(df):
    if "Link" in df.columns and not df["Link"].isnull().all():
        print(df)
        df = df.dropna(subset=["Link"])
        df = df[df["Link"].str.startswith("http")]
        df[["Federation", "Birth Year", "Sex", "FIDE Title", "World Rank"]] = df[
            "Link"
        ].apply(lambda x: pd.Series(extract_info_from_html(x)))
        return df
    else:
        return None


def create_dataframe(headers, data):
    """Creates a DataFrame from table headers and data."""
    try:
        df = pd.DataFrame(data, columns=headers).iloc[1:, :]
        return df
    except Exception as e:
        print("File can't be processed:", headers, data[:50])
        return pd.DataFrame()


def process_url(url, save_path="processed_data"):
    driver = setup_driver()
    driver.get(url)

    try:
        click_show_tournament_data(driver)

        html_pages = click_show_tournament_details(driver)

        for html_content in html_pages:
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.title.string.strip().replace(
                "Chess-Results_Server_Chess-results.com_-_", ""
            )
            print("Title:", title)

            tournament_date = get_tournament_date(soup, title)
            print("Tournament Date:", tournament_date)

            table = soup.find("table", class_="CRs1")
            headers = [header.text.strip() for header in table.find_all("th")]
            headers = fix_headers(headers)

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
            if table_data is not None:
                df = create_dataframe(headers, data)
                if "Link" in df.columns:
                    df = parse_fide_data(df)
                    df = df[df["Link"].notna()]
                    df["Tournament_Date"] = tournament_date
                    filename = f"{title.replace(' ', '_')}.csv"
                    df.to_csv(os.path.join(save_path, filename), index=False)
    finally:
        driver.quit()


def setup_driver():
    """Setup and return a Chrome WebDriver."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def open_website(driver, url):
    """Open a website given its URL."""
    driver.get(url)


def accept_cookies(driver):
    """Accept cookies on the website if the dialog appears."""
    try:
        agree_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-47sehv"))
        )
        agree_button.click()
    except Exception as e:
        print(f"Could not find the cookies acceptance button: {e}")


def set_tournament_and_dates(driver, query):
    """Set the tournament search criteria and dates."""
    tournament_input = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[aria-labelledby='P1_lb_bez']")
        )
    )
    tournament_input.clear()
    tournament_input.send_keys(query)

    start_date_input = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "P1_txt_von_tag"))
    )
    end_date_input = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "P1_txt_bis_tag"))
    )

    start_date_input.clear()
    start_date_input.send_keys("01.01.2008")
    end_date_input.clear()
    end_date_input.send_keys("01.01.2020")


def set_max_results(driver, value):
    """Set the maximum number of result lines in the search."""
    max_lines_dropdown = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "P1_combo_anzahl_zeilen"))
    )
    Select(max_lines_dropdown).select_by_value(value)


def get_tournament_links(driver):
    """Fetch all the tournament links from the results table."""
    links = []
    elements = driver.find_elements(By.CSS_SELECTOR, "table.CRs2 a")
    for element in elements:
        links.append(element.get_attribute("href"))
    return links


def get_html(driver, link):
    """Navigate to the link and retrieve the HTML content."""
    driver.get(link)
    time.sleep(3)  # Giving the page time to load
    return driver.page_source


def search_and_collect_data(driver, query):
    """Set search parameters, conduct search, and collect data links."""
    set_tournament_and_dates(driver, query)
    set_max_results(driver, "5")  # Assuming '5' corresponds to '2000'
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input[aria-labelledby='P1_lb_bez']")
        )
    ).send_keys(Keys.ENTER)
    return get_tournament_links(driver)


def main():
    queries = ["European Youth", "International Open", "World Youth"]

    # Create processed_data directory if it doesn't exist
    save_path = "processed_data"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    driver = setup_driver()
    open_website(driver, "https://chess-results.com/TurnierSuche.aspx?lan=1")
    accept_cookies(driver)

    for query in queries:
        print("Processing query:", query)

        csv_filename = query + ".csv"
        if not os.path.exists(csv_filename):
            links = search_and_collect_data(driver, query)
            print("Tournament links for query", query, ":", links)

            df = pd.DataFrame({"Link": links, "Checked": False})
            df.to_csv(csv_filename, index=False)

        else:
            df = pd.read_csv(csv_filename)
            links = df.loc[df["Checked"] == False, "Link"].tolist()

        for link in links:
            process_url(link, save_path=save_path)
            df.loc[df["Link"] == link, "Checked"] = True
            df.to_csv(csv_filename, index=False)

    driver.quit()


if __name__ == "__main__":
    main()
