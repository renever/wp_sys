d = {'a':1, 'b':2, 'c':3}

class obj:

    def __init__(self):
        pass
a = obj()

for key,value in d.items():
    setattr(a,key,value)

print a.c
