# -*- coding: utf-8 -*-
import datetime
import requests
import concurrent.futures
from dataclasses import dataclass
from typing import Optional
from dnsblock import config
from dnsblock import utils as ut

@dataclass
class url_repsonse:
    url: str 
    success: bool
    text: Optional[str] = None

def fetch_url_data(session, url, timeout):
    """Fetch all data from blocklist urls and trap specific errors"""
    try:
        with session.get(url, timeout=timeout) as response:
            return url_repsonse(url, True, response.text)
    except requests.exceptions.RequestException as e:
        return url_repsonse(url, False, '')

def get_blocklist_data(timeout=10):
    """Use threading to process the source list and pull in fetched url data"""
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

def unpack_dnsname():
    """Isolate DNS names from blockist and build a list of only DNS names"""
    blocklist_data = get_blocklist_data()
    results = (blocklist_data[0])
    result = [obj.text for obj in results]
    for r in result:
        result_all = r.splitlines()
    return result_all

def format_dnsname_list(app: str, prefix: str='', suffix: str=''):
    app_lower = app.lower
    formatted_blocklist = []
    app_choices = config.DNS_APP_DICT.keys()
    if app not in app_choices:
        print('App choice is not valid')
    elif app_lower == 'unbound':
      prefix = 'local-zone: "'
      suffix = '" redirect'
    elif app_lower == 'dnsmasq':
      prefix = 'address=/'
      suffix = '/'
    elif app_lower == 'custom':
        prefix = prefix
        suffix = suffix
    for line in unpack_result():
        if not line.startswith('#'):
            domain_name = line.split(' ')[-1]
            formatted_blocklist_url = prefix, domain_name, suffix
            formatted_blocklist.append(formatted_blocklist_url)
    return formatted_blocklist

def format_blocklist_dnsmaq():
    #address=/example.com/
    unbound_blocklist = []
    for line in unpack_result():
        if not line.startswith('#'):
            domain_name = line.split(' ')[-1]
            formatted_blocklist_url = 'address=/' + domain_name + '/'
            unbound_blocklist.append(formatted_blocklist_url)
    return unbound_blocklist

def build_conf_file(app: str, conf_path: str,prefix: str='', suffix: str=''):
    if dns_app is None or conf_path is None:
        print('Either the dns_app or conf_path argument is empty. Please specify both arguments.')
    else:
        dns_app_lower = dns_app.lower()
        DNS_APP_DICT = config.DNS_APP_DICT
        if dns_app_lower in DNS_APP_DICT:
            dateandtime = datetime.datetime.now()
            date_string = dateandtime.strftime(config.GENERATED_DATETIME_FORMAT)
            if dns_app_lower == 'dnsmasq':
                app_name = DNS_APP_DICT["dnsmasq"]
                lead_string = ''
                blocklist = format_blocklist_dnsmaq()
            elif dns_app_lower == 'unbound':
                app_name = DNS_APP_DICT["unbound"]
                lead_string = config.LEADSTRING_DICT['unbound']
                blocklist = format_blocklist_unbound()
    with open(conf_path, 'w') as filehandle:
        generatedby_comment = config.GENERATED_COMMENT_LEAD + app_name + date_string
        filehandle.writelines(generatedby_comment)
        filehandle.write(config.REPO_URL)
        filehandle.writelines(lead_string)
        for url in blocklist:
            block_url = url + '\n'
            filehandle.writelines(block_url)
