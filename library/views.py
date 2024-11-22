from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, BorrowingHistory, Reservation, Fine, Author, Order, OrderItem
from django.utils import timezone
from .forms import UserRegistrationForm

# Create your views here.
def home(request):
    books = Book.objects.all()
    return render(request, 'library/home.html', {'books':books})


# Logout view
def logout_view(request):
    logout(request)
    return render(request, 'library/logout.html')

# Register view
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

# About view
def about_view(request):
    return render(request, 'library/about.html')

# Contact view
def contact_view(request):
    if request.method == "POST":
        # Handle form submission here
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        # Save the message to the database or send an email
        return HttpResponse("Thank you for reaching out to us!")
    return render(request, 'library/contact.html')

def book_detail(request, book_id):
    # Get the book object
    book = get_object_or_404(Book, pk=book_id)
    authors = Author.objects.filter(bookauthor__book=book)  # Assuming a many-to-many relationship with BookAuthor
    
    # Retrieve borrowing history for the book
    borrowing_history = BorrowingHistory.objects.filter(book=book)

    # Retrieve reservations and fines for the current user if logged in
    user_reservations = Reservation.objects.filter(book=book, user=request.user) if request.user.is_authenticated else []
    user_fines = Fine.objects.filter(user=request.user) if request.user.is_authenticated else []

    # Render the book detail page with all required data
    return render(request, 'library/book_detail.html', {
        'book': book,
        'authors': authors,
        'borrowing_history': borrowing_history,
        'user_reservations': user_reservations,
        'user_fines': user_fines,
    })

@login_required
def borrow_book(request, book_id):
    # Get the book object
    book = get_object_or_404(Book, pk=book_id)

    # Check if copies are available
    if book.copies_available > 0:
        # Create an Order and OrderItem for the user
        order = Order.objects.create(user=request.user, due_date=timezone.now() + timezone.timedelta(days=14))  # Assuming a 14-day borrowing period
        OrderItem.objects.create(order=order, book=book, borrow_date=timezone.now())

        # Decrement the available copies
        book.copies_available -= 1
        book.save()

        messages.success(request, "You have successfully borrowed the book!")
    else:
        messages.error(request, "This book is currently unavailable.")

    return redirect('book_detail', book_id=book_id)

@login_required
def reserve_book(request, book_id):
    # Get the book object
    book = get_object_or_404(Book, pk=book_id)

    # Check if the book is already reserved by the user
    existing_reservation = Reservation.objects.filter(user=request.user, book=book, status='Pending').exists()
    if existing_reservation:
        messages.warning(request, "You have already reserved this book.")
    else:
        # Create a reservation for the user
        Reservation.objects.create(user=request.user, book=book, reservation_date=timezone.now(), status='Pending')
        messages.success(request, "Your reservation has been placed successfully!")

    return redirect('book_detail', book_id=book_id)

# User Registration View
def register(request):
    print("Entering register view")  # Debug: check if view is called
    if request.method == 'POST':
        print("POST request received")  # Debug: check if POST request is received
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug: check if form is valid
            user = form.save()  # Save the user to the database
            login(request, user)  # Log in the user after successful registration
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('home')  # Redirect to home or another page
        else:
            print("Form is invalid")  # Debug: check if form is invalid
            print(form.errors)  # Print form errors to the console for debugging
            messages.error(request, "There was an error with your registration.")
    else:
        print("GET request received")  # Debug: check if GET request is received
        form = UserRegistrationForm()
    return render(request, 'library/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect logged-in users to home page
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'library/login.html')

# User Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')  # Redirect to login page after logout

#Profile View
#@login_required(login_url='login')  # Redirect to login if not authenticated
def profile_view(request):
    return render(request, 'library/profile.html')


############################################################################
#Book SECTION
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'library/book_detail.html', {'book': book})

@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the book has available copies
    if book.copies_available > 0:
        # Reserve the book
        reservation, created = Reservation.objects.get_or_create(
            user=request.user,
            book=book,
            status='Pending'
        )
        
        if created:
            # Reduce the available copies by 1
            book.copies_available -= 1
            book.save()
            messages.success(request, f"Book '{book.title}' has been reserved for you.")
        else:
            messages.info(request, f"You already have a pending reservation for '{book.title}'.")
    else:
        messages.error(request, f"Sorry, '{book.title}' is not available for reservation.")
    
    return redirect('book_detail', book_id=book.id)