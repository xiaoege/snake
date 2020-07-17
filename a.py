import pymysql.cursors

connection = pymysql.connect(host='192.168.1.125',
                            user='root',
                            password='root',
                            db='rtc',
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
try:
    with connection.cursor() as cursor:
        # 查询7天内的新闻
        sql = 'select url from rtc_news_check where gmt_create > DATE_SUB(now(),INTERVAL 7 day);'
        cursor.execute(sql)
        data = cursor.fetchall()
        url_list = []
        for k in data:
            url_list.append(k['url'])
        if 'http://www.chinadaily.com.cn/a/202007/14/WS5f0d0fe3a3108348172593e4.html' not in url_list:
            sql2 = 'insert into rtc_news_check(url) values(%s) '
            cursor.execute(sql2, (i))
            connection.commit()
except:
    connection.rollback()
