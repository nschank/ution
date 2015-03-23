import argparse
from argparse import Namespace
import datetime
from datetime import datetime, timedelta
from dateutil import parser as dparse
from random import randint
import re
import sys
import time
import pickle

class TodoItem:
	def __init__(self, value):
		self.value = value
		self.important = False
		self.duedate = None
		self.startdate = None
		self.category = None
	
	def __lt__(self, other):
		if self.category == other.category:
			return self.value < other.value
		elif self.category is None:
			return False
		elif other.category is None:
			return True
		else:
			return self.category < other.category
			
			
def check_before(todo_item, duedate):
	return (todo_item.duedate is not None and todo_item.duedate <= duedate)
	
def check_important(todo_item):
	return todo_item.important or check_before(todo_item, datetime.today()+timedelta(days=2))

def check_past(todo_item):
	return todo_item.startdate is None or todo_item.startdate <= datetime.today()
	
def do_add(data, settings):
	cat = None
	if len(settings.item) > 0 and settings.item[0][-1] == ':':
		cat = settings.item[0][:-1].upper()
		settings.item.pop(0)
	item = TodoItem(' '.join(settings.item))
	item.category = cat
	if settings.important:
		item.important = True
	if settings.time is not None:
		try:
			item.duedate = datetime.today() if "today" in settings.time else dparse.parse(' '.join(settings.time))
		except Exception:
			item.duedate = None
	if settings.start is not None:
		try:
			item.startdate = datetime.today() if "today" in settings.start else dparse.parse(' '.join(settings.start))
		except Exception:
			item.startdate = None
	data.append(item)
	data.sort()
	do_print(data) 
	rewrite(settings.filename, data)
	
def do_get_rand(olddata, settings):
	data = olddata
	if len(settings.categories) > 0:
		data = [item for item in data if (item.category in settings.categories or ("none" in settings.categories and item.category is None))]

	if settings.important:
		data = [item for item in data if item.important]
	if settings.time is not None:
		try:
			data = [item for item in data if check_before(item, dparse.parse(' '.join(settings.time)))]
		except Exception:
			print("Warning: time argument was improperly formatted.")
			
	if len(data) == 0:
		print ("Error: no items found.")
	else:
		index = randint(0,len(data)-1)
		print("Random item:")
		print_item(data[index], olddata.index(data[index]))
		
def do_hide(data, settings):
	settings.indices.sort()
	settings.indices.reverse()
	for element in settings.indices:
		try:
			if data[element].startdate is None:
				data[element].startdate = datetime.today()
			data[element].startdate = data[element].startdate+timedelta(days=7)
			if data[element].duedate is not None and data[element].startdate > data[element].duedate-timedelta(days=3):
				data[element].startdate = data[element].duedate-timedelta(days=3)
		except Exception:
			print ('Failed to hide item', element)
	print ("\nResult:")
	do_print(data)
	rewrite(settings.filename, data)
	
def do_print(data, settings=Namespace(time=None,important=False, categories=[], verbose=False)):
	settings.categories = [category.upper() for category in settings.categories]
	duedate = None
	if settings.time is not None:
		try:
			duedate = datetime.today() if "today" in settings.time else dparse.parse(' '.join(settings.time))
		except Exception:
			print("Warning: time argument was improperly formatted.")
	
	printed = False
	if settings.verbose:
		print ('+====+' + '='*43 + '+' + '='*26 + '+')
		print ('| {:2s} |  {:>5s} {!s:<30s} {} | {:^11s}  {:^11s} |'.format(" #","CAT ","ITEM", "IMP", "START", "DUE"))
		print ('+====+' + '='*43 + '+' + '='*26 + '+')
	else:
		print ('+====+' + '='*43 + '+' + '='*13 + '+')
		print ('| {:2s} |  {:>5s} {!s:<30s} {} | {:^11s} |'.format(" #","CAT ","ITEM", "IMP", "DUE"))
		print ('+====+' + '='*43 + '+' + '='*13 + '+')
	for num,item in enumerate(data):
		if (settings.important and not check_important(item)) or \
			(duedate is not None and not check_before(item,duedate)) or \
			(len(settings.categories) > 0 and \
				item.category not in settings.categories and not \
				("NONE" in settings.categories and item.category is None)) or \
			(not settings.verbose and not check_past(item)):
				continue
		else:
			printed = True
			print_item(item,num, settings.verbose)
	
		
	if settings.verbose:
		if not printed:
			print ('| {:^73s} |'.format(""))
		print ('+' + '='*75 + '+')
	else:
		if not printed:
			print ('| {:^60s} |'.format(""))
		print ('+' + '='*62 + '+')
	
