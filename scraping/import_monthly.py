from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lib.transform import convert_thai_month
from lib.setting import SETTINGS as setting
import pandas as pd
import os

def import_monthly(CHROMEDRIVER_PATH):
    hs_code = setting['hs_code']
    file_path = "/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/tmp"
    URL = 'https://tradereport.moc.go.th/th/stat/reporthscodeimport03'
    prefs = {"download.default_directory": file_path}
    options = Options()
    options.add_experimental_option("prefs", prefs)
    service = Service(CHROMEDRIVER_PATH)
    result_df = pd.DataFrame()

    for code in hs_code:
        hs_code = code
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(URL)
        sleep(3)
        wait = WebDriverWait(driver, 10)

        print('select search HS code')
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//text()[contains(.,' เลือกพิกัดศุลกากร')]]")
            )
        ).click()

        print('input HS code')
        popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.v-card.v-card--variant-elevated")
            )
        )

        # Find input inside popup
        input_box = WebDriverWait(popup, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.input-group input.form-control")
            )
        )
        input_box.clear()
        input_box.send_keys(hs_code)
        sleep(5)

        popup.find_element(
            By.CSS_SELECTOR,
            "#button-dialogHscode-search button.btn-primary"
        ).click()
        sleep(2)
        checkbox = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"input.row-checkbox[data-id='{hs_code}']")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", checkbox
        )
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

        print('select HS code')
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//text()[contains(.,' ยืนยันการเลือก')]]")
            )
        ).click()

        print('click show result')
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//text()[contains(.,'แสดงผลการค้นหา')]]")
            )
        ).click()
        sleep(3)

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//text()[contains(.,'CSV')]]")
            )
        ).click()
        sleep(5)

        df = pd.read_csv(file_path + '/Report.csv', skiprows=3, skipfooter=2, usecols= range(3))
        df.rename(columns={'เดือน': 'month', 'ปริมาณ': 'quantity','มูลค่า': 'value'}, inplace=True)
        df['month'] = df['month'].apply(lambda x: convert_thai_month(x))
        df['hs_code'] = hs_code

        delete_file = file_path + '/Report.csv'
        if os.path.exists(delete_file):
            os.remove(delete_file)
        driver.quit()

        result_df = pd.concat([result_df, df], ignore_index=True)

    result_df.to_csv("/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/csv/import_monthly.csv", index=False)
