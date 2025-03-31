from django.urls import path,include
import remote_car.views

urlpatterns=[
    path('',remote_car.views.display),
    path('action/<str:act>/<str:cid>/<str:did>/<str:page>/<str:despage>/<str:carselect>/<str:desselect>',remote_car.views.action),
    path('page/<str:page>/<str:despage>/<str:carselect>/<str:desselect>',remote_car.views.displaypage),
    path('refreshposition/<str:id>',remote_car.views.refreshpo),
    path('refreshdes/<str:id>',remote_car.views.refreshdestination),
    # Example URL with car_id as an argument, other inforaiton are in the URL request body in JASON 
    path('api/update_amr_state/<int:car_id>/', remote_car.views.update_AMR_State, name='update_AMR_State'),
    path('history-data/', remote_car.views.history_data, name='history_data'),
    path('sensor_readings', remote_car.views.sensor_readings, name='sensor_readings'),
    
# below are copied from Parsa /sensor_data/urls.py
    # path('', remote_car.views.dashboard, name='dashboard'),
    # path('activate/', remote_car.views.activate_emergency_stop, name='activate'),
    # path('deactivate/', remote_car.views.deactivate_emergency_stop, name='deactivate'),
    # path('sensor-table/', remote_car.views.sensor_table, name='sensor_table'),
    # path('api/sensor-data/', remote_car.views.get_sensor_data, name='get_sensor_data'),  # Add this for the table view
    path('api/latest-sensor-data/', remote_car.views.get_latest_sensor_data, name='urlPatternName_get_latest_sensor_data'),  # Add this for the dashboard
]