from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver

import math
import time


url = 'https://smile.amazon.com/ga/giveaways/?pageId={0}'

class EcWithout:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, ec, without=''):
        self.ec = ec
        self.without = None
        if without != '':
            self.without = without

    def __call__(self, browser):
        present = self.ec(browser)
        if present:
            if self.without:
                classes = present.get_attribute('class')
                if self.without in classes:
                    return False
                return True
            else:
                return True
        return False


def get_offers(browser):
    tt = browser.find_elements_by_xpath('//ul[@class="listing-info-container"]//li//div//a')
    offers = [a.get_attribute('href') for a in tt]
    print(offers)
    return offers


def clicker(browser, offer):
    print(f'getting {offer}')
    browser.get(offer)
    time.sleep(3)
    try:
        # Already checked
        tt = browser.find_element_by_xpath('//span[contains(text(), "Add to cart")]')
        if tt:
            return
    except NoSuchElementException:
        pass
    try:
        # a youtube video
        tt = browser.find_element_by_xpath('//iframe[contains(@class, "video")]')
        if isinstance(tt, list):
            raise NoSuchElementException
        time.sleep(2)
        actions = webdriver.common.action_chains.ActionChains(browser)
        actions.move_to_element_with_offset(tt, 10, 10)
        actions.click()
        actions.perform()

        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'youtube-continue-button'))
        WebDriverWait(browser, 30).until(EcWithout(element_present, without='a-button-disabled'))
        time.sleep(1)
        tt = browser.find_element_by_xpath('//button[contains(@class, "youtube-continue-button")]')
        tt.click()
        return
    except (NoSuchElementException, ) as e:
        pass
    try:
        # amazon video
        tt = browser.find_element_by_xpath('//video[contains(@class, "video")]')
        if isinstance(tt, list):
            raise NoSuchElementException
        time.sleep(2)
        actions = webdriver.common.action_chains.ActionChains(browser)
        actions.move_to_element_with_offset(tt, 10, 10)
        actions.click()
        actions.perform()

        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'amazon-video-continue-button'))
        WebDriverWait(browser, 30).until(EcWithout(element_present, without='a-button-disabled'))
        time.sleep(1)
        tt = browser.find_element_by_xpath('//button[contains(@class, "amazon-video-continue-button")]')
        tt.click()
        return
    except (NoSuchElementException, ) as e:
        pass
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Tap the box to see if you win")]'))
        WebDriverWait(browser, 30).until(element_present)
        tt = browser.find_element_by_xpath('//a[contains(text(), "Tap the box to see if you win")]')
        tt.click()
        time.sleep(5)
        return
    except NoSuchElementException:
        pass
    return


def did_i_win(browser):
    time.sleep(3)
    did_win_xpath = '//span[(contains(@class, "prize-title")) and (contains(text(), "jorge"))]'
    element_present = EC.presence_of_element_located((By.XPATH, did_win_xpath))
    WebDriverWait(browser, 31).until(element_present)
    tt = browser.find_element_by_xpath(did_win_xpath)
    text = tt.text
    won = 'didn\'t' not in text
    print(f'{won} {text}')
    if won:
        raise Exception('you Won!')


def navigator(browser):
    page = 1
    browser.get(url.format(page))
    time.sleep(2)
    tt = browser.find_elements_by_xpath('//ul[@class="a-pagination"]//li')[-2]
    total_pages = int(tt.text)

    for pages in range(total_pages):
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'a-pagination'))
            WebDriverWait(browser, 5).until(element_present)
            for offer in get_offers(browser):
                clicker(browser, offer)
                did_i_win(browser)
        except TimeoutException:
            pass
        page += 1
        if page > total_pages:
            raise Exception('out of pages')
        print(f'current page is {page}')
        browser.get(url.format(page))