def do_rm(data, settings):
	settings.indices.sort()
	settings.indices.reverse()
	for element in settings.indices:
		try:
			print ('Removing item', data.pop(element).value)
		except Exception:
			print ('Failed to remove item', element)
	print ("\nResult:")
	do_print(data)
	rewrite(settings.filename, data)
	
def getdata(filename):
	with open(filename, 'rb') as f:
		try:
			return pickle.load(f)
		except Exception:
			return []
			
def print_item(item, num, verbose=False):
	duestr = item.duedate.strftime("%a %d %b") if item.duedate is not None else ""
	imp = '*' if item.important else ' '
	cat = "{!s:>4s}".format(item.category.upper())+':' if item.category is not None else "     "
	
	if verbose:
		stdstr = item.startdate.strftime("%a %d %b") if item.startdate is not None else ""
		dash = " - " if item.startdate is not None and item.duedate is not None else "   "
		print ('| {:2d} |  {} {!s:<30s}  {}  | {:10s}{:3s}{:11s} |'.format(num,cat,item.value[:30], imp, stdstr, dash, duestr))
		for segment in [item.value[i:min(len(item.value),i+28)] for i in range(30,len(item.value),28)]:
			print ('|    |          {!s:<28s}     | {:24s} |'.format(segment," "))
	else:
		print ('| {:2d} |  {} {!s:<30s}  {}  | {:11s} |'.format(num,cat,item.value[:30], imp, duestr))
		for segment in [item.value[i:min(len(item.value),i+28)] for i in range(30,len(item.value),28)]:
			print ('|    |          {!s:<28s}     | {:11s} |'.format(segment," "))
			
def rewrite(filename, data):
	data.sort()
	with open(filename, 'wb') as f:
		pickle.dump(data, f, protocol=0)

def parse():
	"""Parses command-line arguments using argparse and returns an object containing runtime information."""
	parser = argparse.ArgumentParser(description='Allows for basic usage of a to-do list.')
	parser.add_argument('filename', metavar='F', help='A file to be used as a to-do list. Should be newline-separated, with one item per line.')
	subparsers = parser.add_subparsers(help='sub-command help')
	
	parser_add = subparsers.add_parser('add', help='Adds an item to the todo list.')
	parser_add.add_argument('item', nargs='+', help='The item to add.')
	parser_add.add_argument('-i', dest='important', action='store_true', default=False, help='Marks the added argument as important.')
	parser_add.add_argument('-s', dest='start', nargs='+', help='Adds a start date to the added action. Does not print (except if verbose) until that date.')
	parser_add.add_argument('-t', dest='time', nargs='+', help='Adds a due date to the added action.')
	parser_add.set_defaults(func=do_add)
	
	parser_get = subparsers.add_parser('rand', help='Gets and prints a random item from the to-do list. Does not remove it from the list.')
	parser_get.add_argument('-i', dest='important', action='store_true', help='Gets only important items.')
	parser_get.add_argument('-t', dest='time', nargs='+', help='Gets items due before the given date.')
	parser_get.add_argument('-v', dest='verbose', action='store_true', help='Gets items which may not have started yet.')
	parser_get.add_argument('categories', metavar='C', nargs='*', help='Categories within the todo list to get from specifically.')
	parser_get.set_defaults(func=do_get_rand)
	
	parser_stat = subparsers.add_parser('print', help='Prints all items which are visible.')
	parser_stat.add_argument('-i', dest='important', action='store_true', help='Gets only important items.')
	parser_stat.add_argument('-t', dest='time', nargs='+', help='Gets items due before the given date.')
	parser_stat.add_argument('-v', dest='verbose', action='store_true', help='Gets items which may not have started yet.')
	parser_stat.add_argument('categories', metavar='C', nargs='*', help='Categories within the todo list to get from specifically.')
	parser_stat.set_defaults(func=do_print)
	
	parser_rm = subparsers.add_parser('rm', help='Removes an item from the list.')
	parser_rm.add_argument('indices', type=int, nargs='+', help='The indices of items in the list to remove.')
	parser_rm.set_defaults(func=do_rm)
	
	parser_hide = subparsers.add_parser('hide', help='Hides an item from the list for up to one week.')
	parser_hide.add_argument('indices', type=int, nargs='+', help='The indices of items in the list to hide.')
	parser_hide.set_defaults(func=do_hide)
	
	return parser.parse_args()

def main():
	settings = parse()
	if hasattr(settings, 'func'):
		settings.func(getdata(settings.filename), settings)
	else:
		print("Try 'python todo_edit34.py --help'")
main()
