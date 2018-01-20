# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 20:30:28 2018

@author: Oliver
"""

import itertools
import random

def incr(key, table):
    table[key] = 1 + table.get(key,0)
    

def moving_iter(iterable, n=2):
	ibles = itertools.tee(iterable,n)
	for i,it in enumerate(ibles):
		for k in range(i):
			next(it)

	return zip(*ibles)


class LModel(object):	
    def __init__(self):
        self.FWD_TABLE = {}
        self.BACK_TABLE = {}
        self.totals = {}
       
    def count(self, words):
        current = self.FWD_TABLE
        levels = 0
        for w in words:
            if w not in current:
                current[w] = {}
            current = current[w]
            levels += 1
        
        incr('#', current)
        incr(levels, self.totals)
        
    def P(self, items):
        current = self.FWD_TABLE
        for name in items:
            current = current[name]
        #current

    def ngrams(self, filename, n):
        with open('rapdata/hihop.txt', 'r') as f:
            for line in f:
                words = line.split();
                for k in range(1, n+1):
                    for ww in moving_iter(words, k):
                        self.count(ww)
                        
        return self
        
    def complete(self, prefix):
        table = self.FWD_TABLE;
        for w in prefix:
            if w in table:
                table = table[w]
            else:
                return self.complete(prefix[1:])

        for k in table:
            num table.get('#', 0)