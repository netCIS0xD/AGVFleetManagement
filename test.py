import sys
import socket

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('192.168.1.97',80))
re=client.send("L".encode())
re=client.send("P".encode())
data=client.recv(1024).decode()
print(data)