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
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='library/password_reset.html'), name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
]
