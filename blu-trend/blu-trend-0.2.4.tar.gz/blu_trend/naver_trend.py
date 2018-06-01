from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from blu_trend import trend_to_json_parser
import chromedriver_binary


class Naver_trend():
    def __init__(self):
        super().__init__()

    def crawl_trend(self):
        TEST_URL = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        # UserAgent값을 바꿔줍시다!
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver=None;
        trend_text = None;
        try:
            driver = webdriver.Chrome(chromedriver_binary.chromedriver_filename, chrome_options=options)
            driver.get(TEST_URL)
            xxx = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='keyword_rank select_date']")))
            trend_text = xxx.text
        except (WebDriverException, TimeoutException, NoSuchElementException) as e:
            print(e.message)
        finally:
            driver.quit()
        return trend_text

    def get_trend_json(self,destination):
        j = trend_to_json_parser.naver_trend_to_json(self.crawl_trend())
        return j
        # f = open(destination+"naver_trend.json", 'wb')
        # f.write(j)
        # f.close()
