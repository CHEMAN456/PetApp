"""
URL configuration for petstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from petapp import views
from petapp.views import MyView
from django.conf import settings
from django.conf.urls.static import static
from petstore.views import register_view,login_view,logout_view,edit_pet,pet_review,add_to_cart,view_cart,update_cart,payment,paypal_payment,payment_success,payment_cancel,sales_dashboard,Profile_Create,profile_view
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home',views.home),
    path('about',MyView.as_view()),
    path('',include('petapp.urls')),
    path('register/',register_view,name='register'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('profile/',Profile_Create,name = 'profile'),
    path('profile_view/',profile_view,name = 'profile_view'),
    path('edit/<int:pk>/',edit_pet,name='edit'),
    path('petreview/<int:pk>/',pet_review,name='review'),
    path('cart/add/<int:pk>/',add_to_cart,name='cart'),
    path('cart/',view_cart,name='view_cart'),
    path('update_cart/<int:pk>/',update_cart,name='update'),
    path('payment/',payment,name='payment'),
    path('api/',include('petapp.api_urls')),
    path('make_payment/', paypal_payment, name='paypal_payment'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
    path('dashboard/', sales_dashboard , name = 'dashboard'),
    
  
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
