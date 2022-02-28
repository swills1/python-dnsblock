# -*- coding: utf-8 -*-
import requests
import os
from dnsblock import config

def get_source_path():
    """Get the path to the source file containing blocklists to use"""
    default_path = os.path.expanduser(config.DEFAULT_SOURCE_PATH)
    final_path = os.environ.get('DNSBLOCK_SOURCE_PATH', default_path)
    return final_path

def build_source_list(source_path=None):
    """Compile blocklists from source file into a Python list"""
    if source_path is not None:
        source_path = source_path
    else:
        source_path = get_source_path()
    with open(source_path) as f:
        source_path = f.read().splitlines()
    source_list = [u for u in source_path if not u.startswith('#')]
    return source_list

def fetch_single_blocklist(url=None, path=None):
    """Get DNS entries from a single blocklist by specifying the url"""
    if url is None:
        print('Missing url')
    else:
        response = requests.get(url)
        blocklist_data = []
        if response.status_code == 200:
            response_text_list = response.text.splitlines()
            #response_text_list = [a for a in response_text_list if a and not a.startswith('#')]
            for line in response_text_list:
                if line and not line.startswith('#'):
                    domain_name = line.split(' ')[-1]
                    if domain_name != 'localhost':
                        blocklist_data.append(domain_name)
        else:
            print('...')
        return  blocklist_data

def count_entries(source=None):
    """Count number of enties each blocklist has and also sum the total"""
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
