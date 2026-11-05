import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from .models import TrainEvent


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_events(db):
    now = timezone.now()
    data = [
        ("6205", "Marseille Saint-Charles", 0, False),
        ("6207", "Lyon Part-Dieu", 35, False),
        ("6209", "Paris Gare de Lyon", 0, True),
        ("6211", "Avignon TGV", 5, False),
    ]
    for num, station, delay, cancelled in data:
        TrainEvent.objects.create(
            train_number=num,
            station=station,
            scheduled_at=now,
            delay_minutes=delay,
            is_cancelled=cancelled,
        )


@pytest.mark.django_db
def test_create_event(api_client):
    payload = {
        "train_number": "6201",
        "station": "Paris Gare de Lyon",
        "scheduled_at": "2026-11-05T10:00:00+01:00",
        "delay_minutes": 25,
        "is_cancelled": False,
    }
    response = api_client.post("/api/events/", payload, format="json")

    assert response.status_code == 201
    assert TrainEvent.objects.count() == 1


@pytest.mark.django_db
def test_reject_invalid_train_number(api_client):
    payload = {
        "train_number": "TGV62",
        "station": "Lyon Part-Dieu",
        "scheduled_at": "2026-11-05T10:00:00+01:00",
    }
    response = api_client.post("/api/events/", payload, format="json")

    assert response.status_code == 400
    assert "train_number" in response.data
    assert TrainEvent.objects.count() == 0


def test_filter_by_station(api_client, sample_events):
    response = api_client.get("/api/events/?station=marseille")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["train_number"] == "6205"


def test_kpi(api_client, sample_events):
    response = api_client.get("/api/events/kpi/")

    assert response.status_code == 200
    assert response.data == {
        "total_trains": 4,
        "cancelled_trains": 1,
        "punctuality_rate_pct": 33.3,
        "avg_delay_minutes": 13.3,
        "refund_eligible_trains": 1,
    }