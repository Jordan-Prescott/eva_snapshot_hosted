from django.urls import re_path
from . import views

urlpatterns = [
    re_path('auth', views.auth_token),
    re_path('eva-snapshot', views.eva_snapshot),
]