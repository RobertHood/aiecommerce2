from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('logout/', views.logout, name='logout'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/cart/add/', views.cart_add, name='cart_add'),
    path('api/cart/remove/', views.cart_remove, name='cart_remove'),
    path('api/cart/update/', views.cart_update, name='cart_update'),
]
