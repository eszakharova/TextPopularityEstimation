import re
import pandas as pd
import progressbar
import csv

text = input('input text')

excl = re.findall('!', text)


quest = re.findall('\?', text)


caps = 0
words = text.split()
for word in words:
    print(word, word.upper())
    if word == word.upper():
        caps += 1
print(caps)
if caps/len(words) <= 0.8:
    num_caps = caps/len(words)
else:
    num_caps = 0.0

print(len(excl), len(quest), num_caps)

