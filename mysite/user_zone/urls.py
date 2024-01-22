from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("services/", views.services, name="services"),
    path("products/", views.products, name="products"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("general_data_list/", views.GeneralDataFilterView.as_view(), name="general_data_list"),
    path("edit_general_data/", views.EditGeneralData.as_view(), name="edit_general_data"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='user_zone/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmUserView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='user_zone/password_reset_complete.html'), name='password_reset_complete'),
    path("external_request/", views.login_external_request, name="login_external_request")
]
