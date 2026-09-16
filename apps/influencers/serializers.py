from rest_framework import serializers

from apps.influencers.models import (
    BankDetail,
    ExportReport,
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
)
from apps.users.models import User


class SocialMediaSerializer(serializers.Serializer):
    """
    Serializer for social media information during influencer registration.
    """

    platform = serializers.ChoiceField(
        choices=SocialMediaAccount.Platform.choices,
    )

    handle = serializers.CharField(
        max_length=100,
    )

    followers = serializers.IntegerField(
        min_value=0,
    )


class InfluencerRegistrationSerializer(serializers.Serializer):
    """
    Validate influencer registration data.

    The serializer validates request data only.
    Creation of the related User, Influencer, Profile,
    BankDetail, and SocialMediaAccount records is handled
    by InfluencerService.
    """

    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    email = serializers.EmailField()

    full_name = serializers.CharField(
        max_length=100,
    )

    phone = serializers.CharField(
        max_length=15,
    )

    account_number = serializers.CharField(
        max_length=50,
    )

    bank_name = serializers.CharField(
        max_length=100,
    )

    social_media = SocialMediaSerializer(
        many=True,
    )

    def validate_username(self, value: str) -> str:
        """
        Ensure the username is not already registered.
        """

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")

        return value

    def validate_email(self, value: str) -> str:
        """
        Ensure the email address is not already registered.
        """

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")

        return value

    def validate_social_media(self, value):
        """
        Validate that an influencer does not submit
        duplicate social-media platforms.
        """

        platforms = [item["platform"] for item in value]

        if len(platforms) != len(set(platforms)):
            raise serializers.ValidationError(
                "Each social media platform can only be added once."
            )

        return value


class InfluencerListSerializer(serializers.ModelSerializer):
    """
    Serializer for influencer list responses.
    """

    email = serializers.CharField(
        source="user.email",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Influencer
        fields = (
            "id",
            "influencer_id",
            "status",
            "email",
            "username",
            "created_at",
            "approved_at",
        )


class ReportListSerializer(serializers.ModelSerializer):
    """
    Serializer for asynchronous export report responses.
    """

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ExportReport
        fields = (
            "id",
            "report_type",
            "status",
            "created_at",
            "completed_at",
            "file_url",
        )

    def get_file_url(self, obj) -> str | None:
        """
        Return an absolute file URL when a request is available.
        """

        if not obj.file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url


class InfluencerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for influencer profile information.
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
    Serializer for connected social media accounts.
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

        read_only_fields = (
            "id",
            "is_verified",
        )


class BankDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for influencer bank details.
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

        read_only_fields = ("is_verified",)


class MyProfileSerializer(serializers.ModelSerializer):
    """
    Complete influencer profile response.
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

    def get_profile_completion(self, obj):
        """
        Calculate the current profile completion percentage.
        """

        from services.profile_completion_service import (
            ProfileCompletionService,
        )

        return ProfileCompletionService.calculate(obj)

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

        read_only_fields = (
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
    Validate influencer profile updates.
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
        max_length=100,
    )

    state = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    country = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    pincode = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
    )


class UpdateBankSerializer(serializers.Serializer):
    """
    Validate influencer bank-detail updates.
    """

    account_holder_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    account_number = serializers.CharField(
        required=False,
        max_length=50,
    )

    bank_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    ifsc_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )

    upi_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )


class UpdateSocialMediaSerializer(serializers.Serializer):
    """
    Validate social media account updates.
    """

    platform = serializers.ChoiceField(
        choices=SocialMediaAccount.Platform.choices,
    )

    handle = serializers.CharField(
        max_length=100,
    )

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
    Validate complete influencer profile updates.
    """

    profile = UpdateProfileSerializer()

    bank_detail = UpdateBankSerializer(
        required=False,
    )

    social_accounts = UpdateSocialMediaSerializer(
        many=True,
        required=False,
    )
