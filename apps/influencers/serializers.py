from rest_framework import serializers
from apps.users.models import User
from apps.influencers.models import Influencer


class SocialMediaSerializer(serializers.Serializer):
    platform = serializers.CharField()
    handle = serializers.CharField()
    followers = serializers.IntegerField()


class InfluencerRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    # Profile
    full_name = serializers.CharField()
    phone = serializers.CharField()

    # Bank
    account_number = serializers.CharField()
    bank_name = serializers.CharField()

    # Social media (list)
    social_media = SocialMediaSerializer(many=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class InfluencerListSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Influencer
        fields = [
            'id',
            'influencer_id',
            'status',
            'email',
            'username',
            'created_at',
            'approved_at'
        ]