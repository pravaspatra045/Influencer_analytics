from django.contrib import admin
from .models import (
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
    BankDetail,
)

admin.site.register(Influencer)
admin.site.register(InfluencerProfile)
admin.site.register(SocialMediaAccount)
admin.site.register(BankDetail)
