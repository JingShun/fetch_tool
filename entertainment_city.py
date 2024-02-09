"""撈台灣娛樂城遊樂場資訊
"""

import requests
import csv
from bs4 import BeautifulSoup

# ##################
# 參數設定
# ##################

base_url = "https://台灣娛樂城.com/casino"
city_url = "/city/台南市"  # 若要篩選全部則空字串即可
page_url = "/page/{{page}}/"

limit_size = 100  # 抓幾間
csv_filename = "entertainment_city.csv"  # 輸出檔名


# ##################
# 主程式開始
# ##################

entry_list = []
page_total = 100  # 假定的最大頁碼，後續會動態更新
page = 1

while page <= page_total and len(entry_list) < limit_size:
    page_str = str(page)
    print("第 " + page_str + " 頁 ...", end="")
    url = base_url + city_url + page_url.replace("{{page}}", page_str)

    html = requests.get(url)
    soup = BeautifulSoup(html.content.decode("utf-8"), "html.parser")

    # 更新最大頁碼
    pagenav = soup.find("div", id="pagenav")
    pages = pagenav.find_all("a")
    page_total = int(pages[-2].get_text())

    # 取出內容
    item_list = soup.find_all("li", class_="info_box")
    print(" 發現 " + str(len(item_list)) + " 家!")

    for item in item_list:
        name = item.find("h3", class_="txt_clamp").get_text()
        map = item.find("p", class_="map").get_text()
        phone = item.find("p", class_="phone").get_text()
        entry_list.append(
            {
                "name": name,
                "map": map,
                "phone": phone,
            }
        )
        pass  # for item in item_list
    page = page + 1
    pass  # while end


print("共發現 " + str(len(entry_list)) + " 家")

# ##################
# 儲存
# ##################

if len(entry_list) == 0:
    print("未找到資料")
    exit

print("輸出檔案: " + csv_filename)

fields = list(entry_list[0].keys())
file = open(csv_filename, "w", newline="", encoding="utf-8")

# 寫入欄位名稱
writer = csv.DictWriter(file, fieldnames=fields)
writer.writeheader()

# 寫入檔案
for entry in entry_list:
    writer.writerow(entry)

file.close()
print("輸出完成")

