#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-
import os
import cherrypy
import string
try:
	from pysqlite2 import dbapi2 as sqlite
except ImportError:
	from sqlite3 import dbapi2 as sqlite
from random import shuffle
import cherrypy
import calendar
from jinja2 import Environment, FileSystemLoader

from cgi import escape

from pmxbot.logging import init_logger

BASE = os.path.abspath(os.path.dirname(__file__))
jenv = Environment(loader=FileSystemLoader(os.path.join(BASE, 'templates'), encoding='utf-8'))
TIMEOUT=10.0



colors = ["06F", "900", "093", "F0C", "C30", "0C9", "666", "C90", "C36", "F60", "639", "630", "966", "69C", "039", '7e1e9c', '15b01a', '0343df', 'ff81c0', '653700', 'e50000', '029386', 'f97306', 'c20078', '75bbfd']
shuffle(colors)

def get_context():
	c = cherrypy.request.app.config['botconf']['config']
	d = {'request': cherrypy.request, 'name' : c.bot_nickname, 'config' : c, 'base' : c.web_base, }
	try:
		d['logo'] = c.logo
	except AttributeError:
		d['logo'] = ''
	return d

def make_anchor(line):
	return "%s.%s" % (line[0].replace(':', '.'), line[1])


th_map = {1 : 'st', 2 : 'nd', 3 : 'rd'}
def th_it(num):
	if num in range(11, 14):
		end = 'th'
	elif num % 10 in th_map:
		end = th_map[num % 10]
	else:
		end = 'th'
	return '%s%s' % (num, end)

def pmon(month):
	year, month = month.split('-')
	return '%s, %s' % (calendar.month_name[int(month)], year)

def pday(dayfmt):
	year, month, day = map(int, dayfmt.split('-'))
	return '%s the %s' % (calendar.day_name[calendar.weekday(year, month, day)], 
	th_it(day))

rev_month = {}
for x in xrange(1, 13):
	rev_month[calendar.month_name[x]] = x

def sort_month_key(m):
	parts = m.split(',')
	parts[0] = rev_month[parts[0]]
	return parts[1], parts[0]


class ChannelPage(object):
	def default(self, channel):
		page = jenv.get_template('channel.html')
		
		db = init_logger(cherrypy.request.app.config['db'])
		context = get_context()
		contents = db.get_channel_days(channel)
		months = {}
		for fn in sorted(contents, reverse=True):
			mon_des, day = fn.rsplit('-', 1)
			months.setdefault(pmon(mon_des), []).append((pday(fn), fn))
		context['months'] = sorted(months.items(), key=lambda v: sort_month_key(v[0]),
		reverse=True) 
		context['channel'] = channel
		return page.render(**context).encode('utf-8')
	default.exposed = True

class DayPage(object):
	def default(self, channel, day):
		page = jenv.get_template('day.html')
		db = get_logger_db(cherrypy.request.app.config['db'])
		context = get_context()
		day_logs = db.get_day_logs()
		data = [(t, n, make_anchor((t, n)), escape(m)) for (t,n,m) in day_logs]
		usernames = [x[1] for x in data]
		color_map = {}
		clrs = colors[:]
		for u in usernames:
			if u not in color_map:
				try:
					color = clrs.pop(0)
				except IndexError:
					color = "000"
				color_map[u] = color
		context['color_map'] = color_map
		context['history'] = data
		context['channel'] = channel
		context['pdate'] = "%s of %s" % (pday(day), pmon(day.rsplit('-', 1)[0]))
		return page.render(**context).encode('utf-8')
	default.exposed = True


def karma_comma(karma_results):
	"""
	Take the results of a karma query (keys, value) and return the same
	result with the keys joined by commas.
	"""
	return [
		(', '.join(keys), value)
		for keys, value in karma_results
	]

class KarmaPage(object):
	def default(self, term=""):
		page = jenv.get_template('karma.html')
		context = get_context()
		karma = util.get_karma_from_uri(cherrypy.request.app.config['db'])
		term = term.strip()
		if term:
			context['lookup'] = (
				[karma_comma(res) for res in karma.search(term)]
				or [('NO RESULTS FOUND', '')]
			)
		context['top100'] = karma_comma(karma.list(select=100))
		context['bottom100'] = karma_comma(karma.list(select=-100))
		return page.render(**context).encode('utf-8')
	default.exposed = True

class SearchPage(object):
	def default(self, term=''):
		page = jenv.get_template('search.html')
		context = get_context()
		db = get_logger_db(cherrypy.request.app.config['db'])
		#db.text_factory = lambda x: unicode(x, "utf-8", "ignore")

		# a hack to enable the database to create anchors when building search
		#  results
		db.make_anchor = make_anchor
	
		if not term:
			raise cherrypy.HTTPRedirect(cherrypy.request.base)
		terms = term.strip().split()
		results = sorted(db.search(*terms), key=lambda x: x[1], reverse=True)
		context['search_results'] = results
		context['num_results'] = len(results)
		context['term'] = term
		return page.render(**context).encode('utf-8')
	default.exposed = True
		
	
class HelpPage(object):
	def __init__(self):
		self.run = False
		
	def default(self):
		page = jenv.get_template('help.html')
		context = get_context()
		if not self.run:
			self.commands = []
			self.contains = []
			import pmxbot.pmxbot as p
			p.run(configInput = context['config'], start=False)
			for typ, name, f, doc, channels, exclude, rate, priority in sorted(p._handler_registry, key=lambda x: x[1]):
				if typ == 'command':
					aliases = sorted([x[1] for x in p._handler_registry if x[0] == 'alias' and x[2] == f])
					self.commands.append((name, doc, aliases))
				elif typ == 'contains':
					self.contains.append((name, doc))
			self.run = True
		context['commands'] = self.commands
		context['contains'] = self.contains
		return page.render(**context).encode('utf-8')
	default.exposed = True
	

class PmxbotPages(object):
	channel = ChannelPage()
	day = DayPage()
	karma = KarmaPage()
	search = SearchPage()
	help = HelpPage()
	
	def default(self):
		page = jenv.get_template('index.html')
		db = get_logger_db(cherrypy.request.app.config['db'])
		context = get_context()
		chans = []
		for chan in sorted(db.list_channels(), key = string.lower):
			last = db.last_message(chan)
			summary = [
				chan,
				last['time'].strftime("%Y-%m-%d %H:%M"),
				last['time'].date(),
				last['time'].time(),
				last['nick'],
				escape(last['message'][:75]),
				make_anchor([last['time'].time(), last['nick']]),
			]
			chans.append(summary)
		context['chans'] = chans
		return page.render(**context).encode('utf-8')
	default.exposed = True
