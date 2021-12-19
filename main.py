#!/usr/bin/env python3

from greenery import fsm, lego

# alphabet list
# also used as lookup table for number-strings
n = [str(x) for x in range(10)]

# start and end states
s, e = "S", "E"

# get the state name for a position and the current mod-sum
def p(p, n):
	if	p == 0:
		return s
	return str(p) + ":" + str(n)

# list of all states
states = [p(x, y) for x in range(1, 16) for y in range(10)] + [s, e]

# this function handles the odd number case for Luhn's algorithm
def modi(p, n):
	if p % 2 == 0:
		if n > 4:
			return n * 2 - 9
		else:
			return n * 2
	else:
		return n

# generate all state transitions to non-final states
# t is the transition dictionary
#   the keys are the current states
#   the values are dictionaries from the input alphabet
#   value to the next state
t = {}
for _p in range(15):
	for n1 in range(10):
		# _p == 0 is the initial state -> n1 is always 0
		if _p == 0 and n1 > 0:
			continue

		t[p(_p, n1)] = {}
		for n2 in range(10):
			# checks for mastercard 50s range
			if _p == 0 and n2 != 5:
				continue
			if _p == 1 and (n2 == 0 or n2 > 5):
				continue

			t[p(_p, n1)][n[n2]] = p(_p + 1, (n1 + modi(_p, n2)) % 10)

# generate transitions to the final state
for n1 in range(10):
	t[p(15, n1)] = {}
	for n2 in range(10):
		if (n1 + modi(15, n2)) % 10 == 0:
			t[p(15, n1)][n[n2]] = e

# build FSM from alphabet, state set and state transitions
machine = fsm.fsm(
	alphabet = set(n),
	states   = set(states),
	initial  = s,
	finals   = {e},
	map      = t,
)

# hashtag #datadriven tests
tests = [
	# generated valid (https://fake-name-generator.com/Fake-MasterCard-Number-Generator)
	("5222084305213022", True),
	("5223625675778488", True),
	("5306937024627310", True),
	("5406251442761555", True),
	("5216055885117468", True),
	("5197252600542111", True),
	("5549661903610174", True),
	
	("6216055885117468", False), # Luhn check fail
	("5316055885117468", False),
	("5226055885117468", False),
	("5217055885117468", False),
	("5216155885117468", False),
	("5216065885117468", False),
	("5216054885117468", False),
	("5216055985117468", False),
	("5216055875117468", False),
	("5216055886117468", False),
	("5216055885217468", False),
	("5216055885107468", False),
	("5216055885118468", False),
	("5216055885117568", False),
	("5216055885117478", False),
	("5216055885117469", False),
	("4356180747362517", False), # Visa, not Mastercard
]

# Luhn's check for test cases to confirm if they were generated correctly
# only works for mastercard numbers (the visa test will case fail here)
if False:
	for n, r in tests:
		s = 0
		for i, c in enumerate(n):
			s += modi(i, int(c))
		if not (r == (s % 10 == 0)):
			print("test case %s (%s) is invalid: checksum %d" % (n, r, s % 10))
			exit(1)

print("Original FSM:")
print(machine)
print()

print("Reducing...")
machine = machine.reduce()

print("Reduced FSM:")
print(machine)
print()

print("Testing:")
overall = True
for n, r in tests:
	print("Test case %s (%s)" % (n, r))
	if r == machine.accepts(n):
		print("  OK!")
	else:
		print("  FAIL!")
		overall = False
print()

if not overall:
	print("Test suite failed!")
	exit(1)

print("Building regex...")
rex = lego.from_fsm(machine)
print()
print(rex)
