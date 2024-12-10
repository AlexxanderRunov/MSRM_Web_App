from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Sample(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    date_discovery = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Образец"
        verbose_name_plural = "Образцы"
        db_table = "samples"
        ordering = ("pk",)


class Mission(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True,  null=True)

    name = models.CharField(blank=True, null=True)
    success = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return "Миссия №" + str(self.pk)

    class Meta:
        verbose_name = "Миссия"
        verbose_name_plural = "Миссии"
        db_table = "missions"
        ordering = ('-date_formation', )


class SampleMission(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.DO_NOTHING, blank=True, null=True)
    mission = models.ForeignKey(Mission, on_delete=models.DO_NOTHING, blank=True, null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "sample_mission"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['sample', 'mission'], name="sample_mission_constraint")
        ]
