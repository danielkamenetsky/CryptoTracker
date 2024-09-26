from django.contrib import admin
from django.urls import path, include
from contacts import views  # Import your app's views


# This file routes HTTP requests to the appropriate views, which then return templates or handle form submissions.
urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', views.home, name='home'), 
    path('', include('contacts.urls')), 

]