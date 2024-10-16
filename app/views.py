from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Sample, Mission, SampleMission


def index(request):
    sample_name = request.GET.get("sample_name", "")
    samples = Sample.objects.filter(status=1)

    if sample_name:
        samples = samples.filter(name__icontains=sample_name)

    draft_mission = get_draft_mission()

    context = {
        "sample_name": sample_name,
        "samples": samples
    }

    if draft_mission:
        context["samples_count"] = len(draft_mission.get_samples())
        context["draft_mission"] = draft_mission

    return render(request, "samples_page.html", context)


def add_sample_to_draft_mission(request, sample_id):
    sample = Sample.objects.get(pk=sample_id)

    draft_mission = get_draft_mission()

    if draft_mission is None:
        draft_mission = Mission.objects.create()
        draft_mission.owner = get_current_user()
        draft_mission.date_created = timezone.now()
        draft_mission.save()

    if SampleMission.objects.filter(mission=draft_mission, sample=sample).exists():
        return redirect("/")

    item = SampleMission(
        mission=draft_mission,
        sample=sample
    )
    item.save()

    return redirect("/")


def sample_details(request, sample_id):
    context = {
        "sample": Sample.objects.get(id=sample_id)
    }

    return render(request, "sample_page.html", context)


def delete_mission(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE missions SET status=5 WHERE id = %s", [mission_id])

    return redirect("/")


def mission(request, mission_id):
    if not Mission.objects.filter(pk=mission_id).exists():
        return redirect("/")

    mission = Mission.objects.get(id=mission_id)
    if mission.status == 5:
        return redirect("/")

    context = {
        "mission": mission,
    }

    return render(request, "mission_page.html", context)


def get_draft_mission():
    return Mission.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()