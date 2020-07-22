import re
from random import randint
import requests
from time import sleep
from multiprocessing import Pool
from bs4 import BeautifulSoup
import os

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
}
pattern = re.compile('.*?src="//fs.xicidaili.com/images/flag/cn.png"/></td>'
                     '.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?', re.S)

use_ip = []


def get_proxies(page):
    """
    爬取西刺代理，留下可用IP
    :param x: 页数
    :return:
    """
    sleep(randint(1, 3))
    print(page, 'page')
    url = 'https://www.xicidaili.com/wn/{}'.format(page)
    response = requests.get(url=url, headers=header)
    if response.status_code == 200:
        BS = BeautifulSoup(response.text, 'lxml')
        tr = BS.find_all('tr')
        result = []
        for x in tr:
            targets = re.findall(pattern=pattern, string=str(x))
            for target in targets:
                res = target[0] + ':' + target[1]
                new_verify_ip(res)
                with open('ip.txt', 'a') as f:
                    f.write(res + '//')
        # return (result)


def new_verify_ip(ip):
    """
    请求百度网页以验证IP
    :param ip:
    :return:
    """
    sleep(randint(1, 2))
    proxies = {'https': 'https://{}'.format(ip)}
    try:
        stateCode = requests.get(url='https://www.baidu.com/', headers=header, proxies=proxies, timeout=1)
        print(stateCode.status_code)
        print('ok: ' + ip)
        use_ip.append(ip)
        with open('verifyIp.txt', 'a') as f:
            f.write(ip + '//')
    except Exception as e:
        # print(e)
        pass


def read(x):
    with open('updateGetProxies.py', 'r', encoding='utf-8') as fi:
        with open('ss.py', 'w', encoding='utf-8')as fo:
            fo.write(fi.read())


if __name__ == '__main__':
    pool = Pool(os.cpu_count())
    pool.map(get_proxies, range(10))
