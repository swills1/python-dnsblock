# -*- coding: utf-8 -*-
import os
import datetime
import requests
import concurrent.futures
from dataclasses import dataclass
from typing import Optional
from dnsblock.config import BlockConfig as config
from dnsblock import utils as ut

@dataclass
class url_repsonse:
    url: str 
    success: bool
    text: Optional[str] = None

def fetch_url_data(session, url, timeout):
    try:
        with session.get(url, timeout=timeout) as response:
            return url_repsonse(url, True, response.text)
    except requests.exceptions.RequestException as e:
        return url_repsonse(url, False, '')

def get_blocklist_data(timeout=10):
    session = requests.Session()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url in ut.build_source_list():
            if not url.startswith('#'):
                futures.append(executor.submit(fetch_url_data, session, url, timeout))
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        bad_urls = [result.url for result in results if not result.success]
        good_urls = [result.url for result in results if result.success]
    return results, bad_urls, good_urls

def unpack_result():
    blocklist_data = get_blocklist_data()
    results = (blocklist_data[0])
    result = [obj.text for obj in results]
    for r in result:
        result_all = r.splitlines()
    return result_all

def format_blocklist_unbound():
    unbound_blocklist = []
    for line in unpack_result():
        if not line.startswith('#'):
            domain_name = line.split(' ')[-1]
            formatted_blocklist_url = 'local-zone: "' + domain_name + '" redirect'
            unbound_blocklist.append(formatted_blocklist_url)
    return unbound_blocklist

def format_blocklist_dnsmaq():
    #address=/example.com/
    unbound_blocklist = []
    for line in unpack_result():
        if not line.startswith('#'):
            domain_name = line.split(' ')[-1]
            formatted_blocklist_url = 'address=/' + domain_name + '/'
            unbound_blocklist.append(formatted_blocklist_url)
    return unbound_blocklist

def build_conf_file(dns_app=None, conf_path=None):
    if dns_app is None or conf_path is None:
        print('Either the dns_app or conf_path argument is empty. Please specify both arguments.')
    else:
        dns_app_lower = dns_app.lower()
        dns_app_dict = config.dns_app_dict
        if dns_app_lower in dns_app_dict:
            dateandtime = datetime.datetime.now()
            date_string = dateandtime.strftime(config.generated_datetime_format)
            if dns_app_lower == 'dnsmasq':
                app_name = dns_app_dict["dnsmasq"]
                lead_string = ''
                blocklist = format_blocklist_dnsmaq()
            elif dns_app_lower == 'unbound':
                app_name = dns_app_dict["unbound"]
                lead_string = config.unbound_conf_lead_string
                blocklist = format_blocklist_unbound()
    with open(conf_path, 'w') as filehandle:
        generatedby_comment = config.generated_comment_lead + app_name + date_string
        filehandle.writelines(generatedby_comment)
        filehandle.write(config.repo_url)
        filehandle.writelines(lead_string)
        for url in blocklist:
            block_url = url + '\n'
            filehandle.writelines(block_url)
