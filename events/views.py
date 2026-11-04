from django.db.models import Avg, Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TrainEvent
from .serializers import TrainEventSerializer

ON_TIME_THRESHOLD_MINUTES = 5
REFUND_THRESHOLD_MINUTES = 30


class TrainEventViewSet(viewsets.ModelViewSet):
    queryset = TrainEvent.objects.all()
    serializer_class = TrainEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        station = self.request.query_params.get("station")
        min_delay = self.request.query_params.get("min_delay")

        if station:
            queryset = queryset.filter(station__icontains=station)
        if min_delay and min_delay.isdigit():
            queryset = queryset.filter(delay_minutes__gte=int(min_delay))

        return queryset

    @action(detail=False, methods=["get"])
    def kpi(self, request):
        running = Q(is_cancelled=False)
        stats = self.get_queryset().aggregate(
            total=Count("id"),
            cancelled=Count("id", filter=Q(is_cancelled=True)),
            on_time=Count("id", filter=running & Q(delay_minutes__lt=ON_TIME_THRESHOLD_MINUTES)),
            refund_eligible=Count("id", filter=running & Q(delay_minutes__gte=REFUND_THRESHOLD_MINUTES)),
            avg_delay=Avg("delay_minutes", filter=running),
        )

        running_trains = stats["total"] - stats["cancelled"]
        punctuality_rate = (
            round(100 * stats["on_time"] / running_trains, 1) if running_trains else None
        )
        avg_delay = round(stats["avg_delay"], 1) if stats["avg_delay"] is not None else None

        return Response({
            "total_trains": stats["total"],
            "cancelled_trains": stats["cancelled"],
            "punctuality_rate_pct": punctuality_rate,
            "avg_delay_minutes": avg_delay,
            "refund_eligible_trains": stats["refund_eligible"],
        })
        