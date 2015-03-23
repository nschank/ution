import argparse
import random
import sys

def add(filename, datapoint):
	with open(filename, 'a') as f:
		f.write(datapoint + '\n')
	
def aslist(filename):
	with open(filename, 'r') as f:
		return f.readlines()

def parse():
	"""Parses command-line arguments using argparse and returns an object containing runtime information."""
	parser = argparse.ArgumentParser(description='Allows for basic usage of a to-do list.')

	parser.add_argument('listfile', help='A file to be used as a to-do list. Should be newline-separated, with one item per line.')

	action_group = parser.add_mutually_exclusive_group(required=True)
	action_group.add_argument('-a', dest='add', nargs='+', help='Adds the given item to the to-do list.')
	action_group.add_argument('-g', dest='get', nargs='?', const=-1, type=int, help='Gets and prints the specified item from the to-do list. If no number, a random one. Does not remove it from the list.')
	action_group.add_argument('-n', dest='num', action='store_true', help='Gets and prints the number of items on the todo list.')
	action_group.add_argument('-p', dest='pr', action='store_true', help='Prints the entire list')
	action_group.add_argument('-r', dest='rm', type=int, help='Removes the specified item (by index) from the list.')
	action_group.add_argument('--remove', dest='rmi', nargs='+', help='Removes the specified item (by name) from the list. Not the same as -r.')
	
	return parser.parse_args()
	
def rewrite(filename, data):
	with open(filename, 'w') as f:
		for line in data:
			f.write(line)

def main():
	info = parse()
	filename = info.listfile
	listfile = aslist(filename)
	if info.get is not None:
		if info.get == -1:
			print "To do: ", random.choice(listfile)[:-1]
		elif info.get < -1 or info.get >= len(listfile):
			print "List only has", len(listfile), "items."
		else:
			print "To do: ", listfile[info.get][:-1]
	elif info.num:
		print "List has", len(listfile), "items."
	elif info.pr:
		for num,line in enumerate(listfile):
			print num, "-", line[:-1] 
	elif info.rm is not None:
		if info.rm < -1 or info.rm >= len(listfile):
			print "List only has", len(listfile), "items." 
		else:
			print listfile[info.rm][:-1], "removed from list." 
			del listfile[info.rm]
			rewrite(filename,listfile)
	elif info.rmi:
		rem = ' '.join(info.movierm) + '\n'
		if rem in listfile:
			listfile.remove(rem)
			print rem[:-1], "removed from list." 
			rewrite(filename,listfile)
		else:
			print "Could not find ", rem[:-1] 
	elif info.add:
		newitem = ' '.join(info.add)
		print "Adding", newitem
		add(filename, newitem)
	else:
		print "An unknown error occurred!" 
			
			
main()
