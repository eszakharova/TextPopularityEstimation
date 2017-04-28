import re
import pandas as pd
import progressbar
from pymystem3 import Mystem
import csv

# import indicoio
# indicoio.config.api_key = 'fd4833e39654b9d7502458953ce0733e'

# анализатор
m = Mystem()

# загружаем регулярки с нецензурными выражениями
f = open('obscene_regs.txt', 'r')
obscene_regs = [re.compile(i.strip(' \n\'')) for i in f.readlines()]

# загружаем RuSentiLex
fs = open('rusentilex_2017.txt', 'r')
pre_sent_arr = [line.split(', ')[2:4] for line in fs.readlines() if not line.startswith('!')]
sent_arr = []
for i in range(len(pre_sent_arr)):
    if pre_sent_arr[i][1] == 'neutral' or pre_sent_arr[i-1][0] == pre_sent_arr[i][0]:
        continue
    else:
        sent_arr.append(pre_sent_arr[i])

# на всякий слуйчай пишем посты, где нашлись нецензурные слова, в файл
ob = open('obscene_found.txt', 'w')

data = pd.read_csv('../model/data_preprocessed.csv', sep=';', encoding='cp1251')
data['SentNeg'] = 0  # кол-во негативно окрашенных слов (RuSentiLex)
data['SentPos'] = 0  # кол-во положительно окрашенных слов (RuSentiLex)
data['ObsCount'] = 0  # кол-во нецензурных выражений
# data['SentIndico'] = 0  # значение sentiment с помощью модуля indicoio
data['LemText'] = ''  # лемматизированный текст

# -----------------progressbar---------------------------
bar = progressbar.ProgressBar(max_value=len(data))
upd = 1
# --------------------------------------------------------


for i in range(len(data)):
    row = data.iloc[i]
    text = row['Text']

    # лемматизация
    lemtext = ''.join(m.lemmatize(text))
    data['LemText'].iloc[i] = lemtext

    # поиск нецензуных слов
    obscene = []
    for reg in obscene_regs:
        found = re.findall(reg, text.lower())
        obscene.extend(found)
    data['ObsCount'].iloc[i] = len(obscene)
    if len(obscene) > 0:
        ob.write(str(obscene)+'\n'+text+'\r\n')

    # positive/negative polarity - RuSentiLex
    neg_cnt = 0
    pos_cnt = 0
    for pair in sent_arr:
        if pair[0] in lemtext:
            if pair[1] == 'negative':
                neg_cnt += 1
            else:
                pos_cnt += 1
    data['SentNeg'].iloc[i] = neg_cnt
    data['SentPos'].iloc[i] = pos_cnt

# -----------------progressbar---------------------------
    bar.update(upd)
    upd += 1

bar.finish()
# --------------------------------------------------------

data.to_csv('../model/data_preprocessed_final.csv', sep='\t', encoding='cp1251', quoting=csv.QUOTE_NONNUMERIC)
ob.close()
f.close()
