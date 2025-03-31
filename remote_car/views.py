from django.shortcuts import render,redirect
from django.http import HttpResponse
from remote_car.models import Car,Des
from datetime import datetime


import socket
import time
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache
from remote_car.thread import Positions
import random

# MQTT codes copied from parsa
from .models import SensorReading, EnvData
import paho.mqtt.publish as publish
from django.http import JsonResponse

ACCEPTABLE_DATETIME_FORMAT = [
        '%d/%m/%Y %H:%M:%S',  # e.g., 31/12/2025 23:59:59
        '%d/%m/%Y %H:%M:%S.%f',  # e.g., 31/12/2025 23:59:59.596751
        '%Y-%m-%d %H:%M:%S',  # e.g., 2025-12-31 23:59:59
        '%Y-%m-%d %H:%M:%S.%f', # e.g 2022-11-12 21:02:47.596752
        # Add more formats here if needed
    ]

# define the datetime string format to be used in this program
MY_DATETIME_FORMAT ="%Y-%m-%d %H:%M:%S"


MQTT_BROKER = 'broker.hivemq.com' # 192.168.9.126
LED_TOPIC = 'led/control'

import json

print("**** view.py starts ****")
print("     Initial global variables ")

# global variables
# Fetch the number of AMRs dynamically
numAMR = Car.objects.count()
AMRActState = [0] * numAMR  # Initialize all states to 0 ("Inactive")

allAMRs = Car.objects.all()  # Get all cars from the Car model

print("    List all AMRs (allAMRs) retrieved from model class Car (a database table)")
for index, amr in enumerate(allAMRs):
    print(f"   Index: {index}, AMR ID: {amr.car_id}, AMR Name: {amr.car_name}, AMR IP: {amr.car_IP}")


def toggle_AMR_state(request):
    global AMRActState
    if request.method == "POST":
        # Get the car ID from the POST request
        car_id = int(request.POST.get("car_id"))

        # Toggle the state for the specific car
        AGVActState[car_id] = 1 if AGVActState[car_id] == 0 else 0

        print(f"Car {car_id} state changed to: {AGVActState[car_id]}")  # Debugging log

        # Return the updated state as a JSON response
        return JsonResponse({"car_id": car_id, "state": AGVActState[car_id]})

    # Default response for non-POST requests
    return JsonResponse({"error": "Invalid request method"}, status=400)


