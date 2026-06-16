from django.contrib import admin

from .models import City, User


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'city', 'blood_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'city', 'blood_type', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('البيانات الشخصية', {'fields': ('first_name', 'last_name', 'phone_number', 'city', 'blood_type')}),
        ('الصلاحيات', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('التواريخ', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            # New user creation: encrypt the password
            obj.set_password(obj.password)
        else:
            # Editing existing user: encrypt only if the password changed from the stored hash
            original_user = User.objects.get(pk=obj.pk)
            if obj.password != original_user.password:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


