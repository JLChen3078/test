import requests
import json
import csv
from datetime import datetime

API_URL = "https://data.sh.gov.cn/interface/13282/35857"
TOKEN = "34fdb67733895a510fc2a2c62ad7b2bd"
LIMIT = 1000  # 每次最多1000条

headers = {
    "Content-Type": "application/json",
    "token": TOKEN
}

all_data = []
offset = 0

print("开始拉取全部数据（offset/limit 翻页）...\n")

while True:
    payload = {
        "entities": [
            {
                "entity_type": 1,
                "entity_content": {
                    "file": {
                        "file_name": "接口调用说明_13282.docx",
                        "key": "tos-cn-i-ik7evvg4ik/8be25b6a1210465587d05ed0787ed84f.docx",
                        "size": 6516,
                        "file_type": 1,
                        "resource_id": None
                    }
                },
                "identifier": "2a7872c0-3872-11f1-91c9-c514450d30d5",
                "file_name_state": 1,
                "file_parse_state": 1
            }
        ],
        "text": "提取所有数据",
        "offset": offset,  # 偏移量（从第几条开始）
        "limit": LIMIT     # 本次取多少条
    }

    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("code") != "000000":
            print("失败:", result.get("message"))
            break

        data_inner = json.loads(result["data"])
        data_list = data_inner.get("data", [])
        total = data_inner.get("total", 0)

        if not data_list:
            break

        all_data.extend(data_list)
        print(f"offset={offset} → 已获取 {len(all_data)}/{total} 条")

        if len(all_data) >= total:
            break
        offset += LIMIT

    except Exception as e:
        print("异常:", e)
        break

if all_data:
    csv_file = f"上海数据_全量_{datetime.now():%Y%m%d%H%M%S}.csv"
    with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)
    print(f"\n✅ 完成：共 {len(all_data)} 条 → {csv_file}")
else:
    print("\n❌ 无数据")