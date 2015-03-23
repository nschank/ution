import argparse
import datetime
from datetime import datetime, timedelta
from dateutil import parser as dparse
from random import randint
import re
import sys
import time
	
def getdata(filename):
	with open(filename, 'r') as f:
		return [line[:-1] for line in f.readlines()]

def parse():
	"""Parses command-line arguments using argparse and returns an object containing runtime information."""
	parser = argparse.ArgumentParser(description='Allows for basic usage of a to-do list.')

	parser.add_argument('filename', metavar='F', help='A file to be used as a to-do list. Should be newline-separated, with one item per line.')

	parser.add_argument('categories', metavar='C', nargs='*', help='Categories within the todo list to consider specifically.')
	
	parser.add_argument('-i', dest='important', action='store_true', help='Restricts todo to items marked important (with a ! or with a due date within two days).')
	parser.add_argument('-s', dest='start', nargs='+', help='If adding: adds a start date to the added action. Does not print (except if verbose) until that date. Otherwise an error.')
	parser.add_argument('-t', dest='time', nargs='+', help='If adding: adds a due date to the added action. If printing: only prints things due the given day or before. Otherwise an error.')
	parser.add_argument('-v', dest='verbose', action='store_true', help='If adding: adds a due date to the added action. If printing: only prints things due the given day or before. Otherwise an error.')
	
	action_group = parser.add_mutually_exclusive_group()
	action_group.add_argument('-a', dest='add', nargs='+', help='Adds the given item to the to-do list.')
	action_group.add_argument('-g', dest='get', nargs='?', const=-1, type=int, help='Gets and prints the specified item from the to-do list. If no number, a random one. Does not remove it from the list.')
	action_group.add_argument('-h', dest='hide', type=int, help='Hides the given index from the main list.')
	action_group.add_argument('-n', dest='num', action='store_true', help='Gets and prints the number of items on the todo list.')
	action_group.add_argument('-r', dest='rm', type=int, help='Removes the specified item (by index) from the list.')
	
	
	
	return parser.parse_args()
	
def rewrite(filename, data):
	with open(filename, 'w') as f:
		data.sort()
		for line in data:
			f.write(line + "\n")
			
def do_len(data, settings):
	data = [item for item in data if check_after(item,datetime.today())]
	if len(settings.categories) > 0:
		data = [item for item in data if get_category(item) in settings.categories]

	if settings.important:
		if settings.time is not None:
			print ("Warning: Importance and time have undefined union. Importance takes precedence.")
		data = [item for item in data if check_important(item)]
		print ("You have", len(data), "important things to do.")
	elif settings.time:
		duedate = parse_time(settings.time)
		data = [item for item in data if check_before(item, duedate)]
		print ("You have", len(data), "things to do by", duedate.strftime("%A %d %B"))
	else:
		print ("You have", len(data), "things to do.")

def check_important(todo_item):
	return '!' in todo_item or check_before(todo_item, datetime.today()+timedelta(days=2))

def check_after(todo_item, startdate):
	if '<' not in todo_item: return True
	return dparse.parse(re.search(r'<(.*)>', todo_item).group(1)) < startdate

def check_before(todo_item, duedate):
	if '[' not in todo_item: return False
	return dparse.parse(re.search(r'\[(.*)\]', todo_item).group(1)) <= duedate
	
def parse_time(timelist):
	timestr = ' '.join(timelist)
	return dparse.parse(timestr)

def get_category(todo_item):
	if ':' in todo_item:
		return todo_item.partition(':')[0].lower().strip()
	else: return None
	
def do_print(data, settings):
	if settings.important and settings.time is not None:
		print ("Warning: Importance and time have undefined union. Importance takes precedence.")
	elif settings.time is not None:
		duedate = parse_time(settings.time)
		
	for num,item in enumerate(data):
		if settings.important and not check_important(item):
			continue
		elif not settings.important and settings.time is not None and not check_before(item,duedate):
			continue
		elif len(settings.categories) > 0 and get_category(item) not in settings.categories:
			continue
		elif not settings.verbose and not check_after(item,datetime.today()):
			continue
		else:
			print (num, "\t", item)
			
def do_get(data, settings):
	if settings.important or len(settings.categories) > 0 or settings.time is not None:
		print("Warning: Importance, time, and categories do not affect getting a specific item.")
	if settings.get < 0 or settings.get >= len(data):
		print("Error: Invalid index.")
	else:
		print (settings.get, "\t", data[settings.get])
		
def do_get_rand(olddata, settings):
	data = olddata
	if len(settings.categories) > 0:
		data = [item for item in data if get_category(item) in settings.categories]

	if settings.important:
		if settings.time is not None:
			print ("Warning: Importance and time have undefined union. Importance takes precedence.")
		data = [item for item in data if check_important(item)]
	elif settings.time is not None:
		duedate = parse_time(settings.time)
		data = [item for item in data if check_before(item, duedate)]

	if len(data) == 0:
		print ("Error: no items found.")
	else:
		index = randint(0,len(data)-1)
		print (olddata.index(data[index]), "\t", data[index])

def do_add(data, settings):
	if len(settings.categories) > 0:
		print("Warning: Categories are ignored when adding.")
	add = ' '.join(settings.add)
	if settings.important:
		add = add + " ! "
	if settings.time is not None:
		add = add + parse_time(settings.time).strftime("\t[%A %d %B]")
	if settings.start is not None:
		add = add + parse_time(settings.start).strftime("\t<%A %d %B>")
	data.append(add)
	rewrite(settings.filename, data)
	
def do_rm(data, settings):
	if len(settings.categories) > 0:
		print("Warning: Categories are ignored when removing.")
	if settings.important:
		print("Warning: Importance is ignored when removing.")
	if settings.time is not None:
		print("Warning: Time is ignored when removing.")
	if settings.rm < 0 or settings.rm >= len(data):
		print("Error: Removing invalid index.")
	else:
		print("Removing item", data[settings.rm])
		data.pop(settings.rm)
		rewrite(settings.filename, data)

def main():
	settings = parse()
	data = getdata(settings.filename)
	settings.categories = [category.lower() for category in settings.categories]
	
	if settings.num: 			 	# We are getting the length
		do_len(data, settings)
	elif settings.get == -1: 		# We are printing a random value
		do_get_rand(data, settings)
	elif settings.get is not None:	# We are printing a specific value
		do_get(data, settings)
	elif settings.add is not None: 	# We are adding a value
		do_add(data, settings)
	elif settings.rm is not None: 	# We are removing by index
		do_rm(data, settings)
	else:
		do_print(data, settings)

main()
