from django.shortcuts import render, redirect
from django.contrib import messages
from storeapp.models import Customer, Seller, Product, Product_category, Order
from storeapp.models import Seller
import bcrypt
from utils.views import Cart


def index(request):
    return redirect('/home')


def home(request):
    print(request.session)
    context = {}
    if 'seller_id' in request.session:
        seller = Seller.objects.get(id=request.session['seller_id'])
        if seller:
            context = {
                'seller': seller,
                'sellers': Seller.objects.all,
                'products': Product.objects.all()
            }
    if 'customer_id' in request.session:
        user = Customer.objects.get(id=request.session['customer_id'])
        if user:
            context = {
                'user': user,
                'sellers': Seller.objects.all,
                'products': Product.objects.all()
            }
    else:
        context = {
            'seller': None,
            'user': None,
            'sellers': Seller.objects.all,
            'products': Product.objects.all()
        }
    return render(request, 'store/home.html', context)


def view_customer_login(request):
    return render(request, 'login/login.html')


def view_seller_login(request):
    return render(request, 'login/seller_signup.html')

def create_customer(request):
    errors = Customer.objects.validate_user(request)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        print(errors)
        return redirect('/login_customer')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    address = request.POST.get('address')
    password = request.POST.get('password')
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    customer = Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        mobile=mobile,
        email=email,
        address=address,
        password=password_hash
    )
    customer.save()
    request.session['customer_id'] = customer.id
    request.session.modified = True 
    return redirect('/')


def login_customer(request):
    errors = Customer.objects.validate_user_login(request)
    if len(errors) > 0:
        print(errors)
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/login_customer')
    email = request.POST.get('email')
    customer = Customer.objects.get(email=email)
    request.session['customer_id'] = customer.id
    request.session.modified = True 
    return redirect('/')


def login_seller(request):
    errors = Seller.objects.validate_seller_login(request)
    if len(errors) > 0:
        print(errors)
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/login_seller')
    email = request.POST.get('email')
    seller = Seller.objects.get(email=email)
    request.session['seller_id'] = seller.id
    request.session.modified = True 

    return redirect('/seller')


def create_seller(request):
    errors = Seller.objects.validate_seller(request)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        print(errors)
        return redirect('/login_seller')
    seller_name = request.POST.get('seller_name')
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    description = request.POST.get('description')
    city = request.POST.get('city')
    password = request.POST.get('password')
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_seller = Seller.objects.create(
        name=seller_name,
        mobile=mobile,
        email=email,
        description=description,
        city=city,
        password=password_hash
    )
    new_seller.save()
    request.session['seller_id'] = new_seller.id
    request.session.modified = True 
    return redirect('/seller')


def create_product(request):
    seller_id = request.session['seller_id']
    seller = Seller.objects.get(id=seller_id)
    category_id = request.POST.get('category')
    category = Product_category.objects.get(id=category_id)
    name = request.POST.get('name')
    price = request.POST.get('price')
    quantity = request.POST.get('quantity')
    description = request.POST.get('description')
    sale = request.POST.get('sale')
    image = request.FILES.get('image')
    new_product = Product.objects.create(
        name=name,
        quantity=quantity,
        category=category,
        description=description,
        price=price,
        sale=sale
    )
    if image:
        new_product.image = image
    new_product.seller.add(seller)
    new_product.save()
    return redirect('/seller')


def view_product(request, id):
    product = Product.objects.get(id=id)
    context = {
        'product': product,
        'cart': Cart(request)

    }
    return render(request, 'store/product.html', context)


def view_seller_profile(request, id):
    context = {
        'seller': Seller.objects.get(id=id)
    }
    return render(request, 'store/seller_profile.html', context)

def best_sellers(request):
    context = {
        'sellers': Seller.objects.all()
    }
    return render(request, 'store/best_sellers.html', context)

def all_products(request):
    context = {
        'sellers': Seller.objects.all(),
        'all_products': Product.objects.all(),
    }
    return render(request, 'store/all_products.html', context)

def view_sales(request):
    sales = Product.objects.filter(sale__gt=10)
    sellers = Seller.objects.all()
    context = {
        'products_on_sales': sales,
        'sellers': sellers
    }
    return render(request, 'store/sales.html', context)

def customer_profile(request):
    if 'customer_id' in request.session:
        customer = Customer.objects.get(id=request.session['customer_id'])
        context = {
            'customer': customer,
            'orders': customer.orders.all(),
        }
        return render(request, 'store/customer.html', context)
    else:
        return redirect('/customer_login')



def seller_profile(request):
    if 'seller_id' in request.session:
        seller = Seller.objects.get(id=request.session['seller_id'])
        context= {
                'seller': seller,
                'categories': Product_category.objects.all()
            }
        return render(request, 'store/seller.html', context)
    else:
        return redirect('/login_seller')




def add_profile_picture(request):
    if request.FILES.get('seller_image'):
        seller = Seller.objects.get(id=request.session['seller_id'])
        seller.picture= request.FILES.get('seller_image')
        seller.save()
        print(seller.picture.url)
    
    return redirect(request.META.get('HTTP_REFERER'))



""" cart functionality for adding items clearing the cart,
    increase, decrease Items and calculate the order 
"""

def add_to_cart(request, id):
    quantity = request.POST.get('quantity')
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product, quantity)

    return redirect(request.path)


def item_clear(request, id):
    cart = request.session
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart")


def update_cart(request):
    cart = Cart(request)
    quantity = request.post.get(quantity)
    product = Product.POST.get(id=request.POST.get('product_id'))



def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("/cart")


def show_cart(request):
    cart = Cart(request)
    customer_id = request.session['customer_id']
    customer = Customer.objects.get(id=customer_id)
    context = {
        'cart': cart,
        'total': cart.get_total_price(),
        'items_in_cart': len(cart),
        'customer': customer
    }
    return render(request, 'store/cart.html', context)


# @login_required
def place_order(request):
    cart = Cart(request)
    customer_id = request.session['customer_id']
    customer = Customer.objects.get(id=customer_id)
    total = [item.quantity * item.price for item in cart.values()]
    new_order = Order.objects.create(
        customer=customer,
        total=sum(total),
    )
    for item in cart.cart:
        new_order.order_items.add(item)
    new_order.save()
    customer.orders.add(new_order)
    return redirect('/customer_profile')


def about_page(request):
    return render(request, 'store/about.html')


def logout(request):
    request.session.clear()
    return redirect('/')

def test(request):
    return render(request, 'store/test.html')