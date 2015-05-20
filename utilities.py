## Required for try-except-else Error Catching
import sys


## Get the latest (last) value of a series (list) of values
def getLast(mylist):
	try:
		last = mylist[-1]
	except:
		last = 0

	return last

## Get the next latest (next last) value of a series (list) of values
def getNextLast(mylist):
	try:
		nextLast = mylist[-2]
	except:
		nextLast = 0

	return nextLast

## Calculate the conductance, perform a division-by-zero check
def calculateConductance(I,V):
	try:
		return float(I)/float(V)
	except:
		return 0
