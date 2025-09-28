from django.urls import path
from . import views  # all submodules imported via views/__init__.py

urlpatterns = [
    path('', views.home_view, name='home'),

    # Auth + OTP
   
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path("verify-number/", views.verify_number, name="verify_number"),
  

    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

    # Fake News Detection
    path('detect/', views.detect_news_view, name='detect'),
    path('predict/', views.predict_news_view, name='predict_news'),
    path("check/", views.check_news_view, name="check_news"),
    
    # Reports
    path("dashboard/export/csv/", views.export_dashboard_csv, name="export_dashboard_csv"),
    path("dashboard/export/pdf/", views.export_dashboard_pdf, name="export_dashboard_pdf"),

]
