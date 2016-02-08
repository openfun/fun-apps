from rest_framework import serializers


class PaymentNotificationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    order_number = serializers.CharField(required=True)
