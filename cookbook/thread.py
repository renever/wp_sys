# - * - coding:utf-8 - * -
import threading
#, time
#count = 0
class Thread_Upload(threading.Thread):
    def __init__(self, ftp, file, threadName):
        super(Thread_Upload, self).__init__(name = threadName)
        self.ftp = ftp
        self.file = file
        #self.handle = handle

    def run(self):
        self.ftp.storbinary('STOR ' + self.file.name,\
                            self.file.file,\
                            self.ftp.blocksize,\
                            self.ftp.handle)
        pass

#class Counter(threading.Thread):
    #def __init__(self, lock, threadName):
        #'''''@summary: 初始化对象。

        #@param lock: 琐对象。
        #@param threadName: 线程名称。
        #'''
        #super(Counter, self).__init__(name = threadName)  #注意：一定要显式的调用父类的初始化函数。
        #self.lock = lock

    #def run(self):
        #'''''@summary: 重写父类run方法，在线程启动后执行该方法内的代码。
        #'''
        #global count
        #self.lock.acquire()
        #for i in xrange(1000000):
            #count = count + 1
        #self.lock.release()

#lock = threading.Lock()
#time_start = time.clock()
#for i in range(5):
    #Counter(lock, "thread-" + str(i)).start()
#time.sleep(2)   #确保线程都执行完毕
#time_end = time.clock()
#time_consuming = time_end - time_start
#print "time-consuming: %f " % time_consuming
#print count
