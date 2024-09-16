from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('details/<str:place_id>', views.restaurant_detail_view, name='details'),
]