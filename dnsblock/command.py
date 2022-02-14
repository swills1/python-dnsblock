# -*- coding=utf-8 -*-
import click
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

#cli = click.CommandCollection(sources=[dnsblock])
if __name__ == '__main__':
    dnsblock()
