from rest_framework import serializers

from .models import TrainEvent


class TrainEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainEvent
        fields = [
            "id",
            "train_number",
            "station",
            "scheduled_at",
            "delay_minutes",
            "is_cancelled",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_train_number(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError(
                "Le numéro de train doit contenir uniquement des chiffres."
            )
        return value