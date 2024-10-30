from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/samples/', search_samples),  # GET
    path('api/samples/<int:sample_id>/', get_sample_by_id),  # GET
    path('api/samples/<int:sample_id>/update/', update_sample),  # PUT
    path('api/samples/<int:sample_id>/update_image/', update_sample_image),  # POST
    path('api/samples/<int:sample_id>/delete/', delete_sample),  # DELETE
    path('api/samples/create/', create_sample),  # POST
    path('api/samples/<int:sample_id>/add_to_mission/', add_sample_to_mission),  # POST

    # Набор методов для заявок
    path('api/missions/', search_missions),  # GET
    path('api/missions/<int:mission_id>/', get_mission_by_id),  # GET
    path('api/missions/<int:mission_id>/update/', update_mission),  # PUT
    path('api/missions/<int:mission_id>/update_status_user/', update_status_user),  # PUT
    path('api/missions/<int:mission_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/missions/<int:mission_id>/delete/', delete_mission),  # DELETE

    # Набор методов для м-м
    path('api/missions/<int:mission_id>/update_sample/<int:sample_id>/', update_sample_in_mission),  # PUT
    path('api/missions/<int:mission_id>/delete_sample/<int:sample_id>/', delete_sample_from_mission),  # DELETE

    # Набор методов пользователей
    path('api/users/register/', register), # POST
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
    path('api/users/<int:user_id>/update/', update_user) # PUT
]
