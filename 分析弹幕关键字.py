import os
import xml.etree.ElementTree as ET
import pandas as pd

# 定义关键字
keywords = ["忠诚", "忠诚!", "忠!诚!"]

# 读取文本文件中的信息
with open('小约翰可汗.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个空的DataFrame
df = pd.DataFrame(columns=['日期', 'BV号', '标题', '忠诚', '忠诚!', '忠!诚!'])

# 遍历每一行，解析XML文件
for line in lines:
    date, bv, title = line.strip().split(',')
    newtitle=title.replace('/','').replace('|','').replace('?','')
    xml_filename = newtitle + '.xml'
    xml_path = os.path.join('小约翰可汗', xml_filename)

    # 读取XML文件并解析
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 初始化关键字计数
    counts = {keyword: 0 for keyword in keywords}

    # 遍历弹幕元素
    for d in root.findall('d'):
        text = d.text # 获取弹幕文本
        for keyword in keywords:
            counts[keyword] += text.count(keyword)

    # 将结果添加到DataFrame
    new_row = pd.DataFrame({
        '日期': [date],
        'BV号': [bv],
        '标题': [title],
        '忠诚': [counts['忠诚']],
        '忠诚!': [counts['忠诚!']],
        '忠!诚!': [counts['忠!诚!']]
    })
    df = pd.concat([df, new_row], ignore_index=True)

# 将结果写入Excel文件
df.to_excel('小约翰可汗.xlsx', index=False)