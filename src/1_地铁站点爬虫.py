import json
import random  # 修改此处，导入整个random模块
import requests
import sqlite3
from bs4 import BeautifulSoup
import threading
import time
from fake_useragent import UserAgent  # 导入用于获取随机用户代理的库

# 初始化线程锁，用于在线程操作数据库时防止数据竞争和冲突
lock = threading.Lock()
lock2 = threading.Lock()


def init_db():
    """初始化数据库并创建表"""
    conn = sqlite3.connect('../data/city_lines.db', check_same_thread=False)  # 连接数据库
    cur = conn.cursor()
    # 创建数据库表，若不存在则创建该表
    cur.execute('CREATE TABLE IF NOT EXISTS info(city TEXT, line TEXT, name TEXT)')
    conn.commit()  # 提交数据库事务
    return conn, cur


def close_db(conn):
    """关闭数据库连接"""
    conn.close()


def get_message(ID, cityname, name, cur, conn):
    """获取指定城市的地铁线路信息并存储到数据库"""
    url = f'http://map.amap.com/service/subway?_1555502190153&srhdata={ID}_drw_{cityname}.json'
    ua = UserAgent()  # 创建UserAgent实例
    session = requests.Session()  # 创建一个持久化的会话对象
    session.headers.update({'user-agent': ua.random})  # 设置随机的用户代理

    try:
        # 尝试进行请求，最多尝试三次
        for attempt in range(3):
            try:
                response = session.get(url, timeout=10)  # 发送GET请求
                response.raise_for_status()  # 检查响应状态，抛出HTTP错误
                break  # 如果请求成功，跳出循环
            except requests.RequestException:
                # 请求失败时处理异常并进行重试
                print(f"Error fetching {name}, retrying (Attempt {attempt + 1})...")
                time.sleep(1.5 ** attempt + random.uniform(0.5, 1.5))  # 这里调用random.uniform没问题
                continue
        else:
            # 如果三次请求都失败，打印失败信息并返回
            print(f"Failed to fetch data for {name} after multiple attempts.")
            return

        result = json.loads(response.text)  # 解析返回数据JSON格式
        for line in result.get('l', []):  # 遍历线路信息
            for station in line.get('st', []):  # 遍历每条线路的所有车站信息
                # 检查是否有地铁分线
                line_name = f"{line['ln']}({line['la']})" if line.get('la') else line['ln']
                city_info = (name, line_name, station['n'])
                print(*city_info)  # 打印获取的信息

                with lock2:
                    # 插入数据到数据库
                    cur.execute("INSERT INTO info(city, line, name) VALUES (?,?,?)", city_info)
                    conn.commit()  # 提交事务

                with open('../data/subway.csv', 'a+', encoding='utf-8') as f:
                    # 将信息写入CSV文件，以UTF-8编码保存
                    f.write(','.join(city_info) + '\n')

        time.sleep(random.uniform(0.5, 2))  # 这里调用random.uniform也没问题

    except Exception as e:
        print(f"Error processing {name}: {e}")


def get_city():
    """获取地铁图中可用城市的列表"""
    url = 'http://map.amap.com/subway/index.html?&1100'
    ua = UserAgent()  # 创建UserAgent实例
    session = requests.Session()  # 创建会话对象
    session.headers.update({'user-agent': ua.random})  # 设置随机的用户代理

    try:
        response = session.get(url)  # 发送请求获取城市列表页面
        response.raise_for_status()  # 检查请求是否成功

        html = response.content  # 获取页面内容
        soup = BeautifulSoup(html, 'lxml')  # 解析HTML内容

        # 提取城市列表
        city_lists = soup.find_all(class_="city-list fl")  # 热门城市
        more_city_lists = soup.find_all(class_="more-city-list")  # 其他城市
        return city_lists[0], more_city_lists[0]

    except Exception as e:
        print(f"Error fetching city list: {e}")
        return [], []  # 返回空列表表示未能获取到城市列表


def main():
    """主函数，用于获取所有城市的地铁数据"""
    conn, cur = init_db()  # 初始化数据库连接
    try:
        res1, res2 = get_city()  # 获取城市信息

        threads = []  # 用于存储线程

        for city_link in res1.find_all('a') + res2.find_all('a'):
            ID = city_link['id']  # 城市ID
            cityname = city_link['cityname']  # 城市名称拼音
            name = city_link.get_text()  # 城市中文名称

            thread = threading.Thread(target=get_message, args=(ID, cityname, name, cur, conn))
            threads.append(thread)
            thread.start()  # 启动线程

        for thread in threads:
            thread.join()  # 等待所有线程完成

    finally:
        close_db(conn)  # 确保关闭数据库连接


if __name__ == '__main__':
    main()  # 调用主函数开始执行
