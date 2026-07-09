import os
from uuid import uuid4


def profile_image_upload_path(instance, filename):
    """
    Generate upload path for influencer profile images.

    Example:
    profile-images/<influencer_uuid>/profile_<uuid>.jpg
    """

    extension = os.path.splitext(filename)[1].lower()

    return (
        f"profile-images/"
        f"{instance.influencer.influencer_id}/"
        f"profile_{uuid4().hex}{extension}"
    )