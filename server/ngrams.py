# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 20:30:28 2018

@author: Oliver
"""

import itertools
import random
import nltk

def incr(key, table):
	table[key] = 1 + table.get(key,0)
	return table[key]


def moving_iter(iterable, n=2):
	ibles = itertools.tee(iterable,n)
	for i,it in enumerate(ibles):
		for k in range(i):
			try:
				next(it)
			except:
				pass

	return zip(*ibles)


def get_alpha(N, i):
	return 1/(N - i) if N > i else 1

def getlen(table, idx):
	if idx in table and '#' in table[idx]:
		return table[idx]['#']
	return 0

def identity(x): return x

class LModel(object):
	def __init__(self, direction='both'):
		if direction in 'both foreward' and len(direction) > 1:
			self.FWD_TABLE = {}
		if direction in 'both backward':
			self.BACK_TABLE = {}

		#Mprint(self.__dict__, direction)

		self.totals = {}


	def count(self, words):
		to_count = True
		if(self.FWD_TABLE is not None):
			self._count(words, self.FWD_TABLE, identity, to_count)
			to_count = False

		if(self.BACK_TABLE is not None):
			self._count(words, self.BACK_TABLE, reversed, to_count)

	def _count(self, words, table, permuter, to_count):
		current = table
		#previous = None
		levels = 0
		for w in permuter(words):
			if w not in current:
				current[w] = {}
			#previous = current
			current = current[w]
			levels += 1

		if incr('#', current) == 1:
			if to_count:
				incr(levels, self.totals)


	def countLine(self, line, n):
		tokens = ''.join(filter(lambda c: c.isalpha() or c in ' \'', line.replace('\t', ' '))) \
			.lower().split()
		tokens = ['START'] + tokens + ['END']
		#print(tokens)
		for k in range(1, n+1):
			for ww in moving_iter(tokens, k):
				self.count(ww)

	def P(self, items):
		current = self.FWD_TABLE
		for name in items:
			current = current[name]
        #current

	def ngrams(self, filename, n):
		with open(filename, 'r', encoding='latin-1') as f:
			for line in f:
				self.countLine(line, n)

		return self

	def _complete(self, prefix, TABLE, starter):
		table = TABLE
		for w in prefix:
			if w in table and len(table[w]) > 1:
				table = table[w]
			else:
				return self._complete(prefix[1:], TABLE, starter)

		print(self.totals)
		N = self.totals[1] - 1
		cum = 0
		thresh = random.random()
		NN = table['#']
		alpha = get_alpha(N, NN)
		#print(N, NN, alpha)
		#print(table)

		for k in TABLE:
			if k[0] != '#':

				cum += (getlen(table,k) + alpha) / (NN + alpha*N)
				#print(k, cum, thresh, (NN + alpha*N), sep='\t')

				if thresh < cum and k != starter:
					return k
		#print('sum', sum((getlen(table,k) + alpha) / (NN + alpha*N) for k in TABLE if k[0] != '#'))
		raise ValueError("Probability data makes no sense")

	def complete(self, prefix):
		return self._complete(prefix, self.FWD_TABLE, 'START')
	def rcomplete(self, postfix):
		return self._complete(postfix, self.BACK_TABLE, 'END')

	def spin(self, seed = 'START'):
		hist = [self.complete([seed]) ]
		while(hist[-1] != "END"):
			#print(hist)
			hist.append(self.complete(hist))

		return hist[:-1]

	def rspin(self, seed='END'):
		hist = [self.rcomplete([seed]) ]
		while(hist[-1] != "START"):
			#print(hist)
			hist.append(self.rcomplete(hist))

		return list(reversed(hist))[1:]
