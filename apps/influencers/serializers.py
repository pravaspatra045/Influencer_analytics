from rest_framework import serializers
from apps.users.models import User
from apps.influencers.models import Influencer, InfluencerProfile, ExportReport, SocialMediaAccount , BankDetail


class SocialMediaSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(
        choices=SocialMediaAccount.PLATFORM_CHOICES
    )

    handle = serializers.CharField(
        max_length=100
    )

    followers = serializers.IntegerField(
        min_value=0
    )


class InfluencerRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    password = serializers.CharField(
    write_only=True,
    min_length=8,
    style={"input_type": "password"},
)
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


class ReportListSerializer(serializers.ModelSerializer):

    class Meta:

        model = ExportReport

        fields = (
            "id",
            "report_type",
            "status",
            "created_at",
            "completed_at",
            "file",
        )


class InfluencerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for influencer profile.
    """

    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = InfluencerProfile

        fields = (
            "full_name",
            "phone",
            "profile_image",
            "bio",
            "date_of_birth",
            "city",
            "state",
            "country",
            "pincode",
        )
        

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for social media accounts.
    """

    class Meta:
        model = SocialMediaAccount

        fields = (
            "id",
            "platform",
            "handle",
            "profile_url",
            "followers",
            "is_verified",
        )

class BankDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for bank details.
    """

    class Meta:
        model = BankDetail

        fields = (
            "account_holder_name",
            "account_number",
            "bank_name",
            "ifsc_code",
            "upi_id",
            "is_verified",
        )

        read_only_fields = (
            "is_verified",
        )      
class MyProfileSerializer(serializers.ModelSerializer):
    """
    Complete influencer profile serializer.
    """

    profile = InfluencerProfileSerializer(
        read_only=True,
    )

    social_accounts = SocialMediaAccountSerializer(
        many=True,
        read_only=True,
    )

    bank_detail = BankDetailSerializer(
        read_only=True,
    )
    
    profile_completion = serializers.SerializerMethodField()
    
    def get_profile_completion(
        self,
        obj,
    ):
        from services.profile_completion_service import (
            ProfileCompletionService,
        )

        return ProfileCompletionService.calculate(
            obj
        )

    class Meta:
        model = Influencer

        fields = (
            "influencer_id",
            "status",
            "approved_at",
            "rejection_reason",
            "profile",
            "social_accounts",
            "bank_detail",
            "profile_completion",
        )
        
class UpdateProfileSerializer(serializers.Serializer):
    """
    Update influencer profile.
    """

    full_name = serializers.CharField(
        required=False,
        max_length=100,
    )

    phone = serializers.CharField(
        required=False,
        max_length=15,
    )

    bio = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
    )

    city = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    state = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    country = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    pincode = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    
class UpdateBankSerializer(serializers.Serializer):
    """
    Update bank details.
    """

    account_holder_name = serializers.CharField(
        required=False,
    )

    account_number = serializers.CharField(
        required=False,
    )

    bank_name = serializers.CharField(
        required=False,
    )

    ifsc_code = serializers.CharField(
        required=False,
    )

    upi_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class UpdateSocialMediaSerializer(serializers.Serializer):
    """
    Update social media account.
    """

    platform = serializers.ChoiceField(
        choices=SocialMediaAccount.PLATFORM_CHOICES,
    )

    handle = serializers.CharField()

    profile_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    followers = serializers.IntegerField(
        min_value=0,
    )

    is_verified = serializers.BooleanField(
        required=False,
        default=False,
    )
    

class UpdateMyProfileSerializer(serializers.Serializer):
    """
    Complete profile update serializer.
    """

    profile = UpdateProfileSerializer()

    bank_detail = UpdateBankSerializer(
        required=False,
    )

    social_accounts = UpdateSocialMediaSerializer(
        many=True,
        required=False,
    )