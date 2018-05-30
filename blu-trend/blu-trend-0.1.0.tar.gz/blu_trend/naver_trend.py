from selenium import webdriver
from blu_trend import trend_to_json_parser
import chromedriver_binary
import platform
import os

TEST_URL = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# UserAgent값을 바꿔줍시다!
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
driver = None;
os_name = platform.system()
driver_path = os.path.abspath('')
if(os_name == "Linux"):
    driver = webdriver.Chrome("./linux_chromedriver",chrome_options=options)
else:
    driver = webdriver.Chrome(chrome_options=options)
        #.Chrome(chrome_options=options)
driver.get(TEST_URL)
xxx = driver.find_element_by_css_selector("div[class='keyword_rank select_date']")
def save_json_trend():
    j = trend_to_json_parser.naver_trend_to_json(xxx.text)
    f = open("naver_trend.json", 'w')
    f.write(j)
    f.close()