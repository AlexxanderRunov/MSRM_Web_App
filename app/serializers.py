from rest_framework import serializers

from .models import *


class SamplesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, sample):
        if sample.image:
            return sample.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Sample
        fields = ("id", "name", "status", "date_discovery", "image")


class SampleSerializer(SamplesSerializer):
    class Meta:
        model = Sample
        fields = "__all__"


class SampleAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ("name", "description", "date_discovery", "image")


class MissionsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Mission
        fields = "__all__"


class MissionSerializer(MissionsSerializer):
    samples = serializers.SerializerMethodField()

    def get_samples(self, mission):
        items = SampleMission.objects.filter(mission=mission)
        return [SampleItemSerializer(item.sample, context={"order": item.order}).data for item in items]


class SampleItemSerializer(SampleSerializer):
    order = serializers.SerializerMethodField()

    def get_order(self, _):
        return self.context.get("order")

    class Meta:
        model = Sample
        fields = ("id", "name", "status", "date_discovery", "image", "order")


class SampleMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMission
        fields = "__all__"


class UpdateMissionStatusAdminSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


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


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
