from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from blu_trend import trend_to_json_parser
import chromedriver_binary
import logging
import traceback


class Melon_chart():
    def __init__(self):
        super().__init__()

    def crawl_trend(self):
        TEST_URL1 = 'https://www.melon.com/chart/'
        TEST_URL2 = 'https://www.melon.com/chart/#params%5Bidx%5D=51'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        # UserAgent값을 바꿔줍시다!
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver_1_to_50 =None;
        driver_51_to_100 = None;
        melon_chart_artist_title = {};
        try:
            driver_1_to_50 = webdriver.Chrome(chromedriver_binary.chromedriver_filename, chrome_options=options)
            driver_1_to_50.get(TEST_URL1)
            title_1_to_50 = WebDriverWait(driver_1_to_50, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank01")))
            artist_1_to_50 = WebDriverWait(driver_1_to_50, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst50 > td:nth-child(6) > div > div > div.ellipsis.rank02")))
            link_1_t0_50 = WebDriverWait(driver_1_to_50, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst50 > td:nth-child(9) > div > button")))

            driver_51_to_100 = webdriver.Chrome(chromedriver_binary.chromedriver_filename, chrome_options=options)
            driver_51_to_100.get(TEST_URL2)
            title_51_to_100 = WebDriverWait(driver_51_to_100, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst100 > td:nth-child(6) > div > div > div.ellipsis.rank01")))
            artist_51_to_100 = WebDriverWait(driver_51_to_100, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst100 > td:nth-child(6) > div > div > div.ellipsis.rank02")))
            link_51_tp_100 =  WebDriverWait(driver_51_to_100, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#lst100 > td:nth-child(9) > div > button")))

            title_webelement = title_1_to_50 + title_51_to_100
            artist_webelement = artist_1_to_50 + artist_51_to_100
            link_webelement = link_1_t0_50 + link_51_tp_100
            artist = {}
            title = {}
            link = {}
            for idx in range (0,len(artist_webelement)):
                artist[idx] = artist_webelement[idx].text
                title[idx] = title_webelement[idx].text
                link[idx] = link_webelement[idx].get_attribute("onclick")
            melon_chart_artist_title[0] = artist
            melon_chart_artist_title[1] = title
            melon_chart_artist_title[2] = link
        except (WebDriverException, TimeoutException, NoSuchElementException):
            logging.error(traceback.format_exc())
        finally:
            driver_1_to_50.quit()
            driver_51_to_100.quit()
        return melon_chart_artist_title

    def get_trend_json(self):
        j = trend_to_json_parser.melon_chart_to_json(self.crawl_trend())
        return j
        # f = open(destination+"melon_chart.json", 'wb')
        # f.write(j)
        # f.close()
