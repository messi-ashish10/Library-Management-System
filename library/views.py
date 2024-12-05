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

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def admin_register(request):
    if request.method == "POST":
        # Get data from the form
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "library/admin_register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "library/admin_register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "library/admin_register.html")

        # Create the admin user
        try:
            user = User.objects.create_user(
                first_name=full_name.split(" ")[0],  # First name from full name
                last_name=" ".join(full_name.split(" ")[1:]),  # Last name
                username=username,
                email=email,
                password=password,  # Automatically hashes the password
            )
            user.is_staff = True  # Grant is_staff privilege
            user.save()

            messages.success(request, "Admin account created successfully.")
            return redirect("admin_login")  # Redirect to admin login page
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, "library/admin_register.html")

    return render(request, "library/admin_register.html")



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
    """
    View for displaying book details.
    """
    book = get_object_or_404(Book, id=book_id)
    context = {'book': book}
    return render(request, 'library/book_detail.html', context)

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
@login_required
def profile_view(request):
    """
    View to display the user's profile and currently borrowed books.
    """
    # Fetch currently borrowed books (where return_date is NULL)
    borrowed_books = OrderItem.objects.filter(
        order__user=request.user,
        return_date__isnull=True
    ).select_related('book', 'order')

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
        print("Hello world")
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
    """
    Handles the borrowing of a book by a user.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        # Borrow and return dates
        borrow_date = request.POST.get("borrow_date", date.today())
        return_date = request.POST.get("return_date", date.today() + timedelta(days=14))

        if book.copies_available < 1:
            messages.error(request, f"'{book.title}' is not available for borrowing.")
            return redirect("book_list")

        # Create Order
        order = Order.objects.create(user=request.user, due_date=return_date)

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            book=book,
            borrow_date=borrow_date,
            expected_return_date=return_date
        )

        # Update book's availability
        book.copies_available -= 1
        book.save()

        messages.success(request, f"You have successfully borrowed '{book.title}'. Due date: {return_date}.")
        return redirect("borrow_history")  # Redirect to the borrow history page

    context = {
        "book": book
        #"borrow_date": date.today(),
    }
    return render(request, "library/borrow_book.html", context)
#Reservation
@login_required
def save_reservation(request, book_id):
    """
    Save a reservation for a book and decrease the available copies.
    """
    book = get_object_or_404(Book, id=book_id)

    # Check if the user already has a pending reservation for this book
    existing_reservation = Reservation.objects.filter(user=request.user, book=book, status='Pending').first()
    if existing_reservation:
        messages.error(request, "You already have a pending reservation for this book.")
        return redirect("my_reservations")  # Redirect to reservations page

    if book.copies_available <= 0:
        messages.error(request, f"The book '{book.title}' is currently unavailable for reservation.")
        return redirect("my_reservations")  # Redirect to reservations page

    try:
        # Create a new reservation
        reservation = Reservation.objects.create(user=request.user, book=book)

        # Decrease the available copies
        book.copies_available -= 1
        book.save()

        messages.success(request, f"Your reservation for '{book.title}' has been saved!")
    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An error occurred while saving your reservation: {e}")
        return redirect("my_reservations")  # Redirect to reservations page

    # Redirect to reservations page
    return redirect("my_reservations")


@login_required
def my_reservations(request):
    """
    Display all reservations for the logged-in user.
    """
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, "library/my_reservations.html", {"reservations": reservations})


@login_required
def cancel_reservation(request, reservation_id):
    """
    Cancel a reservation and increase the available copies.
    """
    # Fetch the reservation
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # Increase the available copies for the reserved book
    book = reservation.book
    book.copies_available += 1
    book.save()

    # Delete the reservation
    reservation.delete()

    messages.success(request, f"Reservation for '{book.title}' has been canceled, and the book is now available for others.")
    return redirect('my_reservations')

#Borrow history
@login_required
def borrow_history(request):
    # Fetch all borrowed books for the logged-in user
    orders = OrderItem.objects.filter(order__user=request.user).select_related('book')
    return render(request, 'library/borrow_history.html', {'orders': orders})

@login_required
def return_book(request, book_id):
    """
    Handles the return of a borrowed book.
    """
    if request.method == "POST":
        
        try:
            # Fetch the order item related to the user and book
            order_item = OrderItem.objects.filter(
                order__user=request.user,
                book_id=book_id,
                return_date__isnull=True
            ).first()
            
            if not order_item:
                messages.error(request, "No active borrowing record found for this book.")
                return redirect("borrow_history")

            # Update return_date and calculate fine
            order_item.return_date = date.today()
            order_item.calculate_fine()

            # Update Order status
            order = order_item.order
            if order_item.fine_total > 0:
                order.status = "Overdue"
            else:
                order.status = "Returned"
            order.save()

            # Update book availability
            book = order_item.book
            book.copies_available += 1
            book.save()

            # Automatically create a fine record if applicable
            #if order_item.fine_total > 0:
                #Fine.objects.create(
                    #user=request.user,
                    #order_item=order_item,
                    #amount=order_item.fine_total,
                    #payment_status="Unpaid"
                #)

            messages.success(request, f"Successfully returned the book '{book.title}'.")
        except Exception as e:
            messages.error(request, f"An error occurred while returning the book: {str(e)}")

        return redirect("borrow_history")
    
@login_required
def fine_management(request):
    """
    View for managing fines.
    """
    fines = Fine.objects.filter(user=request.user)
    context = {
        'fines': fines,
    }
    return render(request, 'library/fine.html', context)