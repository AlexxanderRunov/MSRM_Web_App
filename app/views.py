import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from .serializers import *


def get_draft_mission():
    return Mission.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_samples(request):
    sample_name = request.GET.get("sample_name", "")

    samples = Sample.objects.filter(status=1)

    if sample_name:
        samples = samples.filter(name__icontains=sample_name)

    serializer = SamplesSerializer(samples, many=True)
    
    draft_mission = get_draft_mission()

    resp = {
        "samples": serializer.data,
        "samples_count": SampleMission.objects.filter(mission=draft_mission).count() if draft_mission else None,
        "draft_mission": draft_mission.pk if draft_mission else None
    }

    return Response(resp)


@api_view(["GET"])
def get_sample_by_id(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)
    serializer = SampleSerializer(sample)

    return Response(serializer.data)


@api_view(["PUT"])
def update_sample(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    serializer = SampleSerializer(sample, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_sample(request):
    serializer = SampleSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Sample.objects.create(**serializer.validated_data)

    samples = Sample.objects.filter(status=1)
    serializer = SampleSerializer(samples, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_sample(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)
    sample.status = 2
    sample.save()

    samples = Sample.objects.filter(status=1)
    serializer = SampleSerializer(samples, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_sample_to_mission(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    draft_mission = get_draft_mission()

    if draft_mission is None:
        draft_mission = Mission.objects.create()
        draft_mission.owner = get_user()
        draft_mission.date_created = timezone.now()
        draft_mission.save()

    if SampleMission.objects.filter(mission=draft_mission, sample=sample).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = SampleMission.objects.create()
    item.mission = draft_mission
    item.sample = sample
    item.order = SampleMission.objects.count()
    item.save()

    serializer = MissionSerializer(draft_mission)
    return Response(serializer.data["samples"])


@api_view(["POST"])
def update_sample_image(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    image = request.data.get("image")
    if image is not None:
        sample.image = image
        sample.save()

    serializer = SampleSerializer(sample)

    return Response(serializer.data)


@api_view(["GET"])
def search_missions(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    missions = Mission.objects.exclude(status__in=[1, 5])

    if status > 0:
        missions = missions.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        missions = missions.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        missions = missions.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = MissionsSerializer(missions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_mission_by_id(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)
    serializer = MissionSerializer(mission, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_mission(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)
    serializer = MissionSerializer(mission, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)

    if mission.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    mission.status = 2
    mission.date_formation = timezone.now()
    mission.save()

    serializer = MissionSerializer(mission, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    mission = Mission.objects.get(pk=mission_id)

    if mission.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        mission.success = random.randint(0, 1)

    mission.date_complete = timezone.now()
    mission.status = request_status
    mission.moderator = get_moderator()
    mission.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_mission(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)

    if mission.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    mission.status = 5
    mission.save()

    serializer = MissionSerializer(mission, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_sample_from_mission(request, mission_id, sample_id):
    if not SampleMission.objects.filter(mission_id=mission_id, sample_id=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SampleMission.objects.get(mission_id=mission_id, sample_id=sample_id)
    item.delete()

    remaining_items = SampleMission.objects.filter(mission_id=mission_id).order_by('order')
    for index, remaining_item in enumerate(remaining_items):
        remaining_item.order = index + 1
        remaining_item.save()

    data = [
        SampleItemSerializer(item.sample, context={"order": item.order}).data
        for item in remaining_items
    ]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_sample_in_mission(request, mission_id, sample_id):
    if not SampleMission.objects.filter(sample_id=sample_id, mission_id=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SampleMission.objects.get(sample_id=sample_id, mission_id=mission_id)
    current_order = item.order

    # Находим следующий элемент по порядку
    next_item = SampleMission.objects.filter(
        mission_id=mission_id, order=current_order + 1
    ).first()

    if not next_item:
        # Если следующего элемента нет, нельзя увеличить порядок
        return Response({"detail": "Cannot move item further down."}, status=status.HTTP_400_BAD_REQUEST)

    # Используем транзакцию для безопасного изменения данных
    with transaction.atomic():
        # Меняем местами порядки текущего элемента и следующего
        next_item_order = next_item.order
        item.order = next_item_order
        next_item.order = current_order

        item.save()
        next_item.save()

    # Получаем обновленные данные обоих элементов
    updated_items = SampleMission.objects.filter(
        id__in=[item.id, next_item.id]
    ).order_by("order")

    # Сериализуем обновленные элементы
    serialized_data = SampleMissionSerializer(updated_items, many=True).data

    return Response(serialized_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)