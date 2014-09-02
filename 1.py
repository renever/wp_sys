
def d(items, key=None):
	seen = set()
	for item in items:
		val = item if key is None else key(item)
		if val not in seen:
			seen.add(val)
			yield item
			
with open('1.txt', 'r') as f:
	for line in d(f):
		print line,
		

