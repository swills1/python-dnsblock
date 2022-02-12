# -*- coding: utf-8 -*-
import requests

def build_source_list(source_path):
    with open(source_path) as f:
        source_path = f.read().splitlines()
    source_list = [u for u in source_path if not u.startswith('#')]
    return source_list

def count_blocklist_entries(source):
    source_list = build_source_list(source_path=source)
    d = {}
    for s in source_list:
        response = requests.get(s)
        if response.status_code == 200:
            response_text_list = response.text.splitlines()
            text_list_numitems = len(response_text_list)
            d[s] = text_list_numitems 
        else:
            print('poop')
    return d

count = count_blocklist_entries('/home/steven/projects/repos/python-dnsblock/blockfiles/ticked.txt')
print(sum(count.values()))
