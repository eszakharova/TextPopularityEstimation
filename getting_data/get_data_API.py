import vk
import csv
# import os
import time
import progressbar

# ссылка для получения кол-ва просмотров
# https://vk.com/like.php?act=a_get_stats&al=1&al_ad=0&object=wall-58620569_399255&views=1


# считываем из файла ид групп, из котрых будем загружать посты
def get_groups():
    group_ids = []
    file = open('groups.txt', 'r')
    for line in file:
        group_ids.append(line.split('=')[-1].strip())
    return group_ids

group_ids = get_groups()

# https://oauth.vk.com/authorize?client_id=5773873&display=page&redirect_uri=http://oauth.vk.com/blank.html&scope=wall,friends,offline&response_type=token&v=5.60
token = '57cd155f4667cb9742308019070a8891e16de156dd902ee3206587b992f14a4e1abb7ab1976e62bad7579'
# вход в учетную запись
session = vk.Session(access_token=token)
api = vk.API(session)


# получение постов для каждой группы
def get_n_posts(group_ids, n):
    '''
            Если надо выкачать от 100 постов со стен групп ВКонтакте.

            Args:
            group_ids: list - список с id нужных групп (без "-" в начале)
            n: int - сколько постов нужно выкачать со стены каждой группы (лучше кратное сотке)

            Функция создает таблицу csv, в каждой строке информация про 1 пост:
            Ид группы, Ид поста, Текст поста, Тип поста, Типы вложений,
            Кол-во лайков, Кол-во репостов
            И еще одну таблицу, содержащую полный словарь поста на всякий случай.
            '''
    # all_posts = []
    new = open('..data/groups_data.csv', 'w', encoding='cp1251')
    full_posts = open('..data/groups_full.csv', 'w', encoding='cp1251')
    row1 = ['Full']
    row0 = ['GroupId', 'Text', 'Type', 'Attachments', 'IsAdd', 'Date', 'Likes', 'Reposts']
    writer = csv.writer(new, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
    writer1 = csv.writer(full_posts, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(row0)
    writer1.writerow(row1)
    bar = progressbar.ProgressBar(max_value=len(group_ids))
    upd = 0
    for group_id in group_ids:
        bar.update(upd)
        upd += 1
        off = 100
        group_posts = []
        while len(group_posts) < n and off <= 5000:
            current_posts = api.wall.get(owner_id='-' + group_id, count=100, offset=off)
            group_posts.extend(current_posts[1:])
            off += 100
            # подождать немного, чтобы не привысить лимит запросов в секунду
            time.sleep(0.4)

        # all_posts.append(group_posts)
        # print(group_posts[0])
        for post in group_posts:
            try:
                if post['text'] != '':
                    if 'attachments' not in post.keys():
                        post['attachments'] = [{'type': 'No'}]
                    row = [group_id, post['text'], post['post_type'], ' '.join([i['type'] for i in post['attachments']]),
                           post['marked_as_ads'], post['date'], post['likes']['count'], post['reposts']['count']]
                    # print(row)
                    row1 = [post]
                    writer.writerow(row)
                    writer1.writerow(row1)
                # bar.update(upd)
                # upd += 1
            except:
                pass
                # bar.update(upd)
                # upd += 1
    bar.finish()
    new.close()
    full_posts.close()
    # return all_posts


get_n_posts(group_ids, 500)
