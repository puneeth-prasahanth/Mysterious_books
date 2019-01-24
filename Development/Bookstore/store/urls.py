from django.conf.urls import  url
from . import views

urlpatterns = [url(r'^$', views.store,name='index'),
               url(r'^book/(\d+)', views.book_detailes,name='book_detailes'),
               url(r'^cart/', views.cart,name='cart'),
               url(r'^add/(\d+)', views.add_to_cart,name='add_to_cart'),
               url(r'^remove/(\d+)', views.remove_from_cart,name='remove_from_cart'),
               url(r'^order_error/', views.order_error,name='order_error'),
               url(r'^checkout/(\w+)', views.checkout,name='checkout'),
               url(r'^processor/(\w+)', views.process_order,name='process_order'),
               url(r'^completed_order/(\w+)', views.completed_order,name='completed_order'),
               ]
