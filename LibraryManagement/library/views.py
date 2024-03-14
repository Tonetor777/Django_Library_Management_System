from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate
from .models import Book,User,Borrow
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
# Create your views here.

def home_page(request):
    return render(request , 'home.html')

def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')

    else:
        form = RegistrationForm()

    return render(request, 'registration/sign_up.html', {"form": form} )

def logout(request):
    logout(request)
    return redirect ('/home')

def all_books(request):
    allbooks = Book.objects.all()
    return render(request , 'allbooks.html' , {'allbooks' : allbooks})

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'book_detail.html', {'book': book})

def borrow(request, user_id, book_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        book = get_object_or_404(Book, pk=book_id)
        
        if Borrow.objects.filter(user=user, book=book).exists():
            messages.error(request, "You have already borrowed this book.")
            return redirect('book_detail', book_id=book_id)
        
        num_borrowed_books = Borrow.objects.filter(user=user).count()
        if num_borrowed_books >= 3:
            messages.error(request, "You have already borrowed the maximum number of books. Return th books to borrow another")
            return redirect('book_detail', book_id=book_id)

        borrow_date = datetime.now().date()
        return_date = borrow_date + timedelta(days=7)

        borrow = Borrow.objects.create(
            user=user,
            book=book,
            borrow_date=borrow_date,
            return_date=return_date
        )
        borrow.save()
        book.copies -= 1
        book.save()
        messages.success(request , "Borrowed book successfuly! ")

        return redirect('book_detail', book_id=book_id) 
    else:
        messages.error(request , "Some thing went wrong try again" )

@login_required
def borrowed_books(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    borrowings = Borrow.objects.filter(user=user)
    books_with_dates = [(borrow.book, borrow.return_date) for borrow in borrowings]
    return render(request, 'borrowed_books.html', {'books_with_dates': books_with_dates})
