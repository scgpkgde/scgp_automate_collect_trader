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
import re

def principal_export_country(CHROMEDRIVER_PATH):
    tmp_date = datetime.now().date() - relativedelta(months=2)
    input_month = tmp_date.strftime("%m")
    input_year = tmp_date.strftime("%Y")
    file_path = "/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/tmp"
    URL = 'https://tradereport.moc.go.th/th/stat/reportcomcodeexport04'

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
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH,"//span[text()='ม.ค.']/ancestor::div[@role='combobox']")
        )
    ).click()

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
    input_box.send_keys("20")

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
    driver.quit()
    df = pd.read_csv(
                    file_path+'/Report.csv',
                    skiprows = 4,
                    skipfooter= 6,
                    header = None,
                    names=['country','value_0','value_1','value_2','value_3','expansion_rate_0','expansion_rate_1','expansion_rate_2','expansion_rate_3','proportion_0','proportion_1','proportion_2','proportion_3']
                )
    df = pd.read_csv(
                    file_path+'/Report.csv',
                    skiprows = 4,
                    skipfooter= 6,
                    header = None,
                    names=['country','value_0','value_1','value_2','value_3','expansion_rate_0','expansion_rate_1','expansion_rate_2','expansion_rate_3','proportion_0','proportion_1','proportion_2','proportion_3']
                )
    
    # -------------------------
    # 1) Melt VALUE columns
    # -------------------------
    df_value = df.melt(
        id_vars=["country"],
        value_vars=["value_0", "value_1", "value_2", "value_3"],
        var_name="idx",
        value_name="value"
    )

    # -------------------------
    # 2) Melt EXPANSION RATE
    # -------------------------
    df_exp = df.melt(
        id_vars=["country"],
        value_vars=[
            "expansion_rate_0",
            "expansion_rate_1",
            "expansion_rate_2",
            "expansion_rate_3"
        ],
        var_name="idx",
        value_name="expansion_rate"
    )

    # -------------------------
    # 3) Melt PROPORTION
    # -------------------------
    df_prop = df.melt(
        id_vars=["country"],
        value_vars=[
            "proportion_0",
            "proportion_1",
            "proportion_2",
            "proportion_3"
        ],
        var_name="idx",
        value_name="proportion"
    )

    # -------------------------
    # 4) Extract month index
    # -------------------------
    for d in (df_value, df_exp, df_prop):
        d["month_idx"] = (
            d["idx"]
            .str.extract(r"(\d+)")
            .astype(int)
        )

    # -------------------------
    # 5) Merge all metrics
    # -------------------------
    df_long = (
        df_value
        .merge(
            df_exp[["country", "month_idx", "expansion_rate"]],
            on=["country", "month_idx"]
        )
        .merge(
            df_prop[["country", "month_idx", "proportion"]],
            on=["country", "month_idx"]
        )
    )

    # -------------------------
    # 6) AUTO-detect start month/year from DataFrame VALUES
    # -------------------------
    thai_month_map = {
        "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4,
        "พ.ค.": 5, "มิ.ย.": 6, "ก.ค.": 7, "ส.ค.": 8,
        "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12
    }

    pattern = re.compile(
        r"(ม.ค.|ก.พ.|มี.ค.|เม.ย.|พ.ค.|มิ.ย.|ก.ค.|ส.ค.|ก.ย.|ต.ค.|พ.ย.|ธ.ค.)\s*(\d{4})"
    )

    start_month = None

    for col in df.columns:
        for val in df[col].astype(str):
            m = pattern.search(val)
            if m:
                month_th, year_th = m.groups()
                start_month = pd.Timestamp(
                    year=int(year_th) - 543,
                    month=thai_month_map[month_th],
                    day=1
                )
                break
        if start_month is not None:
            break

    if start_month is None:
        raise ValueError("Cannot detect start month/year from DataFrame")

    # -------------------------
    # 7) Create month & year
    # -------------------------
    df_long["month_dt"] = df_long["month_idx"].apply(
        lambda x: start_month + pd.DateOffset(months=x)
    )
    df_long["year"] = df_long["month_dt"].dt.year + 543

    df_long["month"] = df_long["month_dt"].dt.month

    # -------------------------
    # 8) Final selection
    # -------------------------
    df_long = (
        df_long[[
            "country",
            "value",
            "expansion_rate",
            "proportion",
            "month",
            "year"
        ]]
        .reset_index(drop=True)
    )
    df_long = df_long[df_long["country"] != "ประเทศ"].reset_index(drop=True)

    df_long.to_csv("/Users/samapatsrihan/work/scgp/scgp_automate_collect_trader/scraping/csv/principal_export_country.csv", index=False)

    delete_file = file_path + '/Report.csv'
    if os.path.exists(delete_file):
        os.remove(delete_file)


