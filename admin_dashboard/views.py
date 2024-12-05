from django.shortcuts import render, redirect, get_object_or_404
from library.models import Book, OrderItem, Author, BorrowingHistory
from django.contrib import messages


def admin_dashboard(request):
    # Fetch all books
    books = Book.objects.all()

    # Calculate total books
    total_books = books.count()

    # Calculate borrowed books
    borrowed_books = OrderItem.objects.filter(return_date__isnull=True).count()

    # Calculate returned books
    returned_books = OrderItem.objects.filter(return_date__isnull=False).count()

    return render(request, 'admin_dashboard.html', {
        'total_books': total_books,
        'borrowed_books': borrowed_books,
        'returned_books': returned_books,
        'books': books,
    })


def add_book(request):
    if request.method == 'POST':
        # Book fields
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        isbn = request.POST.get('isbn')
        publisher = request.POST.get('publisher')
        publication_date = request.POST.get('publication_date')
        total_copies = int(request.POST.get('total_copies', 1))
        total_copies_available = int(request.POST.get('total_copies_available', 1))
        cover_image_url = request.POST.get('cover_image_url')
        description = request.POST.get('description')

        # Create Book
        book = Book.objects.create(
            title=title,
            genre=genre,
            isbn=isbn,
            publisher=publisher,
            publication_date=publication_date,
            total_copies=total_copies,
            copies_available=total_copies_available,
            cover_image_url=cover_image_url,
            description=description,
        )

        # Author fields
        first_names = request.POST.getlist('first_name[]')
        last_names = request.POST.getlist('last_name[]')
        biographies = request.POST.getlist('biography[]')
        birth_dates = request.POST.getlist('birth_date[]')

        for first_name, last_name, biography, birth_date in zip(first_names, last_names, biographies, birth_dates):
            if first_name.strip() and last_name.strip():
                try:
                    author, created = Author.objects.get_or_create(
                        first_name=first_name.strip(),
                        last_name=last_name.strip(),
                        defaults={
                            'biography': biography.strip() if biography else '',
                            'birth_date': birth_date if birth_date else None,
                        }
                    )
                    book.authors.add(author)

                except Exception as e:
                    print(f"Error saving author {first_name} {last_name}: {e}")

        return redirect('admin_dashboard')

    return render(request, 'add_book.html')



def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Update Book Fields
        book.title = request.POST.get('title')
        book.genre = request.POST.get('genre')
        book.isbn = request.POST.get('isbn')
        book.publisher = request.POST.get('publisher')
        book.publication_date = request.POST.get('publication_date')
        book.total_copies = request.POST.get('total_copies', 1)
        book.copies_available = request.POST.get('total_copies_available')
        book.cover_image_url = request.POST.get('cover_image_url')
        book.description = request.POST.get('description')
        book.save()

        # Update Author Fields
        first_names = request.POST.getlist('first_name[]')
        last_names = request.POST.getlist('last_name[]')
        biographies = request.POST.getlist('biography[]')
        birth_dates = request.POST.getlist('birth_date[]')

        # Clear existing authors
        book.authors.clear()

        # Re-add authors (update existing or create new)
        for first_name, last_name, biography, birth_date in zip(first_names, last_names, biographies, birth_dates):
            author, created = Author.objects.get_or_create(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                defaults={'biography': biography, 'birth_date': birth_date if birth_date else None}
            )
            book.authors.add(author)

        return redirect('admin_dashboard')  # Redirect to the book's detail page

    return render(request, 'edit_book.html', {'book': book})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('admin_dashboard')

    return render(request, 'delete_book.html', {'book': book})