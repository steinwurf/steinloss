import csv
import time
from datetime import datetime
from socket import *
from threading import Thread, Lock
from typing import Optional, Callable, Any, Iterable, Mapping


class Counter(object):
	def __init__(self):
		# RawValue because we don't need it to create a Lock:
		self.val = 0
		self.lock = Lock()

	def increment(self):
		with self.lock:
			self.val += 1

	def value(self):
		with self.lock:
			return self.val


_FINISH = False


def receiver(counter):
	number_of_bytes_2_get = 1024
	destination_address = ("127.0.0.1", 7070)
	client_socket = socket(AF_INET, SOCK_DGRAM)
	client_socket.sendto("HIT ME".encode(), destination_address)
	oldtime = time.time()
	while True:
		received_request = client_socket.recv(number_of_bytes_2_get)
		if _FINISH:
			break
		counter.increment()


def poster(counter):
	oldtime = time.time()
	while True:
		if _FINISH:
			break
		val = counter.value()
		with open('client_stats.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([val])
		time.sleep(0.5)


def run():
	counter = Counter()
	with open('client_stats.csv', 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(["packets"])
	global _FINISH
	poster_thread = Thread(target=poster, args=(counter,))
	receiver_thread = Thread(target=receiver, args=(counter,))
	timer_thread = Thread()

	receiver_thread.start()
	poster_thread.start()
	time.sleep(15)
	_FINISH = True
	poster_thread.join()
	receiver_thread.join()
	print("main process exiting")
# with open('client.csv', 'a') as file:
#	result = "%d,\n" % self.packets_received
#	file.writelines(result)
