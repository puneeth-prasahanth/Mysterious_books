from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Author(models.Model):
        first_name= models.CharField(max_length=100)
        middle_name= models.CharField(max_length=100,null=True,blank=True)
        last_name= models.CharField(max_length=100,null=True,blank=True)
        def __str__(self):
            return u"%s %s %s" % (self.first_name, self.middle_name, self.last_name)
            #return u"%s,  %s" % (self.first_name, self.last_name)

class Books(models.Model):
    title = models.CharField(max_length=200)
    Auther = models.ForeignKey(Author, blank=False, null=False)
    Discription = models.TextField()
    Publish_date = models.DateField(default=timezone.now)
    Prize = models.DecimalField(decimal_places=2, max_digits=8)
    stack = models.IntegerField(default=0)

class Review(models.Model):

    book=models.ForeignKey(Books)
    user=models.ForeignKey(User)
    Publish_date = models.DateField(default=timezone.now)
    text = models.TextField()

class Cart(models.Model):

    user = models.ForeignKey(User)
    active = models.BooleanField(default=True)
    order_date = models.DateField(null=True)
    payment_type = models.CharField(max_length=100,null=True)
    payment_id = models.CharField(max_length=100,null=True)

    def add_to_cart(self,book_id):
        book=Books.objects.get(pk=book_id)
        try:
            prexisting_order=BooksOrdered.objects.get(book=book,cart=self)
            prexisting_order.quantity += 1
            prexisting_order.save()
        except BooksOrdered.DoesNotExist:
                new_order=BooksOrdered.objects.create(
                    book=book,
                    cart=self,
                    quantity=1
                )
                new_order.save()

    def remove_from_cart(self,book_id):
        book=Books.objects.get(pk=book_id)
        try:
            prexisting_order=BooksOrdered.objects.get(book=book,cart=self)
            if prexisting_order.quantity >= 1:
                prexisting_order.quantity -= 1
                prexisting_order.save()
            else:
                prexisting_order.delete = 0

        except BooksOrdered.DoesNotExist:
            pass

        #BooksOrdered.save()

class BooksOrdered(models.Model):

    book = models.ForeignKey(Books)
    cart = models.ForeignKey(Cart)
    quantity = models.IntegerField(default=0)
