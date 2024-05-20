import unittest
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
import pandas as pd
import os
from list_chess_tournaments import (
    get_player_html, fix_headers, parse_table, extract_info_from_html,
    parse_fide_data, create_dataframe, process_url, setup_driver, open_website,
    accept_cookies, set_tournament_and_dates, set_max_results, get_tournament_links,
    get_html, search_and_collect_data, main
)


class TestYouthChess(unittest.TestCase):

    def setUp(self):
        self.driver = setup_driver()
    
    def tearDown(self):
        self.driver.quit()

    # Functional Testing

    def test_web_scraping_setup(self):
        """Verify web scraping setup"""
        try:
            driver = setup_driver()
            self.assertIsNotNone(driver)
        except Exception as e:
            self.fail(f"Web scraping setup failed: {e}")

    def test_website_opening(self):
        """Verify website opening"""
        try:
            open_website(self.driver, "https://chess-results.com/TurnierSuche.aspx?lan=1")
            self.assertIn("Chess-Results", self.driver.title)
        except Exception as e:
            self.fail(f"Website opening failed: {e}")

    def test_accept_cookies(self):
        """Verify cookies acceptance"""
        try:
            open_website(self.driver, "https://chess-results.com/TurnierSuche.aspx?lan=1")
            accept_cookies(self.driver)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Cookies acceptance failed: {e}")

    def test_tournament_search_and_data_retrieval(self):
        """Check tournament search and data retrieval"""
        try:
            open_website(self.driver, "https://chess-results.com/TurnierSuche.aspx?lan=1")
            accept_cookies(self.driver)
            links = search_and_collect_data(self.driver, "European Youth")
            self.assertGreater(len(links), 0)
        except Exception as e:
            self.fail(f"Tournament search and data retrieval failed: {e}")

    def test_parse_table(self):
        """Verify data parsing from HTML"""
        sample_html = "<html>...</html>"  # Use actual sample HTML content
        try:
            headers, data, title = parse_table(sample_html)
            self.assertIsNotNone(headers)
            self.assertIsNotNone(data)
            self.assertIsNotNone(title)
        except Exception as e:
            self.fail(f"Parsing table failed: {e}")

    def test_data_enrichment_from_fide(self):
        """Verify data enrichment from FIDE site"""
        link = "sample_fide_link"  # Use actual sample link
        try:
            federation, b_year, sex, fide_title, world_rank = extract_info_from_html(link)
            self.assertIsNotNone(federation)
            self.assertIsNotNone(b_year)
            self.assertIsNotNone(sex)
            self.assertIsNotNone(fide_title)
            self.assertIsNotNone(world_rank)
        except Exception as e:
            self.fail(f"Data enrichment from FIDE site failed: {e}")

    # Performance Testing

    def test_data_scraping_performance(self):
        """Measure data scraping performance"""
        start_time = time.time()
        try:
            main()
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.assertLess(elapsed_time, 600)  # Adjust time limit as per your requirement
        except Exception as e:
            self.fail(f"Data scraping performance test failed: {e}")

    # Usability Testing

    def test_usability_of_output_files(self):
        """Verify user-friendliness of data outputs"""
        try:
            main()
            for query in ["European Youth", "International Open", "World Youth"]:
                filename = f"{query}.csv"
                self.assertTrue(os.path.exists(filename))
                df = pd.read_csv(filename)
                self.assertIn("Link", df.columns)
        except Exception as e:
            self.fail(f"Usability of output files test failed: {e}")

    # Error Handling

    def test_invalid_url_handling(self):
        """Test error handling for invalid URLs"""
        try:
            content = get_player_html("invalid-url")
            self.assertIsNone(content)
        except Exception as e:
            self.fail(f"Error handling for invalid URLs failed: {e}")

    def test_non_standard_table_handling(self):
        """Test handling of non-standard table structures"""
        sample_html = "<html>...</html>"  # Use HTML content with non-standard structure
        try:
            headers, data, title = parse_table(sample_html)
            self.assertIsNone(data)
        except Exception as e:
            self.fail(f"Handling of non-standard table structures failed: {e}")

    # Data Validity

    def test_data_consistency(self):
        """Ensure data consistency"""
        sample_link = "sample_fide_link"
        try:
            federation, b_year, sex, fide_title, world_rank = extract_info_from_html(sample_link)
            expected_data = {
                "federation": "XYZ",
                "b_year": "2000",
                "sex": "Male",
                "fide_title": "GM",
                "world_rank": "10"
            }
            self.assertEqual(federation, expected_data["federation"])
            self.assertEqual(b_year, expected_data["b_year"])
            self.assertEqual(sex, expected_data["sex"])
            self.assertEqual(fide_title, expected_data["fide_title"])
            self.assertEqual(world_rank, expected_data["world_rank"])
        except Exception as e:
            self.fail(f"Data consistency check failed: {e}")

    # Integration Testing

    def test_integration(self):
        """Test end-to-end data collection and processing"""
        try:
            main()
            for query in ["European Youth", "International Open", "World Youth"]:
                filename = f"{query}.csv"
                self.assertTrue(os.path.exists(filename))
                df = pd.read_csv(filename)
                self.assertIn("Link", df.columns)
                self.assertFalse(df['Link'].isnull().all())
        except Exception as e:
            self.fail(f"End-to-end integration test failed: {e}")


if __name__ == "__main__":
    unittest.main()
