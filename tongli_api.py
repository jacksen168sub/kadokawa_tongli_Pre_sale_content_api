import requests
import time
from bs4 import BeautifulSoup

# 爬取页面并解析
def fetch_page_data(page_number):
    url = f'https://www.tongli.com.tw/Search1.aspx?Page={page_number}'
    try:
        response = requests.get(url, timeout=10)  # 设置超时
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('table.Form_sb tr')[1:]  # 跳过表头
            books = []
            for row in rows:
                cols = row.find_all('td')
                book_name = cols[0].get_text(strip=True)
                author = cols[1].get_text(strip=True)
                genre = cols[2].get_text(strip=True)
                format_size = cols[3].get_text(strip=True)
                paper_number = cols[4].get_text(strip=True)
                notes = cols[5].get_text(strip=True) if len(cols) > 5 else ''
                
                books.append({
                    'book_name': book_name,
                    'author': author,
                    'genre': genre,
                    'format_size': format_size,
                    'paper_number': paper_number,
                    'notes': notes
                })
            return books
        else:
            print(f'Failed to fetch page {page_number}, status code: {response.status_code}')
            return []
    except requests.RequestException as e:
        print(f'Error fetching page {page_number}: {e}')
        return []

# 获取总页数
def get_total_pages():
    url = 'https://www.tongli.com.tw/Search1.aspx?Page=1'
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            total_pages = soup.select('div.nav_links ul li a')
            date = soup.select_one('h5 span').get_text(strip=True) if soup.select_one('h5 span') else ''
            
            if total_pages:
                last_page_url = total_pages[-1]['href']
                last_page_num = last_page_url.split('=')[-1]
                print(f"总页数为: {last_page_num}")
                print(f"预计发布日期: {date}")
                return int(last_page_num), date
            else:
                return 1, ""
    except requests.RequestException as e:
        print(f'Error fetching total pages: {e}')
        return 1, ""

# 主函数，爬取所有页面
def get_tongli_all_book():
    total_pages, date = get_total_pages()
    all_data = {"date": date, "books": []}
    
    for page in range(1, total_pages + 1):
        time.sleep(3)
        print(f'正在爬取第 {page} 页...')
        page_data = fetch_page_data(page)
        if page_data:
            all_data["books"].extend(page_data)
            print(f"{page}页爬取成功")
    
    return all_data

if __name__ == "__main__":
    print(get_tongli_all_book())
