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
from lib.transform import convert_to_thai_month
import pandas as pd
import os


def principal_import(CHROMEDRIVER_PATH):
    
    tmp_date = datetime.now().date() - relativedelta(months=2)
    input_month = tmp_date.strftime("%m")
    input_year = tmp_date.strftime("%Y")

    file_path = "/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/tmp"
    URL = 'https://tradereport.moc.go.th/th/stat/reportcomcodeimport03'

    prefs = {"download.default_directory": file_path}
    options = Options()
    options.add_experimental_option("prefs", prefs)
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    sleep(3)
    wait = WebDriverWait(driver, 10)

    print('select frequency')
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,"//span[text()='ปี']/ancestor::div[@role='combobox']")
        )
    ).click()

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//li[@role='option']//span[text()='เดือน']")
        )
    ).click()
    sleep(3)

    print('select month')
    month_boxes = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//input[@placeholder='เลือกเดือน']/ancestor::div[@role='combobox']")
        )
    )
    for box in month_boxes:
        box.click()
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//ul[@role='listbox']"))
        )

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li[@role='option']//span[text()='{convert_to_thai_month(input_month)}']")
            )
        ).click()
        sleep(1)

    print('select currency')
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,"//span[text()='ล้านบาท']/ancestor::div[@role='combobox']")
        )
    ).click()

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//li[@role='option']//span[text()='บาท']")
        )
    ).click()

    print('select show amount')

    input_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='number']"))
    )

    input_box.click()
    input_box.send_keys(Keys.COMMAND + "a")
    input_box.send_keys(Keys.BACKSPACE)
    input_box.send_keys("300")

    print('click show result')
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//text()[contains(.,'แสดงผลการค้นหา')]]")
        )
    ).click()
    sleep(2)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//text()[contains(.,'CSV')]]")
        )
    ).click()
    sleep(5)
    driver.quit()
    df = pd.read_csv(
                        file_path+'/Report.csv',
                        skiprows = 5,
                        skipfooter= 6,
                        header = None, names=['product','value','expansion_rate','proportion']
                    )
    df.to_csv("/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/csv/principal_import.csv", index=False)

    delete_file = file_path + '/Report.csv'
    if os.path.exists(delete_file):
        os.remove(delete_file)

