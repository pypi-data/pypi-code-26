import logging
import time
from behave import step
from selenium import webdriver
from selenium.webdriver.common.by import By

from tutorial.wikipedia_page import WikipediaPage


@step("I open a browser")
def step_impl(context, maximized=True):
    context.driver = webdriver.Chrome()
    if maximized:
        context.driver.maximize_window()

@step("I navigate to the Wikipedia page")
def step_impl(context):
    context.wikipedia_page = WikipediaPage(context.driver)
    logging.info("Navigating to the Wikipedia page")
    context.wikipedia_page.navigate()


@step("I wait for an invalid element")
def step_impl(context):
    context.driver.find_element(By.ID, "invalid")
    time.sleep(3)