import logging
import time
from behave import step
import os
from selenium import webdriver
from lib.common.decorators import dec_log_execution_time


@step("I search for the text '{search_text}'")
def step_impl(context, search_text):
    logging.info("Searching for the text '{}'".format(search_text))
    context.wikipedia_page.search_for(search_text)
    time.sleep(1)


@step("I see in the page '{page_title}'")
def step_impl(context, page_title):
    assert context.wikipedia_page.get_search_result_title() == page_title


@step("I test logging")
def step_impl(context):
    logging.info("I'm opening the web_1 page...")
    logging.debug("Testing debug message")
    logging.warning("Warning message")
    logging.error("Error message")


@step("I go to the Google web_1 page")
@dec_log_execution_time
def step_impl(context):
    context.driver.get("https://www.google.com")
    context.driver.get_screenshot_as_file(os.path.join(os.getcwd(), "output", "Google_page.png"))
    time.sleep(3)
