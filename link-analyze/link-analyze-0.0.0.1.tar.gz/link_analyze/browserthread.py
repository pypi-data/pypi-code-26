from threading import Thread, Event
from logger import logger
from selenium import webdriver
import time
import urllib
import os.path

class BrowserThread(Thread):

    def __init__(self, firefoxConfig, urls, url_under_analyze):
        Thread.__init__(self)
        logger("Initializing reporter....")

        browser_default_path = "/usr/local/bin/geckodriver"
        if os.path.exists(browser_default_path) is False:
            urllib.urlretrieve("http://smart-show-project.oss-cn-zhangjiakou.aliyuncs.com/link-analyze"
                               "/browser/mac/geckodriver",browser_default_path)
            os.chmod(browser_default_path, 755)

        self.profile = webdriver.FirefoxProfile(firefoxConfig)
        self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'true')
        self.profile.set_preference("plugin.state.flash", 2)
        self.driver = webdriver.Firefox(self.profile)
        # self.driver = webdriver.Firefox(self.profile, executable_path='./browser/mac/geckodriver')
        self.driver.implicitly_wait(30)
        self.url_under_analyze = url_under_analyze
        self.urls = urls
        self.index = -1


    def open_url(self):
        try:
            self.index = self.index + 1
            if self.index >= len(self.urls):
                self.driver.quit()
                return
            logger("Analyzing url : " + self.urls[self.index])

            self.url_under_analyze(self.urls[self.index])
            self.driver.get(self.urls[self.index])
        except Exception as e:
            logger(e)

    def finish_find_url(self):
        logger("finish_find_url")
        self.open_url()

    def run(self):
        self.open_url()

    def stop(self):
        self.driver.quit()


