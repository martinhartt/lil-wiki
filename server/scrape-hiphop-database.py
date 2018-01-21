# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 20:51:47 2018

@author: Oliver
"""

# language models

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()



from bs4 import BeautifulSoup
import requests



def crawl(url, host, writer=None, container=None, append=True):
    page = requests.get(host + url).text
    #print(url)
    if url[-4:] == '.txt':
        tagless = strip_tags(page)
        lines = tagless.split('\n')[4:]
        if not writer:
            return lines

        for line in lines:
            #print(line)
            writer.write(line+'\n')
        return

    if not writer: results = []

    soup = BeautifulSoup(page, 'html.parser')
    if container is not None:
        soup = soup.find(container)

    for a in soup.find_all('a'):
        #print(' ..',a,'?')
        if not a.has_attr('href'):
            continue

        href = a.get('href')
        if href[0] in '?/':
            continue
        #print(' --> ', href)

        newrslt = crawl(url+href if append else href, host, writer)
        if not writer: results.extend(newrslt)
    #print('<')

    if not writer: return results




def get_all():
    with open('rapdata/hihop.txt', 'a', 1, encoding="utf-8") as hiphop:
        host = 'http://ohhla.com/'
        crawl('all_three.html', host, hiphop,'pre', False)
