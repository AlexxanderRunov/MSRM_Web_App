from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('samples/<int:sample_id>/', sample),
    path('missions/<int:mission_id>/', mission),
]