import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import uuid0
import os
import time
import random

# url = 'http://www.chinadaily.com.cn/a/202007/07/WS5f03dd80a310834817257acd.html'
# url = 'http://www.chinadaily.com.cn/a/202006/29/WS5ef9598fa310834817255c98.html'
# url = 'http://www.chinadaily.com.cn/a/202007/08/WS5f03d442a310834817257a4c.html'
url = 'http://www.chinadaily.com.cn/a/202007/09/WS5f0679c0a310834817258428.html'
# url = 'https://www.chinadaily.com.cn/a/202007/08/WS5f05d461a31083481725827c.html'
url = 'http://www.chinadaily.com.cn/a/202007/09/WS5f06b249a310834817258577.html'
url = 'http://www.chinadaily.com.cn/a/202007/10/WS5f07a29ca3108348172586f0.html'

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}


# 获取一页里要下载的新闻url
def get_page_url():
    _url = 'https://www.chinadaily.com.cn/china'
    r = requests.get(_url, headers=header)
    text = r.text
    soup = BeautifulSoup(text, 'html.parser')
    a = soup.find_all('a')
    url_list = []
    for i in a:
        if 'www.chinadaily.com.cn/a' in str(i):
            url_list.append('http:' + i['href'])
    result_list = list(set(url_list))
    result_list.sort(key=url_list.index)
    for i in result_list:
        download_page(i)
        # 防止被ban
        time.sleep(30)


def download_page(_url=url):
    r = requests.get(_url, headers=header)
    if r.status_code == 200:
        return r.text
    else:
        return


def page_check():
    # 多页新闻对应1个uuid
    uuid = str(uuid0.generate())

    text = download_page()
    soup = BeautifulSoup(text, 'html.parser')

    # 暂不抓取视频新闻
    video = soup.find(id='playerFrame')
    if video != None:
        return

    # 一页还是多页
    page = soup.find(id='div_currpage')
    page_list = [url]
    if page == None:
        parse(soup, uuid)
    else:
        a = page.find_all('a')
        for i in a:
            href = 'http:' + i['href']
            page_list.append(href)
        url_list = list(set(page_list))
        url_list.sort(key=page_list.index)
        for i in url_list:
            t = download_page(i)
            s = BeautifulSoup(t, 'html.parser')
            parse(s, uuid)


def parse(soup, uuid):
    source = 'Chinadaily'

    # 栏目
    nav = soup.find(id='bread-nav')
    nav_str = ''
    if nav != None:
        a = nav.find_all('a')
        nav_str += a[1].string.strip().replace('/ ', '') + \
            a[2].string.strip().replace('/ ', '/')

    # 标题
    title = ''
    author = ''
    info_l = soup.find(class_='info_l')
    # 判断是否是图片新闻
    if soup.find(class_='picshow') == None:
        title = soup.find(id='lft-art').h1.string.strip().replace('\n', '')
        author = info_l.string.strip().replace('\n', '')
    else:
        title = soup.find(class_='ce_art').h1.string.strip().replace('\n', '')
        author = info_l.contents[0].string.strip().replace('\n', '')

    # 作者
    authorArray = author.split('|')
    _author = ''
    for j in authorArray[:len(authorArray)-1]:
        _author += j.strip() + ' | '
    _author = _author[:_author.find(' | ', -1)-2]

    # 新闻内容
    content = soup.find(id='Content')
    contents = content.contents
    figures = content.find_all('figure')

    # 图片
    figure_list = []
    figure_list_index = 0
    for i in figures:
        img = i.find('img')['src']
        img = 'http:' + img
        r = requests.get(img, headers=header, stream=True)
        if r.status_code == 200:
            file_path = mkdir() + '.jpeg'
            with open(file_path, 'wb') as f:
                f.write(r.content)

        figcaption = i.find('figcaption').string.strip()

        _figure = "<figure><img src='%s'><figcaption>%s</figcaption></figure>" % (
            file_path, figcaption)
        figure_list.append(_figure)

    # 文字
    content_list = []
    for i in contents:
        if i != '\n':
            if 'figure' in str(i):
                content_list.append(figure_list[figure_list_index])
                figure_list_index += 1
            else:
                content_list.append(i)

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='rtc',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # uuid = str(uuid0.generate())
            sql = "insert into rtc_news(uuid,author,title,content,source,country)values(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (uuid, _author, title,
                                 str(content_list), source, nav_str))
            # cursor.execute(sql,('uuid','_author','title','content','Chinadaily'))
            # result = cursor.fetchone()
            connection.commit()
    except:
        connection.rollback()

    connection.close()


def mkdir():
    _path = '192.168.1.123:80/work/images/chinadaily/'
    # _path = '/home/ftpuser/images'
    _path = '/Users/chenhang/work/picture/chinadaily/'
    _month = str(time.strftime("%Y-%m", time.localtime())) + '/'
    _day = str(time.strftime("%d", time.localtime())) + '/'
    if os.path.exists(_path + _month + _day):
        pass
    else:
        os.makedirs(_path + _month + _day)
    _timestamp = time.mktime(time.strptime(time.strftime(
        "%a %b %d %H:%M:%S %Y", time.localtime()), "%a %b %d %H:%M:%S %Y"))
    file_name = str(_timestamp)[:-2] + '-' + str(random.randint(0, 10000))
    # 不带.jpg /.png之类
    return _path + _month + _day + file_name


if __name__ == "__main__":
    page_check()
    # get_page_url()
