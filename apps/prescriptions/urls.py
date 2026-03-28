from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('prescriptions/new/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), name='prescription_delete'),
    path('prescriptions/<int:pk>/pdf/', views.prescription_pdf_view, name='prescription_pdf'),
    path('prescriptions/<int:pk>/print/', views.prescription_print_view, name='prescription_print'),
    path('prescriptions/<int:pk>/send-telegram/', views.send_to_telegram_view, name='prescription_send_telegram'),
    # Public share links — no login required
    path('rx/<uuid:token>/',     views.prescription_share_view,     name='prescription_share'),
    path('rx/<uuid:token>/pdf/', views.prescription_share_pdf_view, name='prescription_share_pdf'),
]
