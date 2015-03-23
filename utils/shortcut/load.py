#!python
import xml.etree.ElementTree as ET
from enum import Enum

PROGRAM_XML = "/home/nschank/mini/utils/shortcut/programs.xml"
SHORTCUT_XML = "/home/nschank/mini/utils/shortcut/shortcut.xml"
ALIAS_OUTPUT = "/home/nschank/mini/utils/shortcut/.aliases"

class Alias:
	""" An Alias shortcut which can be run from the command line. """
	alias = None
	pre = ""
	post = ""
	
	def build(self, loc):
		return "alias " + self.alias + "=\"" + self.pre + loc + self.post + "\""
	
	def __init__(self, name):
		self.alias = name

class KeyShortcut:
	""" A key shortcut which can be pressed at any time to run a program. """
	ctrl = False
	shift = False
	alt = False
	letter = None
	
	def __init__(self, xmlNode):
		""" Builds this KeyShortcut using an XML node. """
		letter = xmlNode.text
		for child in xmlNode:
			if "ctrl" == child.tag:
				ctrl = True
			elif "shift" == child.tag:
				shift = True
			elif "alt" == child.tag:
				alt = True
	
	def __str__(self):
		r = ""
		if ctrl:
			r += "Ctrl-"
		if alt:
			r += "Alt-"
		if shift:
			r += "Shift-"
		return r + letter

class Program:
	""" A program which may have an alias, a command, or both. May have one
	name, or many, all of which will be displayed by the command 'halp'.
	Has one location, which should be an absolute, Cygwin path.
	"""
	names = []
	location = ""
	keys = []
	command = ""
	aliases = []
	
	def __init__(self):
		self.names = []
		self.keys = []
		self.aliases = []
		
def build_alias(attribs, alias):
	a = Alias(alias)
	for key,val in attribs.items():
		if key == "pre":
			a.pre = val
		elif key == "post":
			a.post = val
		elif key == "cygstart":
			a.pre = "cygstart "
		elif key == "amp":
			a.post = " &"
	return a
	
def build_program(xml_node):
	""" Uses an XML 'program' node to build a Program object. """
	p = Program()
	for child in xml_node:
		if "name" == child.tag:
			p.names.append(child.text)
		elif "alias" == child.tag:
			p.aliases.append(build_alias(child.attrib, child.text))
		elif "command" == child.tag:
			p.command = child.text
		elif "key" == child.tag:
			p.keys.append(KeyShortcut(child))
		elif "location" == child.tag:
			p.location = child.text
	return p

def build_program_tree():
	""" Use the XML file specified by PROGRAM_XML to build a list of Program
	objects, which will be used to dynamically build the halp command and to
	load aliases.
	"""
	_tree = ET.parse(PROGRAM_XML)
	_root = _tree.getroot()
	
	programs = []
	for node in _root:
		if "program" == node.tag:
			programs.append(build_program(node))
	return programs

def build_shortcut_tree():
	""" Use the XML file specified by SHORTCUT_XML to build a list of
	shortcuts, which will be used to dynamically build the halp command and
	to load aliases.
	"""
	_tree = ET.parse(SHORTCUT_XML)
	_root = _tree.getroot()
	
	shortcuts = []
	for node in _root:
		if "shortcut" == node.tag:
			pr = Program()
			al = Alias(node.attrib["name"])
			al.pre = "cd "
			pr.location = node.text
			pr.aliases.append(al)
			shortcuts.append(pr)
	return shortcuts
	
def main():
	programTree = build_program_tree()
	shortcuts = build_shortcut_tree()
	
	with open(ALIAS_OUTPUT, "wb") as A:
		for program in programTree:
			for alias in program.aliases:
				A.write((alias.build(program.location)+"\n").encode("ascii"))
		for program in shortcuts:
			for alias in program.aliases:
				A.write((alias.build(program.location)+"\n").encode("ascii"))
		
main()