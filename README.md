# 依照姓名去撈司法判決書

可協助去司法院的裁判書系統抓指定姓名的與法院的判決書內文

[司法院的裁判書系統](https://judgment.judicial.gov.tw/FJUD/Default.aspx)

# 操作方式

1. 下載chromedriver、chrome並解壓縮
chromedriver、chrome可從以下連結進行下載: https://googlechromelabs.github.io/chrome-for-testing/

2. 編輯py中的參數設定

|參數|說明|
|---|---|
|names|要查詢的姓名，逗號區隔|
|sleep_sec|每次查詢間隔幾秒|
|CHROMEDRIVER_PATH|chromedriver.exe路徑|
|CHROME_PATH|chrome.exe路徑|

3. 執行以下語法
```python
python3 download_judgment_book.py
```

# 輸出

1. output/total.xlsx : 本次查詢的所有結果
2. output/<姓名>.xlsx : 個別查詢結果
