from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    """Setup and return a Chrome WebDriver."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def open_website(driver, url):
    """Open a website given its URL."""
    driver.get(url)

def accept_cookies(driver):
    """Accept cookies on the website if the dialog appears."""
    try:
        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-47sehv")))
        agree_button.click()
    except Exception as e:
        print(f"Could not find the cookies acceptance button: {e}")

def set_tournament_and_dates(driver):
    """Set the tournament search criteria and dates."""
    tournament_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-labelledby='P1_lb_bez']")))
    tournament_input.send_keys("U12")

    start_date_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "P1_txt_von_tag")))
    end_date_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "P1_txt_bis_tag")))

    start_date_input.clear()
    start_date_input.send_keys("01.01.2008")
    end_date_input.clear()
    end_date_input.send_keys("01.01.2020")

def set_max_results(driver, value):
    """Set the maximum number of result lines in the search."""
    max_lines_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "P1_combo_anzahl_zeilen")))
    Select(max_lines_dropdown).select_by_value(value)

def main():
    driver = setup_driver()

    open_website(driver, "https://chess-results.com/TurnierSuche.aspx?lan=1")
    
    accept_cookies(driver)
    
    set_tournament_and_dates(driver)
    
    set_max_results(driver, "5")  # 5 corresponds to 2000 results
    
    # Submit the search
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-labelledby='P1_lb_bez']"))
    ).send_keys(Keys.ENTER)
    
    time.sleep(10)
    
    # html_content = driver.page_source
    # print(html_content)

    driver.quit()

if __name__ == "__main__":
    main()
