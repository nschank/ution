#python v3.4
from random import sample, shuffle
import argparse
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

def auto_sample_space(settings):
	""" Takes an object containing the settings that the user specified. Returns a string to be used as the 'sample space' for the passwords.
	That is, if a character is sampled uniformly at random from this string,
	it will approximately follow the settings specified by the user in terms
	of how often that character should appear in a created password.
	"""
	return ascii_lowercase*(settings.lowweight) + \
			ascii_uppercase*(settings.capweight) + \
			digits*3*settings.numweight + \
			punctuation*settings.specweight + \
			" "*30*settings.spaceweight

def build_sample_space(str, escaped=False):
	""" Build a sample space string using a string describing how it should
	be built. Return a string which can be sampled uniformly at random to
	satisfy the described character class.
	"""
	if not str:
		return ""
	first_char = str[0]
	if escaped:
		return {"a": ascii_lowercase,
				"A": ascii_uppercase,
				"0": digits,
				"!": punctuation,
				"s": " ",
				"\\": "\\"
				}.get(first_char, "") + build_sample_space(str[1:],False)
	elif first_char == "\\":
		return build_sample_space(str[1:],True)
	else:
		return first_char + build_sample_space(str[1:],False)

def error(id=0):
	""" Print the error statement associated with an error ID. Return the id
	if it is a correct error id.
	"""
	if id == 1:
		print("Cannot create a password of length less than 1.")
	elif id == 2:
		print("No character classes were allowed.")
	elif id == 3:
		print("Too many required character classes.")
	else:
		id = 0
	return id
	
def get_password(settings, sampleSpace, requiredSpaces):
	""" Use the settings object to create a password and display it to the
	user. If rejection is enabled in the setting, waits for the user to 
	accept or reject before returning the created password.
	"""
	normalLength = settings.length - len(requiredSpaces)
	while True:
		required = [sample_with_replacement(space) for space \
					in requiredSpaces]
		normal = list(sample_with_replacement(sampleSpace, normalLength))
		password_list = required + normal
		shuffle(password_list)
		password = ''.join(password_list)
		print(password)
		if (not settings.reject) or input("To accept type anything: "):
			return password
		
def get_settings():
	""" Parse command line flags and arguments to determine user-chosen
	settings. Return an object containing those settings.
	"""
	parser=argparse.ArgumentParser(description="Create a random password")

	parser.add_argument("-0", dest="numweight", nargs="?", default=3, const=3, type=int, help="Sets the weight of uppercase letters. Default weight is 3.")
	parser.add_argument("-!", dest="specweight", nargs="?", default=0, const=1, type=int, help="Sets the weight of special characters. Default is not to include them.")
	parser.add_argument("-a", dest="lowweight", nargs="?", default=5, const=5, type=int, help="Sets the weight of lowercase letters. Default weight is 5.")
	parser.add_argument("-A", dest="capweight", nargs="?", default=5, const=5, type=int, help="Sets the weight of uppercase letters. Default weight is 5.")
	parser.add_argument("-j", dest="reject", action="store_true", default=False, help="Activates rejection mode, where you press enter to get a new password")
	parser.add_argument("-l", dest="length", action="store", default=8, type=int, help="The length of the password to produce. Default is 8.")
	parser.add_argument("-p", action="store_true", dest="practice", default=False, help="Turns on practice mode. Exit by typing 'exit'")
	parser.add_argument("-s", dest="spaceweight", nargs="?", default=0, const=1, type=int, help="Sets the weight of spaces. Default is not to include them.")
	parser.add_argument("--nolows", dest="lowweight", action="store_const", const=0, help="Turns off lowercase letters in the password. Shorthand of '-a 0'")
	parser.add_argument("--nocaps", dest="capweight", action="store_const", const=0, help="Turns off uppercase letters in the password. Shorthand of '-A 0'")
	parser.add_argument("--nonums", dest="numweight", action="store_const", const=0, help="Turns off numbers in the password. Shorthand of '-0 0'")
	parser.add_argument("-r", dest="required", nargs="+", default=[], help="Adds types that are required. Escape types (specifically \\a for lowercase, \\A for uppercase, \\! for special characters, \\0 for digits, and \\s for a space), or type strings where any character can satisfy that line. For example, \"-r \\a \\0 \\a\\0 1\" will require one letter, one number, one letter or number, and the digit '1'.")
	
	return parser.parse_args()
	
def practice(aString):
	""" Allow the user to repeatedly practice typing a given string.
	After each attempt, print whether or not the user correctly typed it.
	Return silently if the user enters 'exit'.
	"""
	attempt = input("Password: ")
	while True:
		print("\t{}".format(attempt == aString))
		if "exit" == attempt:
			break
		attempt = input("Password: ")
		
def sample_with_replacement(space, size=1):
	""" Sample from the given string space. Return a string with the given
	length (size), or the empty string if space is also empty or None. Sample
	with replacement.
	"""
	if not space or size <= 0:
		return ""
	elif size == 1:
		return sample(space, 1)[0]
	else:
		return sample(space, 1)[0] + sample_with_replacement(space, size-1)
	
def main():
	""" Allows the user to create a password based on command line settings.
	"""
	settings = get_settings()
	if settings.length < 1:
		return error(1)
		
	sampleSpace = auto_sample_space(settings)		
	requiredSampleSpaces = [build_sample_space(req) for req \
							in settings.required]
	if len(requiredSampleSpaces) > settings.length:
		return error(3)
	elif len(requiredSampleSpaces) < settings.length and not sampleSpace:
		return error(2)
		
	password = get_password(settings, sampleSpace, requiredSampleSpaces)
	if settings.practice:
		practice(password)
	return 0
	
main()
