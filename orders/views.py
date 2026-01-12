# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.timezone import now
from django.db.models import F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import MenuItem, Order, OrderItem
from .serializers import MenuItemSerializer, OrderSerializer

# Menu CRUD (Admin Menu Management) - This automatically gives: create, read, update, delete
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

# Place Order API
class PlaceOrderView(APIView):
    def post(self, request):
        items = request.data.get('items')

        if not items:
            return Response(
                {"error": "Order must contain items"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create()
        total_price = 0

        for item in items:
            menu_item = MenuItem.objects.get(id=item['menu_item_id'])
            quantity = item['quantity']

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )

            total_price += menu_item.price * quantity

        order.total_price = total_price
        order.save()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
# Order Status Workflow
VALID_TRANSITIONS = {
    'pending': ['cooking'],
    'cooking': ['ready'],
    'ready': ['delivered'],
}

class UpdateOrderStatusView(APIView):
    def patch(self, request, pk):
        order = Order.objects.get(pk=pk)
        new_status = request.data.get('status')

        if new_status not in VALID_TRANSITIONS.get(order.status, []):
            return Response(
                {"error": "Invalid status transition"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        
        if new_status == 'delivered' and order.delivered_at is None:
            order.delivered_at = timezone.now()

        order.save()
        

        return Response(OrderSerializer(order).data)

# Dashboard API
class DashboardView(APIView):
    def get(self, request):
        total_sales = Order.objects.filter(
            status='delivered'
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0

        total_orders = Order.objects.count()

        most_ordered_item = (
            OrderItem.objects
            .values('menu_item__name')
            .annotate(total=Sum('quantity'))
            .order_by('-total')
            .first()
        )

        return Response({
            "total_sales": total_sales,
            "total_orders": total_orders,
            "most_ordered_item": most_ordered_item
        })

class OrderDetailView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return Response(OrderSerializer(order).data)


class DailySalesReportView(APIView):
    def get(self, request):
        today = now().date()

        delivered_orders = Order.objects.filter(
            delivered_at__date=today,
            status='delivered'
        )

        total_sales = delivered_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0

        total_orders = delivered_orders.count()

        items = (
            OrderItem.objects
            .filter(order__in=delivered_orders)
            .values('menu_item__name')
            .annotate(
                total_quantity=Sum('quantity'),
                revenue=Sum(F('menu_item__price') * F('quantity'))
            )
            .order_by('-revenue')
       )


        return Response({
            "date": str(today),
            "total_sales": total_sales,
            "total_orders": total_orders,
            "items": items
        })

