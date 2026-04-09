from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model to track creation and update timestamps
    Used across all models for auditing & debugging
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True