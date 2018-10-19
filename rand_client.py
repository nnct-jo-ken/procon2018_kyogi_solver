import socket
import random

def Tsend():
	buf = ""
	num = 0
	while num < 2:
		buf += str(random.randint(-1, 1))
		buf += ' '
		buf += str(random.randint(-1, 1))
		buf += ':'
		buf += '0'
		buf += ':'
		num += 1
	return buf

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket1:
	socket1.connect(("127.0.0.1", 12346))

	while True:
        # タイルの点数受信
		buff1 = socket1.recv(512)
        # タイミング合わせ
		socket1.send(b'end')
        # 
		buff2 = socket1.recv(512)

		print(buff1)
		print(buff2)

		buffer = Tsend()
		print(buffer);
		socket1.send(buffer.encode('utf-8'))
