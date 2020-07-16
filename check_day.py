import pymysql.cursors
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='rtc',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
try:
    with connection.cursor() as cursor:
        # 查询7天内的新闻
        sql = 'select url from rtc_news_check where gmt_create < DATE_SUB(now(),INTERVAL 7 day);'
        cursor.execute(sql)
        data = []
        data = cursor.fetchall()
        # connection.commit()
        print(data)
except:
    connection.rollback()
connection.close()
