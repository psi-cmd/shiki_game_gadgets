'''静态实现
先获取关键词，装在列表里，字典储存词条和列表索引顺序。
关于接死：
词库不全，无法确定接死目标。如果可以确定接死目标子集，可通过 find_death 立即找到致死链。
'''

import re
import json
import socket
from pyperclip import copy, paste
import codecs
from random import sample, choice

'''socket info'''
addr = ('127.0.0.1', 2501)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection = None

'''words info'''

f = [open('data/game_char.json', 'r'), open('data/spellcard_simple.json', 'r'),
     open('data/spellcard_full.json'), open('data/place_scene.json', 'r'),
     open('data/items.json', 'r'), open('data/nickname.json', 'r'),
     open('data/music.json', 'r'), open('data/stages.json', 'r'),
     open('data/aya_news.json', 'r'), open('data/wenhuatie.json', 'r'),
     open('data/dead_end.json', 'r')]

game_char = json.load(f[0])
spellcard_simple = json.load(f[1])
spellcard_full = json.load(f[2])
place_scene = json.load(f[3])
items = json.load(f[4])
nickname = json.load(f[5])
music = json.load(f[6])
stages = json.load(f[7])
aya_news = json.load(f[8])
wenhuatie = json.load(f[9])

dead_end = json.load(f[-1])
for i in f:
    i.close()

with open('data/count_dict_V2.json', 'r') as f:
    link_dict = json.load(f)

with codecs.open('data/fusion_V2_dict.json', 'r', encoding='utf-8') as f:
    pinyin_dict = json.load(f)
    pinyin_dict = dict([(i[0], i[1:]) for i in pinyin_dict])  # 用来代替 pypinyin 模块

fusion = list(set(
    game_char + spellcard_full + spellcard_simple + place_scene + items + nickname + music + stages + aya_news + wenhuatie))
fusion = list(filter(lambda x: len(x) != 1 and not re.search(r'[^\u4e00-\u9fa5]', x), fusion))

# fusion = json.load(open('data/fusion_V1.json', 'r'))

'''longest 使用出口最多策略'''

search_forbid = []  # 如果寻找合适的内容时 search_forbid 首位相同，不清空，保证下一次不需要再次跳过
prev_head = None
cmd = None
mode = None

with open('data/way_to_death.json', 'r') as f:
    way_to_death = json.load(f)


def main(tech='longest'):
    '''longest / random / todeath'''
    s.bind(addr)
    s.listen()
    global connection, go_die, cmd, mode
    mode = tech
    connection, _ = s.accept()

    target = input('读音：')
    cmd = connection.recv(4)
    forbid = []
    while 1:
        if cmd == b'NEXT':
            if tech == 'longest':
                next_target = max(link_dict[target][1].keys(), key=lambda x: link_dict[x][
                    0] if x not in dead_end + forbid else 0)  # 根据哪个读音可以接的最多来确定 #如果出错，收词太少
            elif tech == 'random':
                next_target = sample(set(link_dict[target][1].keys()) - set(dead_end), 1)[0]
            elif tech == 'todeath':
                try:
                    next_target = way_to_death[target]
                except KeyError:
                    print('end reaches, restarting...')
                    connection.send(b'end reaches, put next string in clipboard.')
                    reload()
                    cmd = connection.recv(4)
                    assert cmd == b'NEXT'
                    try:
                        target = choice(pinyin_dict[paste()][1])
                    except KeyError:
                        target = input('读音：')
                    continue
            result = search_paste(target, next_target)
            if result == 1:
                forbid.append(next_target)  # 直接重选，并禁止其参与选拔。
                continue
            elif result == 2:
                target = input('读音：')
                connection.send(b'OK')
                continue
            elif result == 3:
                while result == 3:
                    next_target = choice(list(set(link_dict[target][1]) & set(way_to_death.keys())))
                    result = search_paste(target, next_target)
            forbid.clear()
            target = next_target


def reload():
    global fusion, link_dict
    with open('data/count_dict_V2.json', 'r') as f:
        link_dict = json.load(f)
    fusion = list(set(
        game_char + spellcard_full + spellcard_simple + place_scene + items + nickname + music + stages + aya_news + wenhuatie))
    fusion = list(filter(lambda x: len(x) != 1 and not re.search(r'[^\u4e00-\u9fa5]', x), fusion))


def search_paste(head, tail):  # 负责搜索并删除词和对应索引计数
    global search_forbid, prev_head, cmd
    if head != prev_head:
        search_forbid.clear()
        prev_head = head  # 接同一个音，必禁同一个字。
    for i in fusion:
        h = pinyin_dict[i][0]
        t = pinyin_dict[i][1]
        if head in h and tail in t and i[0] not in search_forbid:
            copy('.jl ' + i)
            if cmd == b'NEXT':
                connection.send(b'OK')
            cmd = connection.recv(4)
            if cmd == b'RETR':
                connection.send(b'OK')
                search_forbid.append(i[0])  # 记住这个字，不可以在“这种情况”使用。
                if mode == 'todeath':
                    return 3
                continue
            elif cmd == b'STOP':
                connection.send(b'OK')
                return 2
            fusion.remove(i)
            for j in h:
                link_dict[j][0] -= len(t)
                for k in t:
                    link_dict[j][1][k] -= 1
                    if not link_dict[j][1][k]:
                        del link_dict[j][1][k]
                if not link_dict[j][0]:  # 这里应该是双保险吧
                    assert link_dict[j][1] == {}
                    del link_dict[j]
                    dead_end.append(j)
            if cmd == b'DELE':  # 如果有词没收录，就只能空转 delete，然后选下一个。
                connection.send(b'OK')
                continue
            return 0
    return 1


if __name__ == '__main__':
    while 1:
        try:
            main(tech='random')
        except ConnectionResetError:
            pass


def find_death(target_str):
    global way_to_death
    unrelated_set = set(link_dict.keys()) - set(pinyin_dict[target_str][0])
    temp = []
    for i in pinyin_dict[target_str][0]:
        way_to_death[i] = pinyin_dict[target_str][1][0]  # 假设不是多音字，是也没关系。 #添加最终表
        for j, k in pinyin_dict.items():
            if i in k[1]:
                temp += k[0]
        for l in set(temp) & unrelated_set:
            way_to_death[l] = i
        unrelated_set -= set(temp)
        temp.clear()
    counter = 12
    while unrelated_set and counter:
        for i in unrelated_set:
            for j in way_to_death.keys():
                if not search_print(i, j):
                    temp.append((i, j))
                    break
        for i, j in temp:
            way_to_death[i] = j
            unrelated_set.remove(i)
        temp.clear()
        counter -= 1
    return unrelated_set

    next_target = sample(link_dict[start][1].keys(), 1)[0]
    find_death(next_target)
    way_to_death.append(next_target)
    return


def search_print(head, tail):  # 负责搜索并删除词和对应索引计数
    global search_forbid, prev_head
    if head != prev_head:
        search_forbid.clear()
        prev_head = head  # 接同一个音，必禁同一个字。
    for i in fusion:
        h = pinyin_dict[i][0]
        t = pinyin_dict[i][1]
        if head in h and tail in t and i[0] not in search_forbid:
            print('.jl ' + i)
            return 0
    return 1


def save_new_fusion(string):
    with codecs.open(string, 'w', 'utf-8') as f:
        json.dump(fusion, f)
    return 0


'''
        for i in fusion:
            if target in pinyin(i, Style.NORMAL, heteronym=True)[0]:
                if i in dead_end:
                    print('*! ', i)
                else:
                    print(i)
'''
