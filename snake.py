import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import uuid0
import os
import time
import random

# url = 'http://www.chinadaily.com.cn/a/202007/07/WS5f03dd80a310834817257acd.html'
# url = 'http://www.chinadaily.com.cn/a/202006/29/WS5ef9598fa310834817255c98.html'
url = 'http://www.chinadaily.com.cn/a/202007/08/WS5f03d442a310834817257a4c.html'

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}


def download_page():
    r = requests.get(url, headers=header)
    if r.status_code == 200:
        return r.text
    else:
        raise BaseException


def parse():
    text = download_page()
    soup = BeautifulSoup(text, 'html.parser')

    # print(soup.figcaption)

    # 标题
    title = soup.find(class_='lft_art')
    # if title == None:
    # title = soup.find(class_='ce_art')
    title = title.h1.string.strip()

    # 作者
    info_l = soup.find(class_='info_l')
    author = info_l.string.strip().replace('\n', '')
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
    figure_list_index = 0;
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
                figure_list_index += 1;
            else:
                content_list.append(i)

    # 新闻页数
    div_currpage = soup.find(id='div_currpage')
    if div_currpage != None:
        pages = div_currpage.find_all('a', class_=None)
        for i in pages:
            print(i['href'])

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='rtc',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        uuid = str(uuid0.generate())
        sql = "insert into rtc_news(uuid,author,title,content,source)values(%s,%s,%s,%s,%s)"
        cursor.execute(sql, (uuid, _author, str(title),
        str(content_list), 'Chinadaily'))
        # cursor.execute(sql,('uuid','_author','title','content','Chinadaily'))
        # result = cursor.fetchone()
        connection.commit()

    connection.close()


def mkdir():
    _path = '192.168.1.123:80/work/images/chinadaily/'
    _path = '/home/ftpuser/images'
    # _path = '/Users/chenhang/work/picture/chinadaily/'
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
    parse()
