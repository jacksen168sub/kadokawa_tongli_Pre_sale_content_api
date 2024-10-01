import requests
import json
import time
import os
from datetime import datetime
from tongli_api import get_tongli_all_book
from kadokawa_api import get_kadokawa_all_books, get_kadokawa_book_info


# 读取已订阅作品名称
def read_subscribed_titles(filename):
    print(f'正在读取已订阅作品名称从 {filename}...')
    with open(filename, 'r', encoding='utf-8') as f:
        titles = [line.strip() for line in f.readlines()]
    print(f'已订阅的作品名称: {titles}')
    return titles

# 读取已通知作品名称
def read_notified_titles(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r', encoding='utf-8') as f:
        return set(json.load(f))

# 写入已通知作品名称
def write_notified_titles(filename, notified_titles):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(notified_titles), f)

# 发送 webhook 通知
def send_webhook_notification(webhook_url, data):
    try:
        print(f'发送通知到 webhook: {webhook_url}，数据: {data}')
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print('Webhook 发送成功')
    except requests.exceptions.RequestException as e:
        print(f'Webhook 发送失败: {e}')

# 主函数
def main():
    # 发送webhook地址
    webhook_url = '你的Webhook地址'
    # 读取已订阅作品名称
    subscribed_titles = read_subscribed_titles('subscribed.txt')
    # 读取已通知作品名称
    notified_titles = read_notified_titles('notified_books.json')

    # 爬取东立新书信息
    print('开始爬取东立新书信息...')
    new_books_response = get_tongli_all_book()
    
    if not isinstance(new_books_response, dict) or 'books' not in new_books_response:
        print("API返回数据结构不正确")
        return

    new_books = new_books_response['books']
    print(f'共获取到 {len(new_books)} 本新书信息')
    
    date = new_books_response["date"]
    
    for book in new_books:
        if 'book_name' not in book or 'author' not in book:
            print(f"缺少字段的书籍数据: {book}")
            continue

        for title in subscribed_titles:
            if title in book['book_name']:
                if book['book_name'] not in notified_titles:
                    notification_data = {
                        'title': f"新书预售通知《{book['book_name']}》",
                        'message': f"《{book['book_name']}》预售通知:\n"
                                   f"📅 预计发售月份: {date}月\n"
                                   f"✍ 作者/原作: {book['author']}\n"
                                   f"🗃 类型: {book.get('genre', '未知')}\n"
                                   f"📏 开数: {book.get('format_size', '未知')}\n"
                                   f"📃 定页: {book.get('paper_number', '未知')}\n"
                                   f"📝 备注: {book.get('notes', '无')}\n"
                                   f"📔 出版社: 东立出版社"
                    }
                    send_webhook_notification(webhook_url, notification_data)
                    notified_titles.add(book['book_name'])
                    print(f'已发送通知: {book["book_name"]}给订阅者')
                    
                    time.sleep(5)  # 每次发送后暂停5秒
                else:
                    print(f'已通知过 {book["book_name"]}, 本次跳过')

    # 爬取 Kadokawa 新书信息
    print('开始爬取 Kadokawa 新书信息...')
    kadokawa_books_response = get_kadokawa_all_books()
    
    kadokawa_books = kadokawa_books_response
    
    for book in kadokawa_books:
        if 'name' not in book or 'link' not in book:
            print(f"缺少字段的书籍数据: {book}")
            continue

        for title in subscribed_titles:
            if title in book['name']:
                if book['name'] not in notified_titles:
                    # 获取详细书籍信息
                    book_info = get_kadokawa_book_info(book['link'])
                    
                    print(book_info)
                    
                    if book_info and isinstance(book_info, dict):
                        notification_data = {
                            'title': f"新书预售通知《{book_info['name']}》",
                            'message': f"《{book_info['name']}》预售通知:\n"
                                       f"📅 上市日期: {book_info['date']}\n"
                                       f"✍ 作者: {book_info['author']}\n"
                                       f"💰 价格(台币): {book_info['price_ntd']} $\n"
                                       f"💰 价格(人民币): {book_info['price_cny']} ￥\n"
                                       f"📔 出版社: 台湾角川"
                        }
                        send_webhook_notification(webhook_url, notification_data)
                        notified_titles.add(book_info['name'])
                        print(f'已发送通知: {book_info["name"]}给订阅者')
                        
                        time.sleep(5)  # 每次发送后暂停5秒
                else:
                    print(f'已通知过 {book["name"]}, 本次跳过')

    # 更新已通知作品名称
    write_notified_titles('notified_books.json', notified_titles)

if __name__ == "__main__":
    print("-" * 20 + "开始运行" + "-" * 20)
    main()
    print("-" * 20 + "运行结束" + "-" * 20)
