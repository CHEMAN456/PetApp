from django.contrib import admin
from .models import Review,Cart,Order,Profile

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'placed_at', 'status')
    list_filter = ('status', 'placed_at')
    search_fields = ('user__username',)
    filter_horizontal = ('cart_items',)
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass    