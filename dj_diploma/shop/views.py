from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Article, Category, Product, Review, Customer, Order, ProductsInOrder, Section
from .forms import ReviewForm, CustomerLoginForm, CustomerRegisterForm

def home_view(request):
    articles = Article.objects.order_by('created')
    context = {
        'articles': articles,
    }
    return render(request, 'index.html', context)

def product_list_view(request, section_slug=None, category_slug=None):
    products = Product.objects.all()
    category_name = 'Все товары'

    if section_slug and category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = list(category.products.all())
        category_name = category.name.capitalize()

    page = request.GET.get('page')
    paginator = Paginator(products, 5)
    products_paginate = paginator.get_page(page)

    context = {
        'category_name': category_name,
        'products_paginate': products_paginate,
    }

    return render(request, 'product-list.html', context)

def product_view(request, section_slug, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(category.products, slug=slug)
    reviews = product.reviews.all()
    name = request.user.username or None
    form = ReviewForm(initial={'name': name})

    for review_ in reviews:
        review_.rating_view = '\u2605' * review_.rating

    if request.method == 'POST':
        form = ReviewForm(request.POST or None)

        if form.is_valid():
            data = form.cleaned_data

            review = Review(
                product=product,
                **data
            )
            review.save()

            return redirect('product', product.category.section.slug, product.category.slug, product.slug)

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }

    return render(request, 'product.html', context)

def customer_check(user):
    return Customer.objects.filter(user=user).first()


@login_required(login_url='login')
@user_passes_test(customer_check, login_url='login')
def create_or_update_cart_view(request):
    next_ = request.GET.get('next')

    if request.method == 'POST':
        product_pk = request.GET.get('product_id')

        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session.get('cart')

        if product_pk in cart:
            cart[product_pk]['quantity'] += 1

        else:
            cart[product_pk] = {
                'quantity': 1
            }

    request.session.modified = True

    return redirect(next_)


@login_required(login_url='login')
@user_passes_test(customer_check, login_url='login')
def cart_view(request):
    next_ = request.GET.get('next')

    context = {
        'next': next_,
    }

    cart = request.session.get('cart', None)

    if cart:
        products = {}
        product_list = Product.objects.filter(pk__in=cart.keys()).values('id', 'name', 'description')

        for product in product_list:
            products[str(product['id'])] = product

        for key in cart.keys():
            cart[key]['product'] = products[key]

        context['cart'] = cart

    return render(request, 'cart.html', context)

def login_view(request):
    form = CustomerLoginForm(request.POST or None)
    next_ = request.GET.get('next')
    print(next_)

    if form.is_valid():
        data = form.cleaned_data

        email = data['email']
        password = data['password']

        user = User.objects.get(email=email)
        username = user.username

        user = authenticate(username=username, password=password)

        login(request, user=user)
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or 'home'

        request.session['cart'] = {}

        return redirect(redirect_path)

    context = {'form': form}

    return render(request, 'login.html', context)


@login_required(login_url='login')
def logout_view(request):
    try:
        del request.session['cart']
    except KeyError:
        pass

    logout(request)
    return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        register_form = CustomerRegisterForm(request.POST)

        if register_form.is_valid():
            register_form.save()
            return redirect('login')
    else:
        register_form = CustomerRegisterForm()

    context = {'form': register_form}

    return render(request, 'signup.html', context)


@login_required(login_url='login')
def order_view(request):
    if request.method == 'POST':
        customer_pk = request.user.customer.pk
        customer = Customer.objects.get(pk=customer_pk)

        cart = request.session['cart']

        if len(cart) > 0:
            order = Order.objects.create(customer=customer)

            for key, value in cart.items():
                product = Product.objects.get(pk=key)
                quantity = value['quantity']
                ProductsInOrder.objects.create(order=order, product=product, quantity=quantity)

            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, 'Заказ принят')

    return redirect('cart')