from rest_framework import serializers
from .models import MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')
    price = serializers.ReadOnlyField(source='menu_item.price')

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'menu_item_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'created_at', 'delivered_at', 'items']
