import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_search_influencers(
    authenticated_client,
):

    response = authenticated_client.get(
        reverse("influencer-list"),
        {
            "search": "John",
        },
    )

    assert response.status_code == 200

    assert len(response.data["data"]) == 1
