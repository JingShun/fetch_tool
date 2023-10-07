""" 依照姓名去撈司法判決書
"""
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from openpyxl import Workbook

# ##################
# 參數設定
# ##################
names = [
    "王大明",
    "李小花",
]

sleep_sec = 10

CHROMEDRIVER_PATH = "./chromedriver/chromedriver-win64/chromedriver.exe"
CHROME_PATH = "./chromedriver/chrome-win64/chrome.exe"
# ##################


_driver = None
totalbook = Workbook()

# ##################
# func
# ##################
def init_driver():
    """初始化WebDriver

    Returns:
        _type_: _description_
    """
    global _driver,CHROMEDRIVER_PATH,CHROME_PATH

    if not _driver is None:
        return _driver

    # Chrome Options
    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_PATH
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)  # 離開時先不要關閉視窗
    options.add_argument("--disable-notifications")  # 降低彈出視窗的影響

    # Chrome Service
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)

    # WebDriver
    _driver = webdriver.Chrome(service=service, options=options)

    return _driver

def query_judgmen_list(name):
    """查詢並取得清單以及詳細內文的連結

    Args:
        driver (WebDriver): _description_
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    global _driver,sleep_sec

    if not name or _driver is None:
        return []

    # 查詢頁面
    _driver.get("https://judgment.judicial.gov.tw/FJUD/Default_AD.aspx")

    # 設定查詢來源
    select = Select(_driver.find_element(By.ID, "jud_court"))
    for index, option in enumerate(select.options):
        if option.text in [
            "最高法院",
            "臺灣高等法院",
            "臺灣高等法院 臺南分院",
            "臺灣臺南地方法院",
        ]:
            select.select_by_index(index)
        else:
            select.deselect_by_index(index)

    # 裁判主文
    input_subject = _driver.find_element(By.ID, "jud_jmain")
    input_subject.clear()
    input_subject.send_keys(name)

    # 送出查詢
    _driver.find_element(By.ID, "btnQry").click()

    # 等待
    time.sleep(sleep_sec)
    iframe = _driver.find_element(By.TAG_NAME, "iframe")
    _driver.switch_to.frame(iframe)

    # 撈出指定表格的所有儲存格
    td_list = _driver.find_elements(By.ID, "jud")

    if len(td_list) == 0:
        # 查無資料
        return []
    else:
        td_list = td_list[0].find_elements(By.TAG_NAME, "td")

    # 分割儲存格 序號, 裁判字號（內容大小）, 裁判日期, 裁判案由, 摘要
    n = 5
    rows = [td_list[i : i + n] for i in range(0, len(td_list), n)]

    # 解析儲存格內容，並新增新欄位詳細資訊連結
    for idx, row in enumerate(rows):
        for col_idx, col in enumerate(row):
            # 不用解析就跳過
            if not isinstance(col, webdriver.remote.webelement.WebElement):
                continue

            text = col.text
            a = col.find_elements(By.TAG_NAME, "a")
            if len(a):
                url = a[0].get_attribute("href")

                rows[idx].append(url)
            rows[idx][col_idx] = text.rstrip()

    # 取得詳細內文
    for idx, row in enumerate(rows):
        detail_content = ""

        # 進入詳細資料頁面
        _driver.get(row[5])

        # 切換到去除格式引用頁面
        url = row[5]
        url = url.replace("/FJUD/data.aspx", "/EXPORTFILE/reformat.aspx")
        url = url.replace("?ty=", "?type=")
        url = url.replace("&ot=in", "&lawpara=&ispdf=0")
        _driver.get(url)

        # 擷取部分內文並格式化
        html = _driver.find_elements(By.ID, "spanCon")
        if len(html) > 0:
            html = html[0].get_attribute("innerHTML")
            gfg = BeautifulSoup(html, "html.parser") # 為了可以prettify
            detail_content = gfg.prettify().rstrip()
            pattern = r"<.*?>"
            detail_content = re.sub(pattern, "", detail_content).rstrip()

        rows[idx].append(detail_content)

    return rows

def save(name, data):
    """儲存到excel中

    Args:
        name (str): _description_
        data (list): _description_
    """
    global totalbook
    
    # 除存到total
    sheet = totalbook.active
    for row in data:
        row = [name] + row
        sheet.append(row)

    # 各別也另存一份
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["序號", "裁判字號(內容大小)", "裁判日期", "裁判案由", "摘要", "連結", "內文"])
    for row in data:
        sheet.append(row)
    workbook.save("output/" + name + ".xlsx")

# ##################
# start
# ##################
_driver = init_driver()

# excel項目
sheet = totalbook.active
sheet.append(["姓名", "序號", "裁判字號(內容大小)", "裁判日期", "裁判案由", "摘要", "連結", "內文"])

for name in names:
    print(name)

    data = query_judgmen_list(name)
    print(name + ": 找到 " + str(len(data)) + "筆")

    save(name, data)

# 儲存
totalbook.save("output/total.xlsx")
