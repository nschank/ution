

import argparse
import random
import sys

def add(filename, datapoint):
	with open(filename, 'a') as f:
		print>>f, datapoint
	
def aslist(filename):
	with open(filename, 'r') as f:
		return f.readlines()

def parse():
	"""Parses command-line arguments using argparse and returns an object containing runtime information."""
	parser = argparse.ArgumentParser(description='Allows for basic usage of a to-do list.')

	parser.add_argument('listfile', help='A file to be used as a to-do list. Should be newline-separated, with one item per line.')

	action_group = parser.add_mutually_exclusive_group(required=True)
	action_group.add_argument('-a', dest='add', nargs='+', help='Adds the given item to the to-do list.')
	action_group.add_argument('-g', dest='get', action='store_true', help='Gets and prints a random item from the to-do list. Does not remove it from the list.')
	action_group.add_argument('-r', dest='rm', nargs='+', help='Removes the given item from the to-watch list.')
	action_group.add_argument('-t', dest='top', action='store_true', help='Returns the top item on the list.')
	action_group.add_argument('-u', dest='toprm', action='store_true', help='Removes the top of the list.')
	
	return parser.parse_args()
	
def rewrite(filename, data):
	with open(filename, 'w') as f:
		for line in data:
			print>>f, line[:-1]

def main():
	info = parse()
	filename = info.listfile
	listfile = aslist(filename)
	if info.get:
		print "To do: ", random.choice(listfile)[:-1]
	elif info.rm:
		rem = ' '.join(info.movierm) + '\n'
		if rem in listfile:
			listfile.remove(rem)
			print rem[:-1], "removed from list."
			rewrite(filename,listfile)
		else:
			print "Could not find ", rem[:-1]
	elif info.add:
		newitem = ' '.join(info.add)
		print "Adding ", newitem
		add(filename, newitem)
	elif info.top:
		print listfile[0][:-1]
	elif info.toprm:
		print listfile[0][:-1], "removed from list."
		listfile.remove(listfile[0])
		rewrite(filename,listfile)
	else:
		print "An unknown error occurred!"
			
			
main()
