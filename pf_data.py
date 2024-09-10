"""
Version: 3.9.5
OS     : Windows 10 Pro
Name   : subject_id
Purpose: To get each subject's id (additionally make the black board logged in)
"""

from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import warnings
import datetime
import time
import re


def get_driver():
    warnings.filterwarnings('ignore')
    return webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))


def scroll_2_certain_point(by: str, criterion: str, driver) -> None:
    for tag in driver.find_elements(by, criterion):
        driver.execute_script('arguments[0].scrollIntoView(true);', tag)
    time.sleep(2)


def get_name_id_pairs(user_id: str, user_pw: str, driver) -> dict:
    bb_addr = 'https://kulms.korea.ac.kr/#'
    entry_login_xpath = '/html/body/div[1]/div/div/section/div/div/div/div[1]/div/div[2]/h3/strong/a'
    login_input_id_name = 'one_id'
    login_input_pw_name = 'user_password'
    login_btn_selector = '#loginFrm > div.form-button > div:nth-child(1) > button'
    bb_menu_bar_xpath = '//*[@id="main-content-inner"]/div/div[1]/section/button'
    bb_courses_xpath = '//*[@id="base_tools"]/bb-base-navigation-button[4]/div/li/a'
    id_name_tag = 'a'
    id_name_class = 'course-title ellipsis hide-focus-outline large-10 medium-10 small-12'
    bb_dropdown_semester_xpath = '//*[@id="courses-overview-filter-terms"]'
    bb_dropdown_select_current_xpath = '//*[@id="menu-"]/div[3]/ul/li[3]'

    def extract_id(origin: str) -> str: return origin[12:]

    def extract_name(origin: str) -> str:
        return re.sub(r'\([^)]*\)', '', origin[12 if '세종' in origin else 0:]).replace(')', '')

    while True:
        try:
            driver.implicitly_wait(5)
            driver.set_window_size(660, 800)
            driver.get(bb_addr)

            driver.find_element(By.XPATH, entry_login_xpath).click()
            driver.find_element(By.NAME, login_input_id_name).send_keys(user_id)
            driver.find_element(By.NAME, login_input_pw_name).send_keys(user_pw)
            driver.find_element(By.CSS_SELECTOR, login_btn_selector).send_keys(Keys.ENTER)

            break
        except (NoSuchWindowException, NoSuchElementException): time.sleep(3)

    time.sleep(4)

    while True:
        try:
            driver.find_element(By.XPATH, bb_menu_bar_xpath).click()
            time.sleep(0.5)

            driver.find_element(By.XPATH, bb_courses_xpath).click()

            break
        except StaleElementReferenceException: time.sleep(3)

    time.sleep(4)

    while True:
        driver.find_element(By.XPATH, bb_dropdown_semester_xpath).click()
        driver.find_element(By.XPATH, bb_dropdown_select_current_xpath).click()

        scroll_2_certain_point(By.TAG_NAME, id_name_tag, driver)

        if raw_name_id := BeautifulSoup(driver.page_source, 'html.parser').find_all(id_name_tag, class_=id_name_class):
            return {extract_name(i): extract_id(j) for i, j in ((k.h4.text, k['id']) for k in raw_name_id)}

        time.sleep(3)


def get_attendances_by_subjects(name_id: dict, driver) -> tuple:
    attendance_addr = 'https://kulms.korea.ac.kr/webapps/blackboard/content/launchLink.jsp?' \
                      'course_id={0}&tool_id=_5018_1&tool_type=TOOL&mode=view&mode=reset'

    def extract_title_time_pf(unrefined_pfs: tuple, result: tuple = ()) -> tuple:
        if not unrefined_pfs: return result

        title_tim_index = unrefined_pfs.index('컨텐츠명: ') + 1
        pf_index = unrefined_pfs.index('영상 출석 상태(P/F): ') + 1

        title, _, raw_time = (v if i != 2 else v.partition(' ~ ')
                              for i, v in enumerate(unrefined_pfs[title_tim_index].partition(' / ')))
        start_t, end_t = (datetime.datetime.strptime(i, '%Y-%m-%d %H:%M') for i in raw_time if i != ' ~ ')
        pf = unrefined_pfs[pf_index]

        return extract_title_time_pf(unrefined_pfs[pf_index + 1:], result + ((title, start_t, end_t, pf),))

    def pf_by_subjects_body(n_i: iter, result: tuple = ()) -> tuple:
        try: n, i = next(n_i)
        except StopIteration: return result

        driver.get(attendance_addr.format(i))
        time.sleep(1)

        try:
            scroll_2_certain_point(By.ID, 'listContainer_showAllButton', driver)
            driver.find_element(By.ID, 'listContainer_showAllButton').click()
        except NoSuchElementException:
            return pf_by_subjects_body(n_i, result)

        raw_pf_info = tuple(i.text for i in BeautifulSoup(driver.page_source, 'html.parser').select('td > span'))
        return pf_by_subjects_body(n_i, result + ((n,) + extract_title_time_pf(raw_pf_info),))

    return pf_by_subjects_body(iter(name_id.items()))
