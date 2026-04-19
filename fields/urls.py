from django.urls import path
from . import views

app_name = 'fields'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('fields/', views.field_list, name='field_list'),
    path('fields/create/', views.field_create, name='field_create'),
    path('fields/<int:pk>/', views.field_detail, name='field_detail'),
    path('fields/<int:pk>/edit/', views.field_update, name='field_update'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field_delete'),
    path('fields/<int:pk>/add-update/', views.add_field_update, name='add_field_update'),
]