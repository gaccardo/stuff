import sys
import os

counter = -1
f = open('access_generated.log')

lines = list()
line = ""

os.lseek(f.fileno(), counter, 2)

for i in range(1000000):

	char = os.read(f.fileno(), 1)
	counter -= 1
	line = "%s%s" % (char, line)

	if char == "\n":
		lines.append(line)
		line = ""

	try:
		os.lseek(f.fileno(), counter, 2)
	except OSError:
		break

for line in lines:
	print "%s" % line.split('\n')[1]
