from django.urls import path
from .views import PetListCreateAPIView,PetRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('pets/',PetListCreateAPIView.as_view(),name='pet-list-create'),
    path('pet/<int:pk>/',PetRetrieveUpdateDestroyAPIView.as_view(),name='pet_detail_api'),
]