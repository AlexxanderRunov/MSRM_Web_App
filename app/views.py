import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_mission(request):
    user = identity_user(request)

    if user is None:
        return None

    mission = Mission.objects.filter(owner=user).filter(status=1).first()

    return mission


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'sample_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_samples(request):
    sample_name = request.GET.get("sample_name", "")

    samples = Sample.objects.filter(status=1)

    if sample_name:
        samples = samples.filter(name__icontains=sample_name)

    serializer = SamplesSerializer(samples, many=True)

    draft_mission = get_draft_mission(request)

    resp = {
        "samples": serializer.data,
        "samples_count": SampleMission.objects.filter(mission=draft_mission).count() if draft_mission else None,
        "draft_mission_id": draft_mission.pk if draft_mission else None
    }

    return Response(resp)


@api_view(["GET"])
def get_sample_by_id(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)
    serializer = SampleSerializer(sample)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=SampleSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_sample(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    serializer = SampleSerializer(sample, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=SampleAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_sample(request):
    serializer = SampleAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Sample.objects.create(**serializer.validated_data)

    samples = Sample.objects.filter(status=1)
    serializer = SamplesSerializer(samples, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_sample(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)
    sample.status = 2
    sample.save()

    sample = Sample.objects.filter(status=1)
    serializer = SampleSerializer(sample, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_sample_to_mission(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    draft_mission = get_draft_mission(request)

    if draft_mission is None:
        draft_mission = Mission.objects.create()
        draft_mission.date_created = timezone.now()
        draft_mission.owner = identity_user(request)
        draft_mission.save()

    if SampleMission.objects.filter(mission=draft_mission, sample=sample).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = SampleMission.objects.create()
    item.mission = draft_mission
    item.sample = sample
    item.save()

    serializer = MissionSerializer(draft_mission)
    return Response(serializer.data["samples"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_sample_image(request, sample_id):
    if not Sample.objects.filter(pk=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    sample = Sample.objects.get(pk=sample_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    sample.image = image
    sample.save()

    serializer = SampleSerializer(sample)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_missions(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    missions = Mission.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        missions = missions.filter(owner=user)

    if status_id > 0:
        missions = missions.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        missions = missions.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        missions = missions.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = MissionsSerializer(missions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_mission_by_id(request, mission_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)

    if not user.is_superuser and mission.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MissionSerializer(mission)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=MissionSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_mission(request, mission_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)
    serializer = MissionSerializer(mission, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, mission_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)

    if mission.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    mission.status = 2
    mission.date_formation = timezone.now()
    mission.save()

    serializer = MissionSerializer(mission)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=UpdateMissionStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
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

    mission.status = request_status
    mission.date_complete = timezone.now()
    mission.moderator = identity_user(request)
    mission.save()

    serializer = MissionSerializer(mission)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_mission(request, mission_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    mission = Mission.objects.get(pk=mission_id)

    if mission.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    mission.status = 5
    mission.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_sample_from_mission(request, mission_id, sample_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SampleMission.objects.filter(mission_id=mission_id, sample_id=sample_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SampleMission.objects.get(mission_id=mission_id, sample_id=sample_id)
    item.delete()

    mission = Mission.objects.get(pk=mission_id)

    serializer = MissionSerializer(mission)
    samples = serializer.data["samples"]

    return Response(samples)


@swagger_auto_schema(method='PUT', request_body=SampleMissionSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_sample_in_mission(request, mission_id, sample_id):
    user = identity_user(request)

    if not Mission.objects.filter(pk=mission_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SampleMission.objects.filter(sample_id=sample_id, mission_id=mission_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SampleMission.objects.get(sample_id=sample_id, mission_id=mission_id)

    serializer = SampleMissionSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
