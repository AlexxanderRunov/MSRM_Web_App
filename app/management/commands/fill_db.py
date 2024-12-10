from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_samples():
    Sample.objects.create(
        name="Roubion",
        description="Тип грунта, вероятно, назван в честь одной из местностей на Земле или конкретно в контексте геологии Марса. Вопрос требует дальнейшего уточнения, так как такой термин может не быть общепринятым в литературе.",
        date_discovery=random_date(),
        image="1.png"
    )

    Sample.objects.create(
        name="Montdenier",
        description="Как и в случае с Roubion, Montdenier может быть теоретически определён как тип грунта, но требуется больше контекста для точного понимания. Возможно, это название связано с определённым геологическим формированием или областью на Марсе.",
        date_discovery=random_date(),
        image="2.png"
    )

    Sample.objects.create(
        name="Montagnac",
        description="Скорее всего, данный термин также не является общепринятым в марсианской геологии. В геологии может использоваться для обозначения членств в определённых формациях.",
        date_discovery=random_date(),
        image="3.png"
    )

    Sample.objects.create(
        name="Salette",
        description="Salette может относиться к типу грунта или конкретному географическому объекту на Марсе. Однако, в доступной геологической литературе о Марсе информации об этом типе, как правило, нет",
        date_discovery=random_date(),
        image="4.png"
    )

    Sample.objects.create(
        name="Coulettes",
        description="Согласно контексту, Coulettes может упоминаться как тип грунта, связанный с особенностями марсианского ландшафта или геологии. Однако, уточнение тоже требуется для большей ясности.",
        date_discovery=random_date(),
        image="5.png"
    )

    Sample.objects.create(
        name="Robine",
        description="Похожим образом, Robine может быть упомянутым типом грунта или местностью на Марсе, но без дополнительных данных сложновато предложить определённые характеристики или детали.",
        date_discovery=random_date(),
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_missions():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    samples = Sample.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_mission(status, samples, owner, moderators)

    add_mission(1, samples, users[0], moderators)
    add_mission(2, samples, users[0], moderators)
    add_mission(3, samples, users[0], moderators)
    add_mission(4, samples, users[0], moderators)
    add_mission(5, samples, users[0], moderators)


def add_mission(status, samples, owner, moderators):
    mission = Mission.objects.create()
    mission.status = status

    if status in [3, 4]:
        mission.moderator = random.choice(moderators)
        mission.date_complete = random_date()
        mission.date_formation = mission.date_complete - random_timedelta()
        mission.date_created = mission.date_formation - random_timedelta()
    else:
        mission.date_formation = random_date()
        mission.date_created = mission.date_formation - random_timedelta()

    if status == 3:
        mission.success = random.randint(0, 1)

    mission.name = "MSR-1"

    mission.owner = owner

    i = 1
    for sample in random.sample(list(samples), 3):
        item = SampleMission(
            mission=mission,
            sample=sample,
            order=i
        )
        item.save()
        i += 1

    mission.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_samples()
        add_missions()
