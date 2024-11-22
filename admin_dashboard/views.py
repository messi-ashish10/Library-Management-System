from django.shortcuts import render, redirect, get_object_or_404
from library.models import Book, OrderItem
from django.contrib import messages


def admin_dashboard(request):
    # Calculating statistics
    total_books = Book.objects.count()
    borrowed_books = OrderItem.objects.filter(return_date__isnull=True).count()
    returned_books = OrderItem.objects.filter(return_date__isnull=False).count()

    # Fetch all books
    books = Book.objects.all()

    return render(request, 'admin_dashboard.html', {
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'returned_books': returned_books,
        'books': books,
    })

def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        isbn = request.POST.get('isbn')
        publisher = request.POST.get('publisher')
        publication_date = request.POST.get('publication_date')
        total_copies = request.POST.get('total_copies')
        copies_available = total_copies  # When a book is added, all copies are available
        cover_image_url = request.POST.get('cover_image_url')
        description = request.POST.get('description')

        # Save the new book
        Book.objects.create(
            title=title,
            genre=genre,
            isbn=isbn,
            publisher=publisher,
            publication_date=publication_date,
            total_copies=total_copies,
            copies_available=copies_available,
            cover_image_url=cover_image_url,
            description=description
        )
        messages.success(request, 'Book added successfully!')
        return redirect('admin_dashboard')

    return render(request, 'add_book.html')

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.genre = request.POST.get('genre')
        book.isbn = request.POST.get('isbn')
        book.publisher = request.POST.get('publisher')
        book.publication_date = request.POST.get('publication_date')
        book.total_copies = request.POST.get('total_copies')
        book.copies_available = request.POST.get('copies_available')
        book.cover_image_url = request.POST.get('cover_image_url')
        book.description = request.POST.get('description')
        book.save()

        messages.success(request, 'Book updated successfully!')
        return redirect('admin_dashboard')

    return render(request, 'edit_book.html', {'book': book})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('admin_dashboard')

    return render(request, 'delete_book.html', {'book': book})