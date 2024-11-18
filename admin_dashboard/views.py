# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from library.models import Book, Author  # Import models from the main app
from .forms import BookForm  # We’ll create this form in the next step

# Restrict access to admin users only
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    books = Book.objects.all()
    return render(request, 'admin-dashboard.html', {'books': books})

@user_passes_test(is_admin)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully.")
            return redirect('admin-dashboard')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully.")
            return redirect('admin-dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})

@user_passes_test(is_admin)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect('admin-dashboard')
