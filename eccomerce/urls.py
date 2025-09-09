from django.urls import path
from . import views

urlpatterns = [
    path("product" , views.product_list , name="product_list"),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/new/', views.create_product, name='create_product'),
    path('product/<int:pk>/edit/', views.update_product, name='update_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('sales/', views.sales_history, name='sales_history'),
    path('order/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('', views.homepage, name='homepage'),
    path('search/', views.product_search, name='product_search'),


]