import requests
from bs4 import BeautifulSoup

# url = 'http://www.chinadaily.com.cn/a/202007/07/WS5f03dd80a310834817257acd.html'
url = 'http://www.chinadaily.com.cn/a/202006/29/WS5ef9598fa310834817255c98.html'


def download_page():
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    r = requests.get(url, headers=header)
    return r.text


def parse():
    text = download_page()
    soup = BeautifulSoup(text, 'html.parser')

    # print(soup.figcaption)

    # 标题
    title = soup.find(class_='lft_art')
    # if title == None:
        # title = soup.find(class_='ce_art')
    title1 = title.h1.string

    # 作者
    info_l = soup.find(class_='info_l')
    author = info_l.string.strip().replace('\n','')
    authorArray = author.split('|')
    for j in authorArray:
        j = j.strip()

    # 新闻内容
    content = soup.find(id='Content')
    for i in content:
        print(i)

    # 新闻页数
    div_currpage = soup.find(id='div_currpage')
    if div_currpage != None:
        pages = div_currpage.find_all('a', class_=None)
        for i in pages:
            print(type(i))
            print(i['href'])

    print('aaa')


if __name__ == "__main__":
    parse()
