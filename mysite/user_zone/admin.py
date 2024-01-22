from django.contrib import admin
from django import forms
from .models import User, UserManager, GeneralData, ProductProperty, PurchaseOrder, Visit
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def save(self, commit=True):
        if self.is_valid():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password"])
            if commit:
                user.save()
            return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'is_admin']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.Meta.fields.remove('password')

class AdminUser(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    readonly_fields = ["id"]
    list_display = ['id', 'email', 'is_admin']
    list_filter = ['id', 'email', 'is_admin']
    fieldsets = (
        (None, {'fields': ['email', 'password']}),
        ('Permissions', {'fields': ['is_admin']}),
    )

    add_fieldsets = (
        (None, {
            'fields': ['email', 'password']}
        ),
    )
    search_fields = ['id', 'email', 'is_admin']
    ordering = ['email']
    filter_horizontal = []

class AdminGeneralData(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = ["id", "user", "name", "surname", "company_name", "register_id", "vat_id"]
    list_filter = ["id", "user", "name", "surname", "company_name", "register_id", "vat_id"]
    search_fields = ["id", "user", "name", "surname", "company_name", "register_id", "vat_id"]
    ordering = ["id"]

class AdminProductProperty(admin.ModelAdmin):
    list_display = ["product_id", "product_name", "licence_duration", "price"]
    ordering = ["product_id"]

class AdminPurchaseOrder(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = ["id", "user", "get_product_name", "order_date", "payment_date", "license_expiration_date",
                    "last_license_validation_date", "licence_duration", "price"]
    list_filter = ["id", "user", "order_date", "payment_date", "license_expiration_date",
                    "last_license_validation_date", "licence_duration", "price"]
    search_fields = ["id", "user", "order_date", "payment_date", "license_expiration_date",
                    "last_license_validation_date", "licence_duration", "price"]
    ordering = ["id"]

    @admin.display(description="Produkt", ordering="product_name__product_name")
    def get_product_name(self, obj):
        return obj.product_name.product_name

class AdminVisit(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = ["user", "path", "visit_date"]
    list_filter = ["user", "path", "visit_date"]
    search_fields = ["user", "path", "visit_date"]
    ordering = ["id"]

admin.site.register(User, AdminUser)
admin.site.register(GeneralData, AdminGeneralData)
admin.site.register(ProductProperty, AdminProductProperty)
admin.site.register(PurchaseOrder, AdminPurchaseOrder)
admin.site.register(Visit, AdminVisit)
