import requests

def download_page(url):
    url = 'http://www.chinadaily.com.cn/a/202007/07/WS5f03dd80a310834817257acd.html'
    r = requests.get(url)
    return r.text

    

if __name__ == "__main__":
    download_page('a')
