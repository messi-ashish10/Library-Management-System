from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, BorrowingHistory, Reservation, Fine, Author, Order, OrderItem, UserProfile
from django.utils import timezone
from .forms import UserRegistrationForm
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date, timedelta

# Create your views here.
def home(request):
    books = Book.objects.all()
    return render(request, 'library/home.html', {'books':books})


# Logout view
def logout_view(request):
    logout(request)
    return render(request, 'library/logout.html')

# Register view
# Extend UserCreationForm to include additional fields
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address')
    phone_number = forms.CharField(max_length=15, required=False, help_text='Phone number (optional)')
    address = forms.CharField(widget=forms.Textarea, required=False, help_text='Address (optional)')

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2'
        ]

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user instance
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Create the UserProfile instance
            phone_number = form.cleaned_data.get('phone_number', '')
            address = form.cleaned_data.get('address', '')
            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                address=address
            )

            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')  # Replace 'login' with your login page URL name
        else:
            messages.error(request, 'There was an error with your registration. Please check the form and try again.')
    else:
        form = CustomUserCreationForm()

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
#def register(request):
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
@login_required
def library_dashboard(request):
    """
    Custom dashboard for admin/staff users.
    """
    if request.user.is_staff:
        return render(request, 'library/dashboard.html')  # Render the dashboard template
    else:
        return redirect('/')  # Redirect unauthorized users to the homepage

def admin_login_view(request):
    """
    Custom login view for admin/staff users. 
    Authenticates the user and redirects to the admin dashboard if authorized.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:  # Check if the user has staff privileges
                login(request, user)  # Log in the user
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                messages.error(request, "You are not authorized to access the admin dashboard.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'library/admin_login.html')


# User Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:  # Redirect staff/admin users to the admin panel
                messages.error(request, "Admin accounts must log in through the admin portal.")
                return redirect('/admin/login/')

            # Log in regular users
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
    """
    Display the user's profile with borrowed books.
    """
    # Fetch all borrowed books for the logged-in user
    borrowed_books = OrderItem.objects.filter(order__user=request.user).select_related('book')

    # Render the template with user profile and borrowed books
    context = {
        "user": request.user,
        "borrowed_books": borrowed_books,
    }
    return render(request, "library/profile.html", context)


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

#Search Result
def search_books(request):
    """
    Handles the search functionality for books.
    Matches if any word in the query matches the title, genre, author names, or publisher.
    """
    query = request.GET.get('query', '')  # Get the search query from the URL
    results = []

    if query:
        # Split the query into individual words
        query_words = query.split()

        # Build the Q object dynamically for each word
        search_conditions = Q()
        for word in query_words:
            search_conditions |= (
                Q(title__icontains=word) | 
                Q(genre__icontains=word) |
                Q(publisher__icontains=word) |
                Q(authors__first_name__icontains=word) | 
                Q(authors__last_name__icontains=word)
            )

        # Filter books based on the search conditions
        results = Book.objects.filter(search_conditions).distinct()

    return render(request, 'library/search_result.html', {'query': query, 'results': results})

#Borrow
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        borrow_date = request.POST.get("borrow_date", date.today())
        return_date = request.POST.get("return_date", date.today() + timedelta(days=14))

        if book.copies_available < 1:
            messages.error(request, f"'{book.title}' is not available for borrowing.")
            return redirect("book_list")

        # Create Order and OrderItem
        order = Order.objects.create(user=request.user, due_date=return_date)
        OrderItem.objects.create(order=order, book=book, borrow_date=borrow_date, return_date=return_date)

        # Update book copies
        book.copies_available -= 1
        book.save()

        messages.success(request, f"You have successfully borrowed '{book.title}'.")
        return redirect("borrow_history")  # Redirect to the borrow history page

    context = {
        "book": book,
        "borrow_date": date.today(),
    }
    return render(request, "library/borrow_book.html", context)
#Reservation
@login_required
def save_reservation(request, book_id):
    """
    Save a reservation for a book.
    """
    book = get_object_or_404(Book, id=book_id)

    # Check if the user already has a pending reservation for this book
    existing_reservation = Reservation.objects.filter(user=request.user, book=book, status='Pending').first()
    if existing_reservation:
        messages.error(request, "You already have a pending reservation for this book.")
        return redirect("my_reservations")  # Redirect to reservations page

    try:
        # Create a new reservation
        reservation = Reservation.objects.create(user=request.user, book=book)
        messages.success(request, f"Your reservation for '{book.title}' has been saved!")
    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An error occurred while saving your reservation: {e}")
        return redirect("my_reservations")  # Redirect to reservations page
    
    # Redirect to reservations page
    return redirect("my_reservations")

@login_required
def my_reservations(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reservations = Reservation.objects.filter(user=request.user, book=book)
    return render(request, "library/my_reservations.html", {"reservations": reservations, "book": book})

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # Delete the reservation
    reservation.delete()
    messages.success(request, f"Reservation for '{reservation.book.title}' has been canceled.")
    return redirect('my_reservations')

#Borrow history
@login_required
def borrow_history(request):
    # Fetch all borrowed books for the logged-in user
    orders = OrderItem.objects.filter(order__user=request.user).select_related('book')
    return render(request, 'library/borrow_history.html', {'orders': orders})