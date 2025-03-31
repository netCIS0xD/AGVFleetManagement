from django.contrib import admin
from .models import Car,Des,SensorReading

# Register your models here.
#Register the model to Access the admin interface by running the server
# 
# Visit http://127.0.0.1:8000/admin in your browser.
admin.site.register(Car)
admin.site.register(Des)

admin.site.register(SensorReading)  