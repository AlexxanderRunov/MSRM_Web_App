from rest_framework import serializers

from .models import *


class SampleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, sample):
        if sample.image:
            return sample.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Sample
        fields = "__all__"


class SampleItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    def get_image(self, sample):
        if sample.image:
            return sample.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def get_order(self, sample):
        return self.context.get("order")

    class Meta:
        model = Sample
        fields = ("id", "name", "image", "order")


class MissionSerializer(serializers.ModelSerializer):
    samples = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, mission):
        return mission.owner.username

    def get_moderator(self, mission):
        if mission.moderator:
            return mission.moderator.username
            
    def get_samples(self, mission):
        items = SampleMission.objects.filter(mission=mission)
        return [SampleItemSerializer(item.sample, context={"order": item.order}).data for item in items]

    class Meta:
        model = Mission
        fields = '__all__'


class MissionsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, mission):
        return mission.owner.username

    def get_moderator(self, mission):
        if mission.moderator:
            return mission.moderator.username

    class Meta:
        model = Mission
        fields = "__all__"


class SampleMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMission
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
