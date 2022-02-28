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

def unpack_dnslist():
    """Isolate DNS names from blockist and build a list of only DNS names"""
    blocklist_data = get_blocklist_data()
    results = (blocklist_data[0])
    result = [obj.text for obj in results]
    for r in result:
        result_all = r.splitlines()
    return result_all

def format_dnslist(app: str, prefix: str='', suffix: str=''):
    """Format dns names in preparation for conf file"""
    app_lower = app.lower()
    formatted_blocklist = []
    known_app_dict = config.DNS_APP_DICT
    if app in known_app_dict:
        prefix, suffix = known_app_dict.get(app_lower)
    elif app_lower == 'custom':
        prefix = prefix
        suffix = suffix
    else:
        raise ValueError(f'"{app_lower}" is not a valid app choice') 
    for line in unpack_dnslist():
        if not line.startswith('#'):
            domain_name = line.split(' ')[-1]
            formatted_blocklist_url = prefix + domain_name + suffix
            formatted_blocklist.append(formatted_blocklist_url)
    return formatted_blocklist

def build_conf_file(app: str, conf_path: str, leadstring: str='', prefix: str='', suffix: str=''):
    formatted_blocklist = format_dnslist(app, prefix, suffix)
    #dns_app = app
    dateandtime = datetime.datetime.now()
    date_string = dateandtime.strftime(config.GENERATED_DATETIME_FORMAT)
    lead_dict = config.LEADSTRING_DICT
    if app in lead_dict:
        leadstring = lead_dict.get(app)
    with open(conf_path, 'w') as filehandle:
        generatedby_comment = config.GENERATED_COMMENT_LEAD + app + date_string
        filehandle.writelines(generatedby_comment)
        filehandle.write(config.REPO_URL)
        filehandle.writelines(leadstring)
        for url in formatted_blocklist:
            block_url = url + '\n'
            filehandle.writelines(block_url)
