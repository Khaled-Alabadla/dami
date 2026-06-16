from django.urls import path

from .views import request_list

urlpatterns = [
    path('', request_list, name='request_list'),
]
