def count(n):
	while True:
	
		yield n
	
		n += 1

c = count(3)
print next(c)
print next(c)
print next(c)
print type(c)
import itertools
for x in itertools.islice(c,10,20):
	print x