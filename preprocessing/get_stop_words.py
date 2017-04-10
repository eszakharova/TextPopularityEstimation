from lxml import html
import requests


def get_stop_words():
    f = open('stop_words.txt', 'w')
    links = ['http://dict.ruslang.ru/freq.php?act=show&dic=freq_pro&title=%D7%E0%F1%F2%EE%F2%ED%FB%E9%20%F1%EF%E8%F1%EE%EA%20%EC%E5%F1%F2%EE%E8%EC%E5%ED%E8%E9%20(%EC%E5%F1%F2%EE%E8%EC%E5%ED%E8%FF-%F1%F3%F9%E5%F1%F2%E2%E8%F2%E5%EB%FC%ED%FB%E5,%20%EF%F0%E8%EB%E0%E3%E0%F2%E5%EB%FC%ED%FB%E5,%20%ED%E0%F0%E5%F7%E8%FF,%20%EF%F0%E5%E4%E8%EA%E0%F2%E8%E2%FB)',
             'http://dict.ruslang.ru/freq.php?act=show&dic=freq_other&title=%D7%E0%F1%F2%EE%F2%ED%FB%E9%20%F1%EF%E8%F1%EE%EA%20%EB%E5%EC%EC%20%F1%EB%F3%E6%E5%E1%ED%FB%F5%20%F7%E0%F1%F2%E5%E9%20%F0%E5%F7%E8']
    for link in links:
        page = requests.get(link)
        tree = html.fromstring(page.content)
        stop_words = tree.xpath('//td[2]/text()')[3:154]
        stop_parts = tree.xpath('//td[3]/text()')[3:154]
        # print(stop_words)
        for i in range(len(stop_words)):
            if stop_parts[i] != 'intj' and stop_parts[i] != 'part':
                f.write(stop_words[i].strip('*')+'\n')
    f.close()
get_stop_words()
