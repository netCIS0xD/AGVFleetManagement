import threading
import time
from remote_car.models import Car
import socket


class Positions (threading.Thread):
    def run(self):
        for c in Car.objects.all():
            cip=c.car_IP
            x,y = self.callposition(cip)

    def callposition(self,ip):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data=''
        try:
            client.connect((ip, 80))
            re = client.send("GET /Po".encode())
            data = client.recv(1024).decode()
            print(data)
        except:
            print(Exception)
        x = ""
        y = ""
        switch = 0
        for c in data:
            if switch == 0 and c != ',':
                x += c
            elif switch == 1 and c != ',':
                y += c
            elif c == ',':
                switch = 1
        return x, y