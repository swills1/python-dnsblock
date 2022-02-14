# -*- coding: utf-8 -*-
import requests
import os
from dnsblock.config import BlockConfig as config

def get_source_path():
    default_path = config.default_source_path
    final_path = os.environ.get('DNSBLOCK_SOURCE_PATH', default_path)
    return final_path

def build_source_list(source_path=None):
    if source_path is not None:
        source_path = source_path
    else:
        source_path = get_source_path()
    with open(source_path) as f:
        source_path = f.read().splitlines()
    source_list = [u for u in source_path if not u.startswith('#')]
    return source_list

def fetch_single_blocklist_data(source_path, url):
    response = requests.get(url)
    unbound_blocklist = []
    if response.status_code == 200:
        response_text_list = response.text.splitlines()
        #response_text_list = [a for a in response_text_list if a and not a.startswith('#')]
        for line in response_text_list:
            if line and not line.startswith('#'):
                domain_name = line.split(' ')[-1]
                if domain_name != 'localhost':
                    unbound_blocklist.append(domain_name)
    else:
        print('...')
    return  unbound_blocklist

def count_entries(source=None):
    if source is None:
        source_list = build_source_list(source_path=source)
    d = {}
    for s in source_list:
        response = requests.get(s)
        if response.status_code == 200:
            response_text_list = response.text.splitlines()
            response_text_list = [a for a in response_text_list if not a.startswith('#')]
            text_list_numitems = len(response_text_list)
            d[s] = text_list_numitems 
        else:
            print('...')
    return d
