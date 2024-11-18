from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
    path('edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
]
