from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import Pet
admin.site.register(Pet)

# Define a custom UserAdmin
class CustomUserAdmin(UserAdmin):
    # Add a custom column to display user roles
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'role')  # Add 'role' here
    
    # Define a method to determine the user's role
    def role(self, obj):
        if obj.is_superuser:
            return "Superuser"
        elif obj.is_staff:
            return "Staff"
        else:
            return "Customer"
    role.short_description = "User Role"  # Column header in the admin panel


# Unregister the default User admin to allow customization   
admin.site.unregister(User)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)