from datetime import datetime
import pandas as pd

SETTINGS = {
    'CHROMEDRIVER_PATH': '/Users/samapatsrihan/work/scgp/scgp_ir/driver/chromedriver',
    'user': 'krittate@scg.com',
    'password':'@Khwan01',
    'hs_code': ["48191000","48192000"],
    
    'dev':{
        'container': 'data',
        'path': '/scraping/csv',
        'volume_path':'/Volumes/scgp_edl_dev_uat/dev_scgp_edl_landing/collect_trader',
        'host': 'https://adb-483305292468012.12.azuredatabricks.net/',
        'client_id':'b20d2673-fe84-4c10-89f7-f340d74225f4',
        'client_secret':'doseaab443f1c78c7fa6103c283f1d92fa48'
    },
}