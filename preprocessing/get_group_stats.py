import numpy as np
import pandas as pd
import vk
import csv


def get_groups():
    group_ids = []
    file = open('groups.txt', 'r')
    for line in file:
        group_ids.append(line.split('=')[-1].strip())
    return group_ids


def get_followers_count(group_ids):
    # https://oauth.vk.com/authorize?client_id=5773873&display=page&redirect_uri=http://oauth.vk.com/blank.html&scope=wall,friends,offline&response_type=token&v=5.60
    token = '57cd155f4667cb9742308019070a8891e16de156dd902ee3206587b992f14a4e1abb7ab1976e62bad7579'

    # вход в учетную запись
    session = vk.Session(access_token=token)
    api = vk.API(session)
    pre_num_followers = api.groups.getById(group_ids=group_ids, fields="members_count")
    num_followers = []
    for gr in pre_num_followers:
        num_followers.append(gr['members_count'])
    return num_followers


def get_average_likes_sample(group_ids, fulldata):
    avg_likes = []
    for group_id in group_ids:
        current_likes = fulldata['Likes'][fulldata['GroupId'] == int(group_id)]
        avg = int(np.round(np.sum(current_likes)/len(current_likes)))
        avg_likes.append(avg)
    return avg_likes


def group_stats_to_csv(group_ids, fulldata):
    avg_likes = get_average_likes_sample(group_ids, fulldata)
    num_followers = get_followers_count(group_ids)
    new = open('group_stats.csv', 'w', encoding='cp1251')
    row0 = ['GroupId', 'AvgLikes', 'Followers']
    writer = csv.writer(new, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(row0)
    for i in range(len(group_ids)):
        row = [group_ids[i], avg_likes[i], num_followers[i]]
        writer.writerow(row)
    new.close()

dat = pd.read_csv('groups_data.csv', sep = ';', encoding = 'cp1251')
group_ids = get_groups()
group_stats_to_csv(group_ids, dat)
