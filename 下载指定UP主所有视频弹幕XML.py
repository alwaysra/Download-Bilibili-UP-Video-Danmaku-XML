import requests
import math
import os
from datetime import datetime

# 获取UP主名称的函数
def get_up_name(mid):
    """
    根据UP主的mid（用户ID）获取UP主的名称
    :param mid: UP主的用户ID
    :return: UP主的名称，如果获取失败则返回None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    # 尝试使用两种不同的API获取UP主信息，优先使用第二个
    urls = [
        f'https://api.bilibili.com/x/space/acc/info?mid={mid}',
        f'https://api.bilibili.com/x/web-interface/card?mid={mid}'
    ]
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            data = response.json()
            # 尝试从解析后的JSON数据中获取UP主名称，不同API获取的方式略有不同
            if 'data' in data and 'name' in data['data']:
                upname=data['data']['name']
                print(f'UP主名字:{upname}')
                return upname
            elif 'data' in data and 'card' in data['data'] and 'name' in data['data']['card']:
                upname=data['data']['card']['name']
                print(f'UP主名字:{upname}')
                return upname
        except requests.RequestException as e:
            print(f"请求UP主名称信息时出现错误: {e}")
        except ValueError as e:
            print(f"解析JSON获取UP主名称失败: {e}")
    return None

# 获取UP主视频列表信息的函数
def get_up_video_list(mid):
    """
    获取指定UP主的所有视频列表信息
    :param mid: UP主的用户ID
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={mid}&keywords=&ps=20&pn=1'
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            data = response.json()
            total = data['data']['page']['total']
            pages = math.ceil(total / 20)
            print(f'一共有 {total} 个视频')
            print(f'需要请求 {pages} 页')
            for page in range(1, pages + 1):
                get_up_video_lists(mid, page)
        else:
            print(f"获取视频总数时请求失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"请求视频列表信息时出现错误: {e}")
    except KeyError as e:
        print(f"解析视频列表JSON数据时缺少关键键值: {e}")

# 获取指定页面UP主视频详细信息的函数
def get_up_video_lists(mid, page):
    """
    获取指定页面的UP主视频详细信息，并将相关信息写入到以UP主名称命名的文本文件中
    :param mid: UP主的用户ID
    :param page: 要获取的页面序号
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={mid}&keywords=&ps=20&pn={page}'
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            data = response.json()
            archives = data['data']['archives']
            if upname:
                for archive in archives:
                    try:
                        title = archive['title']
                        ctime = archive['ctime']
                        bvid = archive['bvid']

                        # 转换ctime为yyyy-MM-dd格式
                        ctime_datetime = datetime.fromtimestamp(ctime)
                        ctime_str = ctime_datetime.strftime('%Y-%m-%d')

                        with open(f'{upname}.txt', 'a', encoding='utf-8') as f:
                            f.write(f'{ctime_str},{bvid},{title}\n')
                    except KeyError as e:
                        print(f"提取视频详细信息时缺少字段: {e}")
                        continue
            else:
                print("无法获取UP主名称，无法写入视频信息文件")
        else:
            print(f"获取第{page}页视频详细信息时请求失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"请求视频详细信息时出现错误: {e}")

# 获取视频弹幕的函数
def get_video_danmuku(line,current_line,total_lines):
    """
    获取视频弹幕并保存为XML文件，同时显示下载进度
    :param line: 包含视频信息的一行文本，格式为 "时间,bvid,标题"
    :param current_line: 当前处理的行数，用于显示进度
    :param total_lines: 总行数，用于显示进度
    """
    try:
        bv = line.split(',')[1]
        title = line.split(',')[2].replace('\n', '').replace('?', '').replace('/','')
        print(f'进度: {current_line}-{total_lines}   准备下载视频:{title}弹幕文件  ')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        url = f"https://api.bilibili.com/x/player/pagelist?bvid={bv}&jsonp=jsonp"
        req = requests.get(url, headers=headers)
        req.encoding = 'utf-8'
        data = req.json()
        # 假设cid在第一个分页中，获取cid
        if data['data']:
            cid = data['data'][0]['cid']
            url = f'https://comment.bilibili.com/{cid}.xml'
            req = requests.get(url, headers=headers)
            req.encoding = 'utf-8'
            if upname:
                xmlfile = os.path.join(upname, title + '.xml')
                with open(xmlfile, 'wb') as f:
                    f.write(req.content)
            else:
                print("无法获取UP主名称，无法保存弹幕文件")
        else:
            print(f"获取视频 {bv} 的分页信息失败")
    except requests.RequestException as e:
        print(f"请求弹幕相关信息时出现错误: {e}")
    except IndexError as e:
        print(f"解析视频分页信息时出现索引错误: {e}")
    except KeyError as e:
        print(f"解析弹幕相关JSON数据时缺少关键键值: {e}")

if __name__ == '__main__':
    url = input('输入UP主空间URL:')
    mid = url.replace('https://space.bilibili.com/', '')
    upname = get_up_name(mid)
    if upname:
        # 确保下载目录存在
        os.makedirs(f'{upname}', exist_ok=True)
        # 获取UP主视频列表信息并写入文件
        get_up_video_list(mid)
        # 如果对应的文本文件存在，则读取并获取每个视频的弹幕信息
        if os.path.exists(f'{upname}.txt'):
            with open(f'{upname}.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                total_lines = len(lines)
                for index, line in enumerate(lines, start=1):
                    get_video_danmuku(line, index, total_lines)
    else:
        print("无法获取UP主名称，程序无法继续执行")