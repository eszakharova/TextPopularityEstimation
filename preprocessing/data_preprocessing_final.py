import re
import pandas as pd
import progressbar
from pymystem3 import Mystem
import csv

m = Mystem()

data = pd.read_csv('../data/groups_data.csv', sep=';', encoding='cp1251')
stats = pd.read_csv('group_stats.csv', sep=';', encoding='cp1251')


def clean(text):
    text = text.replace('<br>', ' ')  # теги
    text = re.sub('(?:http://|www\.|https://){0,1}(?:[0-9]*[a-zA-Z]+[0-9]*\.)+[a-zA-Z/\.0-9?=\-_]+',
                  ' ', text)  # внешние ссылки
    text = re.sub('club[0-9]+', ' ', text)  # ссылки на сообщества
    text = re.sub('id[0-9]+', ' ', text)  # ссылки на личные станицы
    text = re.sub('[\[\]\|\(\)]+', '', text)  # лишние скобки
    text = re.sub('\W@\W', ' ', text)  # улиточки
    text = re.sub('\W[0-9_-]{5,}\W', ' ', text)  # больше 4 цифр подряд
    text = re.sub('\W0{3,}\W', ' ', text)  # много нулей
    #     text = re.sub('\s[A-Z][a-z][A-Z][a-z]{0,1}', ' ', text) #остатки ссылок
    return text


# загружаем регулярки с нецензурными выражениями
f = open('obscene_regs.txt', 'r')
obscene_regs = [re.compile(i.strip(' \n\'')) for i in f.readlines()]

# загружаем RuSentiLex

new = open('../model/final_preprocessed_data.csv', 'w', encoding='cp1251')
row0 = ['Text', 'Type', 'AttPhoto', 'AttLink', 'AttAudio', 'AttVideo', 'IsAdd', 'Len', 'Date',
        'LikesNormAvg', 'LikesNormFlw', 'Likes', 'AvgLikes', 'Followers', 'GroupId', 'LemText', 'ObsCount',
        'SentNeg', 'SentPos']
writer = csv.writer(new, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(row0)
bar = progressbar.ProgressBar(max_value=len(data))
upd = 1
for i in range(len(data)):
    row = data.iloc[i]
    if len(clean(row['Text']).split()) >= 3:
        text = clean(row['Text'])
        lemtext = ''.join(m.lemmatize(text))
        obscene = []
        for reg in obscene_regs:
            found = re.findall(reg, text.lower())
            obscene.extend(found)
        row1 = [text, row['Type'], len(re.findall('photo', row['Attachments'])),
                len(re.findall('link', row['Attachments'])), len(re.findall('audio', row['Attachments'])),
                len(re.findall('video', row['Attachments'])), row['IsAdd'], len(text.split()),
                row['Date'],
                (int(row['Likes']) / int(stats['AvgLikes'][stats['GroupId'] == row['GroupId']])) * 100,
                (int(row['Likes']) / int(stats['Followers'][stats['GroupId'] == row['GroupId']])) * 100,
                int(row['Likes']), int(stats['AvgLikes'][stats['GroupId'] == row['GroupId']]),
                int(stats['Followers'][stats['GroupId'] == row['GroupId']]),
                row['GroupId'],
                lemtext,
                len(obscene)]

        writer.writerow(row1)
    bar.update(upd)
    upd += 1
bar.finish()
new.close()
