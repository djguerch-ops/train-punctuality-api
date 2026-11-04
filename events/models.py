from django.db import models


class TrainEvent(models.Model):
    train_number = models.CharField(max_length=10)
    station = models.CharField(max_length=100)
    scheduled_at = models.DateTimeField()
    delay_minutes = models.PositiveIntegerField(default=0)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self) -> str:
        return f"Train {self.train_number} - {self.station} (+{self.delay_minutes} min)"