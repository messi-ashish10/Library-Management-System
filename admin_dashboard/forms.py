from django import forms
from library.models import Book  # Import the Book model from the main app

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'genre', 'isbn', 'publisher', 'publication_date', 'total_copies', 'copies_available', 'cover_image_url', 'description', 'authors']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'authors': forms.CheckboxSelectMultiple(),
        }
