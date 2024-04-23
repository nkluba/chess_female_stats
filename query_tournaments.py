from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

def accept_cookies(driver):
    try:
        wait = WebDriverWait(driver, 10)
        
        agree_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-47sehv")))
        agree_button.click()
        
        time.sleep(2)
    except Exception as e:
        print("Could not find the cookie acceptance button:", e)


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open targeted website
driver.get("https://chess-results.com/TurnierSuche.aspx?lan=1")

accept_cookies(driver)

html_content = driver.page_source

wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds
tournament_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-labelledby='P1_lb_bez']"))
)

tournament_input.send_keys("U12")

max_lines_dropdown = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "P1_combo_anzahl_zeilen"))
)
Select(max_lines_dropdown).select_by_value("5")

start_date_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "P1_txt_von_tag"))
end_date_input = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "P1_txt_bis_tag"))
)

# Clear the input fields before sending keys
start_date_input.clear()
start_date_input.send_keys("01.01.2008")

end_date_input.clear()
end_date_input.send_keys("01.01.2020")

tournament_input.send_keys(Keys.ENTER)

time.sleep(10)

driver.quit()
