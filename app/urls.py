from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('samples/<int:sample_id>/', sample_details, name="sample_details"),
    path('samples/<int:sample_id>/add_to_mission/', add_sample_to_draft_mission, name="add_sample_to_draft_mission"),
    path('missions/<int:mission_id>/delete/', delete_mission, name="delete_mission"),
    path('missions/<int:mission_id>/', mission)
]
