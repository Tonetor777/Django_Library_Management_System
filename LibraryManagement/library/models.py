from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username.strip(), email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SuperAdmin')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    STUDENT = 'Student'
    ADMIN = 'Admin'
    SUPER_ADMIN = 'SuperAdmin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (ADMIN, 'Admin'),
        (SUPER_ADMIN, 'SuperAdmin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    @property
    def is_student(self):
        return self.role.strip() == self.STUDENT
    @property
    def is_admin(self):
        return self.role.strip() == self.ADMIN
    @property
    def is_superadmin(self):
        return self.role.strip() == self.SUPER_ADMIN
    objects = UserManager()
    
class Book(models.Model): 
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    genres = models.ManyToManyField('Genre', related_name='books')
    copies = models.PositiveIntegerField()
    book_img = models.ImageField (null=True, blank=True)
    
    def __str__(self):
        return self.title 
    
    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f"{self.title} is written by {self.author}"
        super().save(*args, **kwargs)

    def average_rating(self):
        reviews = Review.objects.filter(book=self)
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return total_rating / reviews.count()
        else:
            return 0.0
    def total_reviews(self):
        return Review.objects.filter(book=self).count()
    def is_available(self):
        return self.copies > 0

class Genre(models.Model): 
    name = models.CharField(max_length=255)
    def __str__(self): 
        return self.name

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]) 
    comment = models.TextField()
    def __str__(self):
        return f"{self.user.username}'s review for {self.book.title}"

class Borrow(models.Model): 
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    borrow_date = models.DateField(auto_now_add=True) 
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default = False)
    def __str__(self): 
        return f"{self.user.username} borrowed {self.book.title}"

