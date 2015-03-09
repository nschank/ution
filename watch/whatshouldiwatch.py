

import argparse
import random
import sys

def add(filename, datapoint):
	with open(filename, 'a') as f:
		print>>f, datapoint
	
def movies(filename):
	with open(filename, 'r') as f:
		return f.readlines()

def parse():
	"""Parses command-line arguments using argparse and returns an object containing runtime information."""
	parser = argparse.ArgumentParser(description='Allows for basic usage of a movie to-watch list.')

	parser.add_argument('movielist', help='A file to be used as a movie to-watch list. Should be newline-separated, with one movie per line.')

	action_group = parser.add_mutually_exclusive_group(required=True)
	action_group.add_argument('-a', dest='moviewr', nargs='+', help='Adds the given movie to the to-watch list.')
	action_group.add_argument('-g', dest='get', action='store_true', help='Gets and prints random movie from the to-watch list. Does not remove it from the list.')
	action_group.add_argument('-r', dest='movierm', nargs='+', help='Removes the given movie from the to-watch list.')
	
	return parser.parse_args()
	
def rewrite(filename, data):
	with open(filename, 'w') as f:
		for line in data:
			print>>f, line[:-1]

def main():
	info = parse()
	filename = info.movielist
	movielist = movies(filename)
	if info.get:
		print "You should watch", random.choice(movielist)[:-1]
	elif info.movierm:
		rem = ' '.join(info.movierm) + '\n'
		if rem in movielist:
			movielist.remove(rem)
			print "Movie", rem[:-1], "removed from list."
			rewrite(filename,movielist)
		else:
			print "Could not find the movie", rem[:-1]
	elif info.moviewr:
		newmovie = ' '.join(info.moviewr)
		print "Adding movie", newmovie 
		add(filename, newmovie)
	else:
		print "An unknown error occurred!"
			
			
main()
