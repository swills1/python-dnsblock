# -*- coding=utf-8 -*-
import click
from dnsblock import config
from dnsblock import utils as ut

@click.group()
def dnsblock():
    pass

@dnsblock.command()
@click.option('--list', '-l', is_flag=True, help='List each blocklist urls and its entry count')
@click.option('--total', '-t', is_flag=True, help='Show total entry count from combined blocklists')
def count(list, total):
    if list:
        print(ut.count_entries())
    elif total:
        data = ut.count_entries()
        print((sum(data.values())))

@dnsblock.command()
@click.option('--app', '-a', type=click.Choice(config.DNS_APP_DICT), is_flag=False, help='DNS app to format for')
@click.option('--path', '-p', is_flag=False, help='Conf file path')
def run(app, path):
    if app == 'dnsmasq':
        print('Dnsmasq')
    elif app == 'unbound':
        print('Unbound')

@dnsblock.command()
@click.option('--url', '-u', is_flag=False, help='Conf file path')
@click.option('--path', '-p', is_flag=False, help='Conf file path')
def fetch(url, path):
    data = ut.fetch_single_blocklist(url, path)
    print(data)


if __name__ == '__main__':
    dnsblock()
