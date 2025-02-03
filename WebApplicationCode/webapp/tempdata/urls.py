from .views import *
from django.urls import path

urlpatterns = [
	path('' , login_page),
    path('login/', login, name='login'),    
    path('prediction/', pred_page, name='prediction'),
    path('index/', index, name='index'),
	
] 
