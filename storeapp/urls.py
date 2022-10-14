from django.urls import path
from storeapp import views


urlpatterns = [
     path('', views.home),
     path('login_customer', views.view_customer_login),
     path('customer_login', views.login_customer),
     path('signup_customer', views.create_customer),
     path('login_seller', views.view_seller_login),
     path('seller_login', views.login_seller),
     path('seller_signup', views.create_seller),
     path('create_product', views.create_product),
     path('all_products', views.all_products),
     path('view_product/<int:id>', views.view_product),
     path('seller', views.seller_profile),
     path('seller/<int:id>', views.view_seller_profile),
     path('best_sellers', views.best_sellers),
     path('customer_profile', views.customer_profile),
     path('sales', views.view_sales),
     path('add_profile_picture', views.add_profile_picture),
     # ========= cart =========
     path('cart', views.show_cart),
     path('add_to_cart', views.add_profile_picture),
     path('update_cart',views.update_cart),
     path('cart_item_clear/<int:id>/', views.item_clear),
     path('cart_cart_clear/', views.cart_clear),
     path('place_order', views.place_order),
     path('about', views.about_page),
     path('logout', views.logout),
     path('test', views.test)
     ]
