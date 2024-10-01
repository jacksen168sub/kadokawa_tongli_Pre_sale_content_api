import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_kadokawa_all_books(limit=100):
    now = datetime.now()
    year = now.year
    month = now.month
    all_books = []
    page = 1

    while True:
        url = f"https://www.kadokawa.com.tw/categories/{year}-{month:02d}?page={page}&limit={limit}"
        print(f"开始爬取第{page}页内容...")
        response = requests.get(url)

        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.content, 'html.parser')

            products = soup.select('div.ProductList-list product-item')

            if not products:
                break  # 如果没有书籍则结束爬取

            for product in products:
                link = product.find('a')['href'] if product.find('a') else '无链接'
                title = product.select_one('a div:nth-of-type(2) div div:nth-of-type(1)').get_text(strip=True) if product.select_one('a div:nth-of-type(2) div div:nth-of-type(1)') else '无标题'
                
                all_books.append({
                    'name': title,
                    'link': link
                })

            # 获取分页信息
            paginator = soup.select_one('ul.ProductList-paginator.pagination')
            if paginator:
                page_links = paginator.select('li a')
                total_pages = max(int(link.get_text(strip=True)) for link in page_links if link.get_text(strip=True).isdigit())
                print(f"共{total_pages}页内容")
                if page >= total_pages:
                    break  # 如果当前页已到达最后一页则结束爬取
            else:
                break  # 如果没有分页信息则结束爬取

            page += 1  # 继续爬取下一页
        else:
            print("请求失败，状态码:", response.status_code)
            break

    return all_books

def get_kadokawa_book_info(book_url):
    response = requests.get(book_url)

    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.select_one('div.box-default h1').get_text(strip=True) if soup.select_one('div.box-default h1') else '无标题'

        # 提取作者和上市日期
        author, release_date = '无作者', '无上市日期'
        summary = soup.find_all('p', class_='Product-summary Product-summary-block')
        
        for p in summary:
            if '作者資訊：' in p.text and '上市日期：' in p.text:
                details = p.decode_contents().split('<br/>')
                for detail in details:
                    detail = detail.strip()
                    if '作者資訊：' in detail:
                        author = detail.replace('作者資訊：', '').strip()
                    elif '上市日期：' in detail:
                        release_date = detail.replace('上市日期：', '').strip()
                break

        # 提取价格
        price_info = soup.select_one('div.global-primary.dark-primary.price-regular.price.js-price')
        price_ntd = price_info.get_text(strip=True).replace('NT$', '').strip() if price_info else '无价格'
        
        # 转换为人民币（假设汇率为 0.22）
        price_cny = float(price_ntd) * 0.22 if price_ntd.isdigit() else '无价格'

        return {
            'name': title,
            'author': author,
            'date': release_date,
            'price_ntd': price_ntd,
            'price_cny': round(price_cny, 2) if isinstance(price_cny, float) else price_cny
        }
    else:
        print("请求失败，状态码:", response.status_code)
        return {}

if __name__ == "__main__":
    all_books = get_kadokawa_all_books()
    print(f"获取到 {len(all_books)} 本书。")
    print(all_books)

    # 示例：获取单本书信息
    if all_books:
        book_info = get_kadokawa_book_info(all_books[22]['link'])
        print(book_info)
