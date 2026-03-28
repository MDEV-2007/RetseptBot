from django.urls import path
from . import views

urlpatterns = [
    path('drugs/', views.DrugListView.as_view(), name='drug_list'),
    path('drugs/<int:pk>/', views.DrugDetailView.as_view(), name='drug_detail'),
]
