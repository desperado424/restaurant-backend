# URLs (Wire Everything Together)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderDetailView
from .views import DailySalesReportCSVExport
from .views import DailySalesReportView
from .views import (
    MenuItemViewSet,
    PlaceOrderView,
    UpdateOrderStatusView,
    DashboardView
)

router = DefaultRouter()
router.register('menu', MenuItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/', PlaceOrderView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
    path('orders/<int:pk>/status/', UpdateOrderStatusView.as_view()),
    path('dashboard/', DashboardView.as_view()),
    path('reports/daily-sales/', DailySalesReportView.as_view()),
    path("reports/daily-sales/export/",
          DailySalesReportCSVExport.as_view(),
          name="daily-sales-csv"
    )

]
