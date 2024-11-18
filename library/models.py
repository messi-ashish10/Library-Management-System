from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# UserProfile Model (extends User with additional details and role)
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_start_date = models.DateField(auto_now_add=True)
    membership_expiration_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# MembershipType Model
class MembershipType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


# Membership Model
class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Expired', 'Expired')], default='Active')

    def save(self, *args, **kwargs):
        if self.membership_type and not self.expiration_date:
            self.expiration_date = self.start_date + timedelta(days=self.membership_type.duration_in_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type.name}"

# Author Model
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
# Book Model
class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    publication_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)
    cover_image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')

    def __str__(self):
        return self.title



# BookAuthor Model (Associative Model for Many-to-Many relationship)
class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'author')

    def __str__(self):
        return f"{self.book.title} by {self.author.first_name} {self.author.last_name}"


# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Borrowed', 'Borrowed'), ('Returned', 'Returned'), ('Overdue', 'Overdue')], default='Borrowed')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    fine_total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.order.due_date:
            overdue_days = (self.return_date - self.order.due_date).days
            self.fine_total = overdue_days * self.fine_per_day
            self.save()

    def __str__(self):
        return f"OrderItem {self.id} for Book {self.book.title}"


# BorrowingHistory Model
class BorrowingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_paid = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"


# Reservation Model
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reservation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')

    def __str__(self):
        return f"Reservation {self.id} by {self.user.username} for {self.book.title}"


# Fine Model
class Fine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')], default='Unpaid')
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Fine {self.id} for {self.user.username}"


# AdminAction Model
class AdminAction(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    action_type = models.CharField(max_length=10, choices=[('Add', 'Add'), ('Update', 'Update'), ('Remove', 'Remove')])
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} {self.action_type} {self.book.title} on {self.action_date}"
