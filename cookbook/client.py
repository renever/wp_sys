from procedure_calls import RPCProxy
from multiprocessing.connection import Client
c = Client(('localhost', 17000), authkey=b'peekaboo')
proxy = RPCProxy(c)
x = proxy.add(2, 3)
print x