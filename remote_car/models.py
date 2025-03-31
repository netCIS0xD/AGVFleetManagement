from django.db import models
from datetime import datetime as dt
from django.utils import timezone

# Create your models here. each class is a table in the database
class Car(models.Model):
    car_id=models.AutoField(primary_key=True)
    car_x=models.IntegerField()
    car_y=models.IntegerField()
    # connection control: 
    #        0 Offline (not to connect) color code (e.g button): dark
    #        1 Online1 (is connecting or connected);  color code (e.g. button): green
    #        2 Conecting (last conecting failed / connection lost, and to re-connect); color code (e.g. button): orange
    car_control=models.IntegerField(default = 0)
    car_IP=models.TextField(default="")
    car_name=models.TextField(default="iCart")
    car_lastTimeConnected=models.TextField(default=dt.now())


class Des(models.Model):
    des_id=models.AutoField(primary_key=True)
    des_name=models.TextField()
    des_description=models.TextField()
    des_x=models.IntegerField()
    des_y=models.IntegerField()
    des_disable=models.IntegerField(default=0)

class SensorReading(models.Model):
    recordID = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now=True)
    AMRID = models.IntegerField(null=True, blank=True)
    AMRState = models.TextField(default="Idle")
    isActive = models.BooleanField(default=False)
    taskID = models.IntegerField(default=None, null=True, blank=True)
    loc_x = models.FloatField(null=True, blank=True)
    loc_y = models.FloatField(null=True, blank=True)
    speed = models.FloatField(default=0, null=True, blank=True) # speed in m/s
    AngOrientation = models.FloatField(default=0, null=True, blank=True) # orientation angle in rad
    current = models.FloatField(null=True, blank=True)
    voltage = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    # dateAdd = models.DateField(auto_now_add=True) #updates to the current date each time the record is saved (not just at creation),
    batterySoC = models.FloatField(default=1, null=True, blank=True)
    
class EnvData(models.Model):
    recordID = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now=True)
    siteID = models.IntegerField(null=True, blank=True) # site may be the workshop, the warehouse
    AMRID = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"{self.timestamp} - Temp: {self.temperature}°C, Volt: {self.voltage}V, Curr: {self.current}mA"
    
    