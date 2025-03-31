from django.apps import AppConfig


class RemoteCarConfig(AppConfig):
    # the class name attributes refers to the actual app folder name ('remote_car')
    name = 'remote_car'  
    def ready(self):
        from remote_car import views
        views.updata()
        
        from . import mqtt_client
