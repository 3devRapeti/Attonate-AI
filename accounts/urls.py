from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("client-signup/", views.client_signup_view, name="client_signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("account/", views.account_view, name="account"),
    path("account/export/", views.export_data_view, name="export_data"),
    path("account/delete/", views.delete_account_view, name="delete_account"),
    path("account/verify/email/send/", views.send_email_otp_view, name="send_email_otp"),
    path("account/verify/email/check/", views.verify_email_otp_view, name="verify_email_otp"),
    path("account/verify/phone/send/", views.send_phone_otp_view, name="send_phone_otp"),
    path("account/verify/phone/check/", views.verify_phone_otp_view, name="verify_phone_otp"),
]
