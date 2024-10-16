import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234")
    User.objects.create_superuser("root", "root@root.com", "1234")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234")

    print("Пользователи созданы")


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

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_missions():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    samples = Sample.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_mission(status, samples, users, moderators)

    add_mission(1, samples, users, moderators)

    print("Заявки добавлены")


def add_mission(status, samples, users, moderators):
    mission = Mission.objects.create()
    mission.status = status

    if mission.status in [3, 4]:
        mission.date_complete = random_date()
        mission.date_formation = mission.date_complete - random_timedelta()
        mission.date_created = mission.date_formation - random_timedelta()
    else:
        mission.date_formation = random_date()
        mission.date_created = mission.date_formation - random_timedelta()

    mission.owner = random.choice(users)
    mission.moderator = random.choice(moderators)

    mission.name = "MSR-1"
    mission.date = random_date()

    i = 1
    for sample in random.sample(list(samples), 3):
        item = SampleMission(
            mission=mission,
            sample=sample,
            value=i
        )
        item.save()

        i += 1

    mission.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_samples()
        add_missions()



















