import re
import pandas as pd
import progressbar
import csv

data = pd.read_csv('../model/data_preprocessed_final.csv', sep='\t', encoding='cp1251')
data['Exclamation'] = 0
data['Question'] = 0
data['Caps'] = 0
# data[''] = 0

# -----------------progressbar---------------------------
bar = progressbar.ProgressBar(max_value=len(data))
upd = 1
# --------------------------------------------------------
for i in range(len(data)):
    row = data.iloc[i]
    text = row['Text']

    excl = re.findall('!', text)
    data['Exclamation'].iloc[i] = len(excl)

    quest = re.findall('\?', text)
    data['Question'].iloc[i] = len(quest)

    caps = 0
    words = text.split()
    for word in words:
        if word == word.upper() and len(word) > 1:
            caps += 1
    if caps / len(words) <= 0.8:
        data['Caps'].iloc[i] = caps/len(words)
    else:
        data['Caps'].iloc[i] = 0.0

# -----------------progressbar---------------------------
    bar.update(upd)
    upd += 1

bar.finish()
# --------------------------------------------------------

data.to_csv('../model/features_final.csv', sep='\t', encoding='cp1251', quoting=csv.QUOTE_NONNUMERIC)
