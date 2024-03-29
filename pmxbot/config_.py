import re

import yaml

import pmxbot
from pmxbot.core import command

@command("config",
	doc="Change the running config, something like a=b or a+=b or a-=b")
def config(client, event, channel, nick, rest):
	pattern = re.compile('(?P<key>\w+)\s*(?P<op>[+-]?=)\s*(?P<value>.*)$')
	match = pattern.match(rest)
	if not match:
		return "Command not recognized"
	res = match.groupdict()
	key = res['key']
	op = res['op']
	value = yaml.safe_load(res['value'])
	if op in ('+=', '-='):
		# list operation
		op_name = {'+=': 'append', '-=': 'remove'}[op]
		op_name
		if not key in pmxbot.config:
			msg = "{key} not found in config. Can't {op_name}."
			return msg.format(**vars())
		if not isinstance(pmxbot.config[key], (list, tuple)):
			msg = "{key} is not list or tuple. Can't {op_name}."
			return msg.format(**vars())
		op = getattr(pmxbot.config[key], op)
		op(value)
	else: # op is '='
		pmxbot.config[key] = value
