import time
import os
from multiprocessing import Process
import threading
'''
利用multiprocess模块的Pool类创建多进程

很多时候系统都需要创建多个进程以提高CPU的利用率，当数量较少时，可以手动生成一个个
Process实例。当进程数量很多时，或许可以利用循环，但是这需要程序员手动管理系统中并发进
程的数量，有时会很麻烦。这时进程池Pool就可以发挥其功效了。可以通过传递参数限制并发进
程的数量，默认值为CPU的核数。

Pool类可以提供指定数量的进程供用户调用，当有新的请求提交到Pool中时，如果进程池还没有
满，就会创建一个新的进程来执行请求。如果池满，请求就会告知先等待，直到池中有进程结束，
才会创建新的进程来执行这些请求。

apply_async(),向进程池中提交需要执行的函数及参数,各进程采用非阻塞(异步)形式,每个进程
只管运行自身的任务,默认方式

close(),关闭进程池Pool,不接受新任务

terminate(),结束工作进程,不再处理未处理任务

join(),父进程阻塞等待子进程的退出,也就是在所有子进程运行结束后,父进程才会退出,join
()要在close()/terminate()之后调用




'''
def long_time_task(i):
	while True:
	    print('子进程: {} - 任务{}'.format(os.getpid(), i))
	    print("结果: {} {}".format(8 ** 20,i))
	    time.sleep(i)

def test(h):
	print('这是主线程：{}'.format(threading.current_thread().name))
	thread_list = []
	for i in range(4, 6):
		t = threading.Thread(target=long_time_task, args=(i, ))
		thread_list.append(t)

	for t in thread_list:
		t.start()

	for t in thread_list:
		t.join()

if __name__ == '__main__':
	print('当前母进程: {}'.format(os.getpid()))
	# start = time.time()
	p1 = Process(target=long_time_task, args=(1,))
	p2 = Process(target=long_time_task, args=(2,))
	p3 = Process(target=test, args=(3,))

	p1.start()
	p2.start()
	p3.start()

	# 阻塞母进程,计算耗时
	# p1.join()
	# p2.join()
	# p3.join()

	# end = time.time()
	# print("总共用时{}秒".format((end - start)))