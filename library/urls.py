from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),  # Home page route
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='library/password_reset.html'), name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('search/', views.search_books, name='search_books'),
    path("borrow/<int:book_id>/", views.borrow_book, name="borrow_book"),
    #path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('borrow-history/', views.borrow_history, name='borrow_history'),
    path("save_reservations/<int:book_id>/", views.save_reservation, name="save_reservation"),
    path('return-book/<int:book_id>/', views.return_book, name='return_book'),
    path('fines/', views.fine_management, name='fine_management'),
    path("library-admin/", views.admin_register, name="admin_register"),
]
