# coding:utf-8
import requests, re, json, os
import csv
from bs4 import BeautifulSoup
# from newShortDiscuss import crawl_discuss
from time import sleep, time
from multiprocessing import Pool, cpu_count, Lock
from random import choices, randint

requestHeader = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',

}


def get_page_content(url, proxies=None):
    """
    获取页面内容
    :param url: 网页链接
    :param proxies: 代理
    :return:
    """
    sleep(randint(1, 9) * 0.1)
    response = requests.get(url=url, headers=requestHeader, proxies=proxies)
    # print(response.text)
    if response.status_code == 200:
        return response.text
    else:
        print(response.status_code)
        return None


def parse_html(html):
    """
    解析网页内容
    :param html: 网页内容
    :return:
    """
    delete = re.compile('&nbsp;', re.S)
    pattern = re.compile(
        '<li>.*?<em.*?class="">(.*?)</em>.*?href="(.*?)">.*?src="(.*?)"\sclass="">.*?</a>.*?"title">(.*?)</span>'
        '.*?class="">(.*?)<br>.*?(\d.*?)\n.*?</p>.*?"v:average">(.*?)</span>.*?<span>(.*?)</span>'
        '\n\s*?</div>(.*?)</div>.*?',
        re.S)

    target = re.sub(delete, '', html)
    items = re.findall(pattern, target)
    for item in items:
        print(item[0] + 'getInfo' + item[3])
        pattern = re.compile('.*?rel="v:starring">(.*?)</a>.*?', re.S)
        actorPage = get_page_content(item[1])
        bs = BeautifulSoup(actorPage, 'lxml')
        allList = bs.find_all(class_='attrs')

        try:
            for writer in allList[1].find_all('a'):
                writers += writer.text + '/'
        except:
            writers = ''

        try:
            collection = re.findall(pattern, str(allList[2]))
            for one in collection:
                actors += one + '/'
        except:
            actors = ''
        quote = '暂无收录'
        if len(item[8]) == 22:
            quote = '暂无收录'
        else:
            try:
                quote = re.findall('.*?class="inq">(.*?)</span>', item[8])[0]
            except:
                pass
        # yield {
        #     'index(排名)': item[0],
        #     'title(电影名)': item[3],
        #     'detailLink(详情链接)': item[1],
        #     'image(海报)': item[2],
        #     'director(导演)': item[4].strip().split(':', 1)[1].split(':', 1)[0][0:-2],
        #     'time&type(上映时间&类型)': item[5],
        #     'score(评分)': item[6],
        #     'numberOfPeople(评分人数)': item[7][0:-3],
        #     'quote(经典语录)': quote
        # }
        yield (
            item[0],  # 排名
            item[3],  # 电影名
            item[1],  # 详情链接
            item[2],  # 海报
            item[4].strip().split(':', 1)[1].split(':', 1)[0][0:-2],  # 导演
            writers,  # 编剧
            actors,  # 主演
            item[5],  # 上映时间&类型
            item[6],  # 评分
            item[7][0:-3],  # 评分人数
            quote  # 经典语录
        )


def save_list(content):
    """
    保存解析后的内容
    :param content: 解析后的内容
    :return:
    """
    with open('./rankList.txt', 'a', encoding='utf-8') as f:
        f.write(str(content) + '\n\n')


def save_csv(contents):
    """
    保存解析后的内容
    :param contents:
    :return:
    """
    with open('./newRankList.csv', 'a', encoding='utf-8') as f:
        # header = ['排名', '电影名', '详情链接', '海报', '导演', '编剧', '主演', '上映时间&类型', '评分', '评分人数', '经典语录']
        writer = csv.writer(f)
        # writer.writerow(header)
        for content in contents:
            writer.writerow(content)
        print('write over')


def remove_file(filename):
    print('当前路径: {}'.format(str(os.getcwd())))
    try:
        os.remove('./{}'.format(filename))
    except:
        pass


def write_table_header():
    """
    写表头
    :return:
    """
    with open('./rankList.csv', 'w', encoding='utf-8') as f:
        tableHeader = ['\ufeff排名', '电影名', '详情链接', '海报', '导演', '编剧', '主演', '上映时间&类型', '评分', '评分人数',
                       '经典语录']  # 添加 \ufeff 将表格内容转换为  UTF-8 with BOM  格式，防止中文乱码问题
        writer = csv.writer(f)
        writer.writerow(tableHeader)


def main(i):
    url = 'https://movie.douban.com/top250?start={}&filter='.format(i * 25)
    items = parse_html(get_page_content(url=url, proxies={'https': 'https://110.52.235.229:9999'}))
    save_csv(items)


if __name__ == '__main__':
    lock = Lock()
    pool = Pool(cpu_count())
    remove_file('newRankList.csv')
    write_table_header()
    pool.map(main, range(10))
    lock.acquire()
    lock.release()
