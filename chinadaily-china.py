import requests
from bs4 import BeautifulSoup
import pymysql.cursors
import uuid0
import os
import time
import datetime
import random

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

url = 'https://www.chinadaily.com.cn/china'

total_uuid = ''
total_author = ''
total_title = ''
total_source = ''
total_nav_str = ''
total_description = []
total_picture = []

# 获取一页里要下载的新闻url
def get_page_url():
    _url = url
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

    target_list =[]

    for i in result_list:
        year_start = i.find('a/') + 2
        day_start = i.index('/', year_start + 1)

        year = int(i[year_start:year_start+4])
        month = int(str(i[year_start+4:year_start+6]))
        day = int(
            str(i[i.find('/', year_start) + 1: i.find('/', i.find('/', year_start) + 1)]))

        timeNow = datetime.datetime.now()
        yestday = datetime.datetime(year, month, day)
        interval_days = (timeNow-yestday).days
        # 不抓取30天前的新闻
        if interval_days <= 30:
            target_list.append(i)

    for i in target_list:
        page_check(i)
        # 防止被ban
        time.sleep(30)


def download_page(_url):
    r = requests.get(_url, headers=header)
    if r.status_code == 200:
        return r.text
    else:
        return


def page_check(_url):
    print('url是:' + _url)

    # 多页新闻对应1个uuid
    uuid = str(uuid0.generate())

    text = download_page(_url)
    soup = BeautifulSoup(text, 'html.parser')

    # 暂不抓取视频新闻
    video = soup.find(id='playerFrame')
    if video != None:
        return

    # 一页还是多页
    page = soup.find(id='div_currpage')
    page_list = [_url]
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
    # 新闻预览
    insert_news()


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
    qqq = soup.find(class_='picshow')
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
        k = i.find('img')
        if k == None:
            continue
        img = k['src']
        img = 'http:' + img
        r = requests.get(img, headers=header, stream=True)
        if r.status_code == 200:
            file_path = mkdir() + '.jpeg'
            with open(file_path, 'wb') as f:
                f.write(r.content)

        if i.find('figcaption').string != None:
            figcaption = i.find('figcaption').string.strip().replace(
                '&nbsp;', ' ').replace('\"', '')
        else:
            figcaption = ''

        # _figure = "<figure><img src='%s'><figcaption>%s</figcaption></figure>" % (
            # file_path, figcaption)
        _figure = "<p><img src='%s'><figcaption>%s</figcaption></p>" % (
            file_path, figcaption)
        figure_list.append(_figure)
        total_picture.append(file_path)

    # 文字
    content_list = []
    description_list = []
    for i in contents:
        if i != '\n':
            if 'figure' in str(i) and 'class' in str(i):
                content_list.append(figure_list[figure_list_index].replace(
                    '&nbsp;', ' ').replace('\"', ''))
                figure_list_index += 1
            else:
                content_list.append(str(i).replace(
                    '&nbsp;', ' ').replace('\"', ''))
                total_description.append(str(i).replace(
                    '&nbsp;', ' ').replace('\"', ''))

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='rtc',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "insert into rtc_news_detail(news_id,author,title,content,source,country)values(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (uuid, _author, title,
                                  str(content_list), source, nav_str))
            connection.commit()
    except:
        connection.rollback()

    connection.close()

    global total_uuid
    total_uuid = uuid
    global total_author
    total_author = _author
    global total_title
    total_title = title
    global total_source
    total_source = source
    global total_nav_str
    total_nav_str = nav_str

def insert_news():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 db='rtc',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = 'INSERT INTO `rtc_news` (uuid,author,title,source,country,description,preview) values(%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql, (total_uuid, total_author, total_title, total_source,
                                 total_nav_str, total_description[0], total_picture[0]))
            connection.commit()
    except:
        connection.rollback()
    connection.close()


def mkdir():
    _path = '/work/images/chinadaily/'
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
    get_page_url()
