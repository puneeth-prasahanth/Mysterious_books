from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string

import string,random
import paypalrestsdk, stripe

from .models import Books,Cart,BooksOrdered,Review
from .forms import ReviewForms


def index(request):
    return render(request,'template.html')

def store(request):
    books=Books.objects.all()
    context={
        'books':books,
    }
    return render(request,'base.html',context)

def book_detailes(request,book_id):
    book=Books.objects.get(pk=book_id)
    context={
            'book':book
        }
    if request.user.is_authenticated():
        if request.method == "POST":
            form=ReviewForms(request.POST)
            if form.is_valid():
                #form=ReviewForms(request.POST)
                new_review=Review.objects.create(
                    book=context['book'],
                    user=request.user,
                    text=form.cleaned_data.get('text')
                    )
                new_review.save()

                if Review.objects.filter(user=request.user).count()<6:
                    subject="Your Reword Points from Mysterious books."
                    to_email=[request.user.email]
                    from_email="site.master143@gmail.com"
                    email_context=Context({
                        'username':request.user.username,
                        'code':''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
                        'discount':10
                    })

                    text_email=render_to_string('email/render_email.txt',email_context)
                    html_email=render_to_string('email/render_email.html',email_context)
                    msg=EmailMultiAlternatives(subject,text_email,from_email,to_email)
                    msg.attach_alternative(html_email,'text/html')
                    msg.context_subtype='html'
                    msg.send()
        else:
            if Review.objects.filter(user=request.user,book=context['book']).count()==0:
                form=ReviewForms()
                context['form']=form
    context['reviews']=book.review_set.all()
    return render(request,'detailes.html',context)


def add_to_cart(request,book_id):
    if request.user.is_authenticated():
        try:
            book=Books.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart=Cart.objects.get(user=request.user,active=True)
            except ObjectDoesNotExist:
                cart=Cart.objects.create(user=request.user)
                cart.save()
            cart.add_to_cart(book_id)
        return redirect ('cart')
    else:
        return redirect ('index')

def remove_from_cart(request,book_id):
    if request.user.is_authenticated():
        try:
            book=Books.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart=Cart.objects.get(user=request.user,active=True)
            cart.remove_from_cart(book_id)
        return redirect ('cart')
    else:
        return redirect ('index')

def cart(request):
    if request.user.is_authenticated():
        cart=Cart.objects.filter(user=request.user,active=True)
        orders=BooksOrdered.objects.filter(cart=cart)
        total = 0
        count = 0
        for order in orders:
            total+=(order.book.Prize*order.quantity)
            ##print(f'order:{order.book.Prize}')
            count+=order.quantity

        context={
            'cart':orders,
            'total':total,
            'count':count,}

        return render(request,'cart.html',context)
    else:
        return redirect ('index')

def checkout(request,processor):
    if request.user.is_authenticated():
        cart=Cart.objects.filter(user=request.user,active=True)
        orders=BooksOrdered.objects.filter(cart=cart)
        if processor=="paypal":
            redirect_url=checkout_paypal(request,cart, orders)
            return redirect(redirect_url)
        elif processor=="stripe":
            token=request.POST('stripeToken')
            redirect_url=checkout_stripe(cart, orders, token)
            if status:
                return redirect(reverse('process_order', args=['stripe']))
            else:
                return redirect('order_error')

    else:
        return redirect ('index')

def checkout_paypal(request,cart,orders):
    if request.user.is_authenticated():
        items=[]
        total=0
        for order in orders:
            total+=(order.book.Prize*order.quantity)
            item={
                "name": order.book.title,
                "sku": order.book.id,
                "price": str(order.book.Prize),
                "currency": 'INR',
                "quantity": order.quantity}
            items.append(item)
        paypalrestsdk.configure({
                "mode": "sandbox", # sandbox or live
                "client_id": "AW8-rCP5SVqnjpZ6qYVym7chGbZ2DAY6qeE9OdPZ_Z2rSt6LOkghM3OVvCGCqcA_gHzls--HYDFkti77",
                "client_secret": "EHiGn_1fbzg5SgGmTl7BEg7MFdzasg12qzJgkAySZ8npj6kL_SWXdoz41bpF_drEnTu_qW-R31VrRLAj" })
        payment=paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                  "payment_method": "paypal"},
                  "redirect_urls": {
                      "return_url":"http://127.0.0.1:8000/store/process/paypal",
                      "cancel_url":"http://127.0.0.1:8000/store"
                  },
                "transactions": [{
                  "item_list":{"items":items},
                  "amount": {
                    "total": str(total),
                    "currency": "INR"},
                  "description": "Mysterious Book order."}]})
        if payment.create():
                cart_instance=cart.get()
                cart_instance.payment_id=payment.id
                cart_instance.save()
                for link in payment.links:
                    if link.method=="REDIRECT":
                        redirect_url=str(link.href)
                        return redirect_url
        else:
                return reverse('order_error')
    else:
        return redirect ('index')

def checkout_stripe(cart,orders, token):
    stripe_api_key="sk_test_ITxk07qF3GQYJHgnBDjEZD9W"
    total=0
    for order in orders:
            total+=(order.book.Prize*order.quantity)
            status=True
            try:
                charge=stripe.Charge.create(
                               amount=int(total*100),
                               currency='INR',
                               description='A Django charge',
                               source=request.POST['stripeToken'])
                cart_instance=cart.get()
                cart_instance.payment_id=charge.id
                cart_instance.save()

            except stripe.error.CardError as e:
                status=False

            return status


def order_error(request):
    if request.user.is_authenticated():
        message="There is an issue in your payment process "
        context={'message':message}
        return render(request,'order_error.html',context)

    else:
        return redirect ('index')

def process_order(request,processor):
    if request.user.is_authenticated():
       if processor=="paypal":
           payment_id=request.GET.get('payment_id')
           cart=Cart.objects.filter(payment_id="payment_id")
           orders=BooksOrdered.objects.filter(cart=cart)
           total=0
           for order in orders:
               total +=(order.book.Prize*order.quantity)

           context={'cart':orders,
                   'total':total,}
           return redirect (request,'process_order.html',context)
       elif processor=="stripe":
           return JsonResponse({'redirect_url':reverse('complete_order',args=['strip'])})

    else:
        return redirect ('index')


def completed_order(request,processor):
    if request.user.is_authenticated():
        cart=Cart.objects.filter(user=request.user,active=True)
        if processor=="paypal":
           payment=paypalrestsdk.Payment.find(cart.payment_id)
           if payment.execute({"payer_id":payment.payer.payer_info.payer_id}):
               message="Success! Your Order Has been placed successfully. Payment_ID:%s",{payment.id}
               cart.actice=False
               cart.order_date=timezone.now()
               cart.save()
           else:
               message="There is an issue in your payment process Error: %s, If your money got deducted they will be credited back with in 7 working days",{payment.error.message}
        elif processor=="strip":
            cart.actice=False
            cart.order_date=timezone.now()
            cart.save()
            message="Success! Your Order Has been placed successfully. Strip Payment_ID:%s",{cart.payment_id}
        else:
            message="Invalied Payment Mode"
        context={'message':message}
        return redirect (request,'order_completed.html',context)
    else:
        return redirect ('index')
