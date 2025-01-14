from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('pets/',views.pet_list,name='pet_list'),
    path('pet/<int:pk>',views.pet_detail_view,name = 'pet_detail'),
    path('dogs/',views.dog_list_view,name = 'dog-list' ),
    path('cats/',views.cat_list_view,name ='cat_list'),
    path('price_range/',views.pet_range_view,name ='pet-range'),
    path('additem/',views.create_item,name='add_item'),
    path('delete/<int:pk>',views.pet_delete,name='delete'),
      
]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

