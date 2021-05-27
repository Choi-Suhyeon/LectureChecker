"""
Version: 3.9.5
OS     : Windows 10 Pro
Name   : subject_id
Purpose: To get each subject's id (additionally make the black board logged in)
"""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import warnings
import time
import re


def extract_id(origin: str) -> str: return origin[13:-2]


def extract_name(origin: str) -> str:
    return re.sub(r'\([^)]*\)', '', origin[12 if '세종' in origin else 0:]).replace(')', '')


def get_name_id_pairs(user_id, user_pw):
    dr_addr = './driver/chromedriver.exe'
    bb_addr = 'https://kulms.korea.ac.kr/#'
    entry_notice_xpath = '//*[@id="modalPush"]/div/div/div[1]/button/span[2]'
    entry_login_xpath = '/html/body/div[2]/div/div/section/div/div/div/div[1]/div/div[2]/h3/strong/a'
    login_input_id_name = 'one_id'
    login_input_pw_name = 'user_password'
    login_btn_selector = '#loginFrm > div.form-button > div:nth-child(1) > button'
    bb_menu_bar_selector = '#main-content-inner > div > header > section > button'
    bb_courses_xpath = '//*[@id="base_tools"]/bb-base-navigation-button[4]/div/li/a'
    id_name_tag = 'a'
    id_name_class = 'course-title ellipsis hide-focus-outline large-10 medium-10 small-12'

    warnings.filterwarnings('ignore')

    driver = webdriver.Chrome(dr_addr)
    driver.implicitly_wait(5)
    driver.set_window_size(600, 800)
    driver.get(bb_addr)

    driver.find_element(By.XPATH, entry_notice_xpath).click()
    driver.find_element(By.XPATH, entry_login_xpath).click()

    driver.find_element(By.NAME, login_input_id_name).send_keys(user_id)
    driver.find_element(By.NAME, login_input_pw_name).send_keys(user_pw)
    driver.find_element(By.CSS_SELECTOR, login_btn_selector).send_keys(Keys.ENTER)

    time.sleep(4)

    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, bb_menu_bar_selector).click()
            time.sleep(0.5)

            driver.find_element(By.XPATH, bb_courses_xpath).click()
            break

        except StaleElementReferenceException:
            time.sleep(3)

    time.sleep(4)

    while True:
        tags = driver.find_elements(By.TAG_NAME, id_name_tag)
        for tag in tags: driver.execute_script('arguments[0].scrollIntoView(true);', tag)
        time.sleep(2)

        raw_name_id = BeautifulSoup(driver.page_source, 'html.parser').find_all(id_name_tag, class_=id_name_class)
        if raw_name_id: break
        time.sleep(3)

    return tuple((extract_name(i), extract_id(j)) for i, j in ((k.h4.text, k['id']) for k in raw_name_id))
