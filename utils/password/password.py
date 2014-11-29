import random,argparse, sys

lows = "qwertyuiopasdfghjklzxcvbnm"
caps = "QWERTYUIOPASDFGHJKLZXCVBNM"
numbers = "1234567890"
specialchars = "`-=[]\;',./<>?:\"{}|~!@#$%^&*()_+"

parser=argparse.ArgumentParser(description="Create a random password")


parser.add_argument("-0", dest="numweight", nargs="?", default=3, const=3, type=int, help="Sets the weight of uppercase letters. Default weight is 3.")
parser.add_argument("-!", dest="specweight", nargs="?", default=0, const=1, type=int, help="Sets the weight of special characters. Default is not to include them.")
parser.add_argument("-a", dest="lowweight", nargs="?", default=5, const=5, type=int, help="Sets the weight of lowercase letters. Default weight is 5.")
parser.add_argument("-A", dest="capweight", nargs="?", default=5, const=5, type=int, help="Sets the weight of uppercase letters. Default weight is 5.")
parser.add_argument("-j", dest="reject", action="store_true", default=False, help="Activates rejection mode, where you press enter to get a new password")
parser.add_argument("-l", dest="length", action="store", default=8, type=int, help="The length of the password to produce. Default is 8.")
parser.add_argument("-p", action="store_true", dest="practice", default=False, help="Turns on practice mode. Exit by typing 'exit'")
parser.add_argument("-r", dest="required", nargs="+", default=[], help="Adds types that are required. Escape types (such as \\a for lowercase), or type strings where any character can satisfy that line. For example, \"-r \\a \\0 \\a\\0 1\" will require one letter, one number, one letter or number, and the digit '1'.")
parser.add_argument("-s", dest="spaceweight", nargs="?", default=0, const=1, type=int, help="Sets the weight of spaces. Default is not to include them.")
parser.add_argument("--nolows", dest="lowweight", action="store_const", const=0, help="Turns off lowercase letters in the password. Shorthand of '-a 0'")
parser.add_argument("--nocaps", dest="capweight", action="store_const", const=0, help="Turns off uppercase letters in the password. Shorthand of '-A 0'")
parser.add_argument("--nonums", dest="numweight", action="store_const", const=0, help="Turns off numbers in the password. Shorthand of '-0 0'")

args = parser.parse_args()

def makestr(str):
	if len(str)==0:
		return ""
	elif str[0]=='\\' and len(str)>1:
		return {
			'a': lows,
			'A': caps,
			'0': numbers*3,
			'!': specialchars,
			'ss': " "*30,
			'\\': "\\"
		}.get(str[1], "") + makestr(str[2:])
	else:
		return str[0]+makestr(str[1:])
		
def randchar(astr):
	if len(astr) == 0:
		return ""
	return random.sample(astr,1)[0]

if args.length < 1:
	print "Length must be 1 or greater."
	sys.exit(1)

str = lows*args.lowweight + caps*args.capweight + numbers*args.numweight*3 + specialchars*args.specweight + " "*args.spaceweight*30

if len(str) == 0:
	print "No characters were allowed!"
	sys.exit(1)

reject = True

while reject:
	reject = False
	password = ""
	for i in range(0,args.length-len(args.required)):
		password += randchar(str)
	password += reduce(lambda a,b: a+b, map(randchar, map(makestr, args.required)), "")
	password = ''.join(random.sample(password,len(password)))

	print password

	if args.reject:
		reject = len(raw_input())==0

if args.practice:
	x = raw_input()
	while(x != "exit"):
		print "\t{}".format(x==password)
		x = raw_input()
