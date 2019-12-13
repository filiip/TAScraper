# coding utf-8

import csv
import logging
import time

import chromedriver_binary

from selenium import webdriver
from selenium.common import exceptions as exc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


# Input list
INPUT = [
    "https://www.tripadvisor.com/AttractionProductReview-g608929-d13225409-Boat_Tour_Egadi_Day_to_discover_Favignana_and_Levanzo-Castellammare_del_Golfo_Prov.html",
    "https://www.tripadvisor.com/Attraction_Review-g1199297-d2320423-Reviews-Spiaggia_dei_Faraglioni-Scopello_Castellammare_del_Golfo_Province_of_Trapani_Sic.html",
    "https://www.tripadvisor.com/Attraction_Review-g657290-d2213040-Reviews-Ex_Stabilimento_Florio_delle_Tonnare_di_Favignana_e_Formica-Isola_di_Favignana_Ae.html",
    "https://www.tripadvisor.com/AttractionProductReview-g187886-d15754813-Yacht_Day_Private_Tour_in_Favignana_and_Levanzo-Sicily.html"
    ]

# Xpaths
REVIEW_TAB = ".//div[@id='REVIEWS' and @data-tab='TABS_REVIEWS']"
TAB_CHECK = "//*[text()='Write a review']"
PAGE_NUMS = ".//div[@class='pageNumbers']"
MORE = ["//span[@class='location-review-review-list-parts-ExpandableReview__cta--2mR2g']",
        "//span[@class='taLnk ulBlueLinks']"]
REVIEW_CONTS = "//div[contains(@class, 'review-container') or contains(@class, 'reviewContainer')]"
RATING = ".//span[contains(@class, 'ui_bubble_rating bubble_')]"
REVIEW = (".//*[@class='location-review-review-list-parts-ExpandableReview__reviewText--gOmRC' "
         "or @class='prw_rup prw_reviews_text_summary_hsx']")
REVIEW_TEXT = [".//p[@class='partial_entry']",
               ".//span"]
NEXT = ".//a[contains(@class, 'next') and contains(@class, 'nav') and contains(@class, 'ui_button')]"
SHOW_LESS = "//span[text()='Show less' or text()='Read less']"


class NoConnectionError(Exception):
    pass


def exists(xpath, elem):
    """Check if element specified by xpath exists under a given element

    :param xpath: xpath of searched element
    :type xpath: str
    :param elem: parent to search from
    :type elem: selenium.webdriver.remote.webelement.WebElement
    :return: True => exists; False => deos not exist
    :rtype: bool
    """
    if not elem:
        elem = driver
    try:
        elem.find_element_by_xpath(xpath)
    except exc.NoSuchElementException:
        return False
    return True


def click(xpath, elem, timeout):
    """Click on element spcified by xpath

    :param xpath: xpath of searched element
    :type xpath: str
    :param elem: parent to search from
    :type elem: selenium.webdriver.remote.webelement.WebElement
    :param timeout: timout to wait until the element is clickable in seconds
    :type timeout: int
    """
    attempts = 100
    for attempt in range(attempts):
        try:
            WebDriverWait(elem, timeout).until(ec.element_to_be_clickable((By.XPATH, xpath))).click()
            break
        except (exc.ElementClickInterceptedException, exc.StaleElementReferenceException):
            if attempt < attempts - 1:
                time.sleep(0.1)
                continue
            else:
                raise


def _show_more(xpath, elem):
    """Open full review by clicking on 'more' button and wait for it to be open

    :param xpath: xpath of searched element
    :type xpath: str
    :param elem: parent to search from
    :type elem: selenium.webdriver.remote.webelement.WebElement
    """
    click(xpath, elem, 20)
    time.sleep(0.5)
    WebDriverWait(elem, 10).until(ec.element_to_be_clickable((By.XPATH, SHOW_LESS)))


def _get_review_text(container):
    """Get review text from a review container

    :param container: container with a review to extract
    :type container: selenium.webdriver.remote.webelement.WebElement
    :return: text of a review from container
    :rtype: str
    """
    review = container.find_element_by_xpath(REVIEW)
    try:
        text = review.find_element_by_xpath(REVIEW_TEXT[0]).text
    except exc.NoSuchElementException:
        text = review.find_element_by_xpath(REVIEW_TEXT[1]).text
    return text


def _check_connection(driver):
    """Check connection to the server is working was established,
       raise exception if connection was not established

    :param driver: selenium web driver with a loaded page
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    """
    try:
        err = driver.find_element(By.CLASS_NAME, "error-code")
    except:
        logging.debug("Connection established")
    else:
        raise NoConnectionError("Could not connect to desired server -", err.text)


def crawl(driver, url, attempt):
    """Crawl trough a given page and save review data to a csv file

    :param driver: selenium web driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: url of the page
    :type url: str
    """
    start = time.time()
    logging.debug("Scrap '{url}', attempt {attempt}".format(url=url, attempt=attempt))
    try:
        csv_file = open("my_results.csv", "w")
        csv_writer = csv.writer(csv_file)
        driver.get(url)
        _check_connection(driver)
        if attempt == 1:
            logging.info("Checking: {}".format(driver.title))
            csv_writer.writerow([driver.title])

        # Find the correct tab ith reviews
        for tab in driver.find_elements_by_xpath(REVIEW_TAB):
            if exists((TAB_CHECK), tab):
                parent = tab.find_element_by_xpath("..")
                break
        else:
            raise exc.NoSuchElementException("Could not find element {}".format(TAB_CHECK))

        # Check number of pages
        if exists(PAGE_NUMS, parent):
            page_nums = parent.find_element_by_xpath(PAGE_NUMS)
            max_page = page_nums.find_elements_by_xpath(".//*")[-1].text
        else:
            max_page = 1

        logging.debug("Found {} pages".format(max_page))
        for page in range(int(max_page)):
            logging.debug("Checking page {}".format(page+1))
            WebDriverWait(parent, 5).until(ec.presence_of_element_located((By.XPATH, TAB_CHECK)))
            if exists(MORE[0], parent):
                _show_more(MORE[0], parent)
            elif exists(MORE[1], parent):
                _show_more(MORE[1], parent)

            containers = driver.find_elements_by_xpath(REVIEW_CONTS)
            logging.debug("Found {} containers".format(len(containers)))
            for container in containers:
                if exists(RATING, container):
                    attr_class = container.find_element_by_xpath(RATING).get_attribute("class")
                    stars = attr_class.split("_")[3]
                else:
                    stars = "-"

                text = _get_review_text()
                csv_writer.writerow([stars, text])

            if page < int(max_page) - 1:
                click(NEXT, parent, 5)
                time.sleep(0.5)

        logging.info("Total time: {} s".format(round(time.time() - start, 2)))
    finally:
        csv_file.close()


def main():
    attempts = 3
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    driver = webdriver.Chrome(chromedriver_binary.chromedriver_filename)

    try:
        for url in INPUT:
            for attempt in range(1, attempts+1):
                try:
                    crawl(driver, url, attempt)
                    break
                except Exception as Error:
                    if attempt < attempts:
                        logging.warning("Caught {}, retry".format(Error))
                        continue
                    else:
                        raise
    finally:
        driver.close()


if __name__ == '__main__':
    main()