# Create your views here.
def display(request):
    maxpage=(Car.objects.all().count()//5)
    if(Car.objects.all().count()%5==0):
        maxpage = (Car.objects.all().count() / 5)-1
    cars2display=[]
    des2display=[]
    for i in range(5):
        try:
            cars2display.append(Car.objects.all()[i])
        except:
            break

    maxdespage=(Des.objects.all().count()//5)
    if(Des.objects.all().count()%5==0):
        maxdespage = (Des.objects.all().count() / 5)-1
    for i in range(5):
        try:
            des2display.append(Des.objects.all()[i])
        except:
            break
    
    # reading data from database (table: SensorReading)
    readings = SensorReading.objects.all().order_by('-timestamp')[:100]
    
    # display html webpage
    return render(request, 'controlPanel.html', {
        'cap': cars2display,
        'dep':des2display,
        'pagenumber':0,
        'despagenumber':0,
        'maxpage':maxpage,
        'maxdespage':maxdespage,
        'carselectd':'NA',
        'desselected':'NA'
    })
        # 'readings':readings #Parsa's MQTT reading

def displaypage(request,page,despage,carselect,desselect):
    maxpage=(Car.objects.all().count()//5)
    if(Car.objects.all().count()%5==0):
        maxpage = (Car.objects.all().count() / 5)-1
    cars2display=[]
    for i in range(int(page)*5,int(page)*5+5):
        try:
            cars2display.append(Car.objects.all()[i])
        except:
            break

    maxdespage=(Des.objects.all().count()//5)
    if(Des.objects.all().count()%5==0):
        maxdespage = (Des.object.all().count() // 5)-1
    des2display=[]
    for i in range(int(despage)*5,int(despage)*5+5):
        try:
            des2display.append(Des.objects.all()[i])
        except:
            break
    # reading data from database (table: SensorReading)
    readings = SensorReading.objects.all().order_by('-timestamp')[:100]
    
    return render(request, 'controlPanel.html', {
        'cap': cars2display,
        'dep':des2display,
        'pagenumber':int(page),
        'despagenumber':int(despage),
        'maxpage':maxpage,
        'maxdespage':maxdespage,
        'carselectd': carselect,
        'desselected': desselect,
         'readings':readings  # Parsa's MQTT reading
    })


def action(request,act,cid,did,page,despage,carselect,desselect):
    message=""
    ip=""
    ca=Car()
    for c in Car.objects.all():
        if str(c.car_id)==cid: # find the object car with the id = cid
            ip=c.car_IP
            ca=c
            break
    dest=Des()
    for d in Des.objects.all():
        if str(d.des_id)==did:
            dest=d
            break
    print('SEND AVG ',cid,'(',ip,') to ',dest.des_name)

    if act=='go':
        if ca.car_control!=1:
            message='AVG_not_valid (connection to the car is lost)'
        elif dest.des_disable==1:
            message='Destination_not_valid'
        else:
            connectStartTime=datetime.now()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket
            try:
                print("to connect the server at "+ip)
                client.connect((ip, 80))  # create a new connection to the server
                print(" and send "+"\"GO,"+did+",iCart\"")
                re=client.send(("GO,"+did+",iCart").encode())  # send letter A
                xi=0
                while (datetime.now()-connectStartTime).total_seconds() < 5:
                    # wait 5 sec for the TCP communicaiton finish
                    xi=xi+1
                print(".... done.")
            except Exception as e:
                 print(e)
    elif act=='stop':
        if message == "":
            message += cid+'_Stopped'
        connectStartTime=datetime.now()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("to connect the server at "+ip)
            client.connect((ip, 80))
            print(" and send "+"\"STOP\"")
            re=client.send("STOP".encode())
            xi=0
            while (datetime.now()-connectStartTime).total_seconds() < 5:
                # wait 5 sec for the TCP communicaiton finish
                xi=xi+1
            print(".... done.")
        except Exception as e:
            print("DXW ERR")
            print(e)



    maxpage = (Car.objects.all().count() // 5)
    if (Car.objects.all().count() % 5 == 0):
        maxpage = (Car.objects.all().count() / 5) - 1
    cars2display = []
    for i in range(int(page) * 5, int(page) * 5 + 5):
        try:
            cars2display.append(Car.objects.all()[i])
        except:
            break
    maxdespage=(Des.objects.all().count()//5)
    if(Des.objects.all().count()%5==0):
        maxdespage = (Des.object.all().count() // 5)-1
    des2display=[]
    for i in range(int(despage)*5,int(despage)*5+5):
        try:
            des2display.append(Des.objects.all()[i])
        except:
            break

    return render(request, 'controlPanel.html', {
        'cap': cars2display,
        'dep':des2display,
        'pagenumber':int(page),
        'despagenumber':int(despage),
        'maxpage':maxpage,
        'maxdespage':maxdespage,
        'carselectd': carselect,
        'desselected': desselect,
        'message':message
    })

def dataupdate():
    for c in Car.objects.all():
        # time.sleep(60)
        print(' *[',datetime.now(),'] to update position of iCart (',c.car_id,')')
        x,y=updateposition(c,c.car_IP)
        print( '          .... the updated postion is [x=',x,' y=',y,']')
        # print(' *[',datetime.now(),'] updated position of iCart (',c.car_id,') with [x=',x,' y=',y,']')
        if x!='':
            c.car_x=int(x)
        else:
            print(' invlide x')

        if y!='':
            c.car_y=int(y)
        else:
            print(' invlide y')
        print("")
        c.save()


def updata():
    scheduler=BackgroundScheduler(job_defaults={'max_instances': 200})
    scheduler.add_job(dataupdate,'interval',seconds=60)
    scheduler.start()

def updateposition(objAMR,ip):
    global MY_DATETIME_FORMAT

    x=''
    y=''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(3)  # Timeout in seconds
    try:
        if objAMR.car_control == 0: 
            # the AMR is offline (and not to connect)
            print(" Skip connecting AMR", {objAMR.car_name}," (IP="+ip, "), as it onlineState is set to OFF (0)")
            x = 0  # use the default orgin address to indicate Offfline
            y = 0
            return x,y

        print("to connect", {objAMR.car_name}," AMR's  server at IP= "+ip)
        client.connect((ip, 80)) # The connect call is blocking by default. 
        print("  send getPOS to the web server at AMR ()", {objAMR.car_name}," at IP= "+ip+")")

        re = client.send("getPOS".encode())
        data=client.recv(1024).decode()
        print("received data: "+data)
        # print(data)
        # received data format: "x,y"
        client.close()
        if data is not None:
            switch = 0
            for cc in data:  # cc is a single letter
                if switch==0 and cc !=',':
                    x+=cc
                elif switch==1 and cc!=',':
                    y+=cc
                elif cc==',':
                    switch=1

        objAMR.car_control=1 # update the car status to 1 (online)
        print("    set ", {objAMR.car_name},"'s control to 1 (online)")
        objAMR.car_lastTimeConnected=datetime.now().strftime(MY_DATETIME_FORMAT) #record the current time as the last connected time
        objAMR.save()  # save to the SQLlight database

    except Exception as e:
        print(e)
        print("     AMR ",{objAMR.car_name},"Last time connected: ",{objAMR.car_lastTimeConnected},"online state control =", {objAMR.car_control})
        if objAMR.car_control==1:  # if the car was connected, but now in exception, 
            objAMR.car_control=2   # change connection status to Online2 (connection is lost, and try to connect)
            objAMR.save()
            print("  change state to 2")

            # else if the car's connection was lost for 120 sec, and still get an exception, 
            # change to state 0 (connection is lost, and still try to connect)
       
        # UK time format
        # elif objAMR.car_control==2 and (datetime.now()-datetime.strptime(objAMR.car_lastTimeConnected, '%d/%m/%Y %H:%M:%S')).total_seconds() > 120:
        
        # CHN time format
        elif objAMR.car_control==2:
            time_now = datetime.now()

            last_connected = strDT2datetime(objAMR.car_lastTimeConnected)
            # try:
            #     last_connected = datetime.strptime(objAMR.car_lastTimeConnected, '%d/%m/%Y %H:%M:%S.%f')
            # except ValueError:
            #    last_connected = datetime.strptime(objAMR.car_lastTimeConnected, '%d/%m/%Y %H:%M:%S')
            print("last connected on ", last_connected)
            
           # try:
           #     last_connected = datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S.%f')
           # except ValueError:
           #     last_connected = datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
                                            
            time_diff = (time_now - last_connected).total_seconds()
            if time_diff > 120:
                print(" has been lost over 120 sec, set to OFFLINE (onlineState =0)")
                objAMR.car_control=0  
                objAMR.save()

    return x,y


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Exempt CSRF validation for testing (make sure to use proper CSRF handling for production)
def update_AMR_State(request, car_id):
    if request.method == 'POST':
        print("  update_AMR_State(): the received request is ", request)
        try:
            # Parse the JSON body of the request
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            # Get the 'new_onlinestate' from the JSON data
            new_onlinestate = body_data.get('new_onlinestate')

            # # Get the 'new_onlinestate' from the JSON body of the request
            # new_onlinestate = request.POST.get('new_onlinestate')

            print("new_onlinestate is ", new_onlinestate)
            if new_onlinestate is not None:
                new_onlinestate = int(new_onlinestate)  # Convert to integer

                # Find the car by its car_id
                car = Car.objects.get(car_id=car_id)

                # Update the car's state (assuming car_control is the field you're updating)
                car.car_control = new_onlinestate
                car.save()

                return JsonResponse({'status': 'success', 'new_onlinestate': new_onlinestate})

            return JsonResponse({'status': 'error', 'message': 'Invalid state value'})

        except Car.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Car not found'})
        except Exception as e:
            print('JsonResponse Exception:',e)
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def refreshpo(request,id):
    ca=Car()
    for c in Car.objects.all():
        if str(c.car_id)==id:
            ca=c
    x=ca.car_x
    y=ca.car_y
    # no comma between the online status (car_control) and position x,y
    # this is due to the html javascript function that process the httpResponse
    # where  data.slice(1,) for the control and data.slice(1,) means 
    success = str(ca.car_control)+','+str(x)+','+str(y) 
    # success = str(ca.car_control)+','+str(x)+','+str(y)
    return HttpResponse(success)

def refreshdestination(request,id):
    de=Des()
    for d in Des.objects.all():
        if str(d.des_id)==id:
            de=d
    return HttpResponse(de.des_disable)

# codes copief from Parsa
def get_latest_sensor_data(request):
    global MY_DATETIME_FORMAT

    # Return the latest sensor data as JSON.
    latest_reading = SensorReading.objects.all().order_by('-timestamp').first()
    if latest_reading:
        data = {
            "timestamp": latest_reading.timestamp.strftime(MY_DATETIME_FORMAT),
            "temperature": latest_reading.temperature,
            "voltage": latest_reading.voltage,
            "current": latest_reading.current,
        }
    else:
        data = {"temperature": None, "voltage": None, "current": None}
    return JsonResponse(data)



def strDT2datetime(datetime_str):
    # Define the potential formats

    global ACCEPTABLE_DATETIME_FORMAT
    for fmt in ACCEPTABLE_DATETIME_FORMAT:
        try:
            # Try parsing the datetime string with the current format
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            # If parsing fails, try the next format
            continue

    # If none of the formats work, raise an error or return None
    raise ValueError(f"Unable to parse datetime string: {datetime_str}")


"""     def history_data(request):
        readings = SensorReading.objects.all().order_by('-timestamp')
        return render(request, 'historydata.html', {'readings': readings}) """

from django.core.serializers import serialize
from django.shortcuts import render
from .models import SensorReading

def history_data(request):
    readings = SensorReading.objects.all().order_by('-timestamp')
    serialized_readings = serialize('json', readings, fields=('timestamp', 'temperature', 'voltage', 'current','humidity'))
    print(serialized_readings)
    return render(request, 'historydata.html', {'readings': readings, 'readings_json': serialized_readings})


def sensor_readings(request):
    start_dateStr = request.GET.get('start_date')
    end_dateStr = request.GET.get('end_date')
    if not start_dateStr or not end_dateStr:
    # the start and end date is not specified, Query all the SensorReading model data
        readings = SensorReading.objects.all().order_by('-timestamp') 
        envData = EnvData.objects.all().order_by('-timestamp')
        # print(readings)
        serialized_readings = serialize('json', readings, fields=('timestamp', 'temperature', 'voltage', 'current','humidity'))
        print("All data quried and to be returned in JSON ", serialized_readings)
        responseRender = {'readings': readings, 'envData':envData, 'readings_json': serialized_readings}
        # return render(request, 'historydata.html', )
    else:
        # Convert the start_date and end_date strings to datetime objects   
        start_date = datetime.strptime(start_dateStr, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_dateStr, '%Y-%m-%d').date()
        # Query the SensorReading model with the specified date range
        readings = SensorReading.objects.filter(timestamp__date__range=(start_date, end_date)).order_by('-timestamp')
        # print(readings)
        envData = EnvData.objects.filter(timestamp__date__range=(start_date, end_date)).order_by('-timestamp')
        
        serialized_readings = serialize('json', readings, fields=('timestamp', 'temperature', 'voltage', 'current','humidity'))
        
        print("Quried data to be returned in JSON ", serialized_readings)
        responseRender = {'readings': readings, 'envData': envData, 'startDateServer': start_dateStr, 'endDateServer': end_dateStr, 'readings_json': serialized_readings}

    return render(request, 'historydata.html', responseRender)
