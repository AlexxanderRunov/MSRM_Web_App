from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Sample(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="default.png", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    date_discovery = models.DateField(blank=True)

    def get_image(self):
        return self.image.url.replace("minio", "localhost", 1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Образец"
        verbose_name_plural = "Образцы"
        db_table = "samples"


class Mission(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True,
                              related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True,
                                  related_name='moderator')

    name = models.CharField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Миссия №" + str(self.pk)

    def get_samples(self):
        return [
            setattr(item.sample, "order", item.order) or item.sample
            for item in SampleMission.objects.filter(mission=self)
        ]

    class Meta:
        verbose_name = "Миссия"
        verbose_name_plural = "Миссии"
        ordering = ('-date_formation',)
        db_table = "missions"


class SampleMission(models.Model):
    sample = models.ForeignKey(Sample, models.DO_NOTHING, blank=True, null=True)
    mission = models.ForeignKey(Mission, models.DO_NOTHING, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "sample_mission"
