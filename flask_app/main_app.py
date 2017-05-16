from flask import Flask
from flask import render_template, request
import vk
import time
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack, vstack
from pymystem3 import Mystem
from sklearn.externals import joblib
import re

m = Mystem()
app = Flask(__name__)

# https://oauth.vk.com/authorize?client_id=5773873&display=page&redirect_uri=http://oauth.vk.com/blank.html&scope=wall,friends,offline&response_type=token&v=5.60
token = '57cd155f4667cb9742308019070a8891e16de156dd902ee3206587b992f14a4e1abb7ab1976e62bad7579'
# вход в учетную запись
session = vk.Session(access_token=token)
api = vk.API(session)


# def vk_api(method, **kwargs):
#     api_request = 'https://api.vk.com/method/'+method + '?'
#     api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
#     return json.loads(requests.get(api_request).text)

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


group_coef_dict = dict()


def get_group_coef(group_id):
    global group_coef_dict
    if group_id not in group_coef_dict:
        off = 100
        num_likes = []
        num_followers = 1
        while len(num_likes) < 500 and off <= 5000:
            current_posts = api.wall.get(owner_id='-' + group_id, count=100, offset=off)
            for post in current_posts[1:]:
                # print(post)
                num_likes.append(post['likes']['count'])
            off += 100
            # подождать немного, чтобы не привысить лимит запросов в секунду
            time.sleep(0.1)
        group_coef_dict[group_id] = np.mean(num_likes) / 100, num_followers
        return np.mean(num_likes) / 100, num_followers
    else:
        return group_coef_dict[group_id]


def browse_obscene():
    f = open('../preprocessing/obscene_regs.txt', 'r')
    obs_regs = [re.compile(i.strip(' \n\'')) for i in f.readlines()]
    return obs_regs


obscene_regs = browse_obscene()


def browse_rusentilex():
    fs = open('../preprocessing/rusentilex_2017.txt', 'r')
    pre_sent_arr = [line.split(', ')[2:4] for line in fs.readlines() if not line.startswith('!')]
    sent_arr = []
    for i in range(len(pre_sent_arr)):
        if pre_sent_arr[i][1] == 'neutral' or pre_sent_arr[i - 1][0] == pre_sent_arr[i][0]:
            continue
        else:
            sent_arr.append(pre_sent_arr[i])
    return sent_arr


sent_arr = browse_rusentilex()


def browse_models():
    knn = joblib.load('../model/knn0.sav')
    frst = joblib.load('../model/frst0.sav')
    vect = joblib.load('../model/tfidf_words.sav')
    return knn, frst, vect


knn, frst, vect = browse_models()


def make_features(link):
    global vect
    gr_id = re.findall('w=wall-([0-9]+)_', link)
    if gr_id != []:
        coef, num_followers = get_group_coef(gr_id[0])
        # page = requests.get(link)
        # tree = html.fromstring(page.content)
        # pre_text = tree.xpath('//div[@class="pi_text"]/text()')
        #
        # text = ' '.join(pre_text)

        post = api.wall.getById(posts='-' + link.split('-')[-1])[0]
        text = post['text']
        text = clean(text)
        lemtext = ''.join(m.lemmatize(text))

        obscene = []
        for reg in obscene_regs:
            found = re.findall(reg, text.lower())
            obscene.extend(found)

        neg_cnt = 0
        pos_cnt = 0
        for pair in sent_arr:
            if pair[0] in lemtext:
                if pair[1] == 'negative':
                    neg_cnt += 1
                else:
                    pos_cnt += 1
        attached = ' '.join([i['type'] for i in post['attachments']])
        ph = len(re.findall('photo', attached))
        link = len(re.findall('link', attached))
        au = len(re.findall('audio', attached))
        vid = len(re.findall('video', attached))
        if post['post_type'] == 'copy':
            post_ = 0
            copy = 1
        else:
            post_ = 1
            copy = 0

        obj = pd.DataFrame(data=[[ph, link, au, vid, post['marked_as_ads'], len(text.split()), num_followers,
                                  neg_cnt, pos_cnt, len(obscene), copy, post_]],
                           columns=['AttPhoto', 'AttLink', 'AttAudio', 'AttVideo', 'IsAdd', 'Len',
                                    'Followers', 'SentNeg', 'SentPos', 'ObsCount', 'copy', 'post'])
        obj_sparse = csr_matrix(obj)
        obj_tfidf = vect.transform([lemtext])

        matrix = hstack((obj_sparse, obj_tfidf))
        return matrix, coef
    else:
        return 'Плохая ссылка(', None


def predict_likes(matrix, coef):
    global knn
    global frst
    frst_likes = frst.predict(matrix)
    knn_likes = knn.predict(matrix)
    final_likes = frst_likes * 0.8 + knn_likes * 0.2
    return final_likes * coef


@app.route('/', methods=['get', 'post'])
def index():
    if request.form:
        link = request.form['link']
        matrix, coef = make_features(link)
        if coef is not None:
            result = round(predict_likes(matrix, coef)[0])
        else:
            result = matrix
        return render_template('index.html', result=result)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
