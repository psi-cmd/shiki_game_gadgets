import json
import re
from pyperclip import copy, paste
from random import choice
import socket
from requests import get

'''socket info'''
addr = ('127.0.0.1', 2502)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection = None

forbidden_char = {'?'}
used_char = {'?'}

with open('data/zunglish.json', 'r') as f:
    res = json.load(f)

added = False

def search(regstring):
    global used_char
    temp_choice = []
    for i in res:
        if re.match('^' + regstring.replace('?', '.') + '$', i) and not any([k in i for k in forbidden_char]):
            temp_choice.append(i)
    if len(temp_choice) <= 20:
        connection.send('\n'.join(temp_choice).encode())
    else:
        connection.send(b'ok')
    try:
        i = choice(temp_choice)
    except IndexError:
        print('库存不足，restart···')
        connection.send(b'failed')
        return 1
    copy('.hang ' + i)
    print('--------------')
    print('\n'.join(temp_choice))
    used_char |= set(i)


def main():
    s.bind(addr)
    s.listen()
    global connection, used_char, forbidden_char
    connection, _ = s.accept()

    connection.send(b'ready')
    while 1:
        cmd = connection.recv(4)
        if cmd == b'SECH':
            query = paste()
            if '。' in query:
                query = re.search(r'.*? ([a-z?]*)，.*', query).groups()[0]
            forbidden_char |= used_char - set(query)
            if search(query):
                cmd = b'REST'
        if cmd == b'REST':
            print('restarting···')
            forbidden_char = {'?'}
            used_char = {'?'}
        if cmd == b'ADIN':
            add = paste()
            if re.match('^[a-z]*$', add):
                connection.send(b'OK')
                print(f'adding {add}.')
                res.append(add)
                with open('data/zunglish.json', 'w') as f:
                    json.dump(res, f)
            else:
                connection.send(b'failed')
                print('some error in copied string.')



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise e



'''
def all_english(url):
    html = get(url)
    soup = Soup(html.text)
    res = re.findall(r'([a-zA-Z]+)', soup.text)
    res = list(filter(lambda x: len(x) > 3, res))
    res = list(set(res))
    res = [i.lower() for i in res]
    return res


def dict_add(*args, save=True):
    global res
    for i in args:
        res.append(i.lower())
    res = list(set(res))
    if save == True:
        f = open('data/zunglish.json', 'w')
        json.dump(res, f)
        f.close()
        return 0
    return res
'''