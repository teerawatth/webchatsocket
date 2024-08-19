from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Message, Product
from django.contrib.auth.models import User
from django.utils.text import slugify
from .forms import ProductForm, RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from django.db import IntegrityError  # เพิ่มบรรทัดนี้เพื่อ import IntegrityError


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def create_or_redirect_room(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    seller = product.seller
    customer = request.user

    slug = slugify(f'chat-about-{product.name}-between-{seller.username}-and-{customer.username}')

    try:
        room = Room.objects.get(slug=slug)
    except Room.DoesNotExist:
        room = Room.objects.create(
            product=product,
            seller=seller,
            customer=customer,
            name=f'Chat about {product.name} between {seller.username} and {customer.username}',
            slug=slug
        )

    return redirect('room', slug=room.slug, username=seller.username, product_id=product.id)

def room(request, slug, username, product_id):
    seller = get_object_or_404(User, username=username)
    product = get_object_or_404(Product, id=product_id)
    customer = request.user

    # ตรวจสอบว่ามีห้องแชทนี้แล้วหรือไม่
    room = Room.objects.filter(slug=slug, seller=seller, product=product).first()

    if not room:
        room = Room.objects.create(
            seller=seller,
            customer=customer,
            product=product,
            name=f'Chat about {product.name} between {seller.username} and {customer.username}',
            slug=slug
        )

    # ดึงข้อความทั้งหมดในห้องแชทนี้
    messages = room.message_set.order_by('created_on')

    return render(request, "room.html", {
        "room": room,
        "product": product,
        "messages": messages,
    })

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_add.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You are now logged in as {username}.')
                return redirect('product_list')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def chat_list(request):
    user = request.user
    rooms = Room.objects.filter(seller=user) | Room.objects.filter(customer=user)
    rooms = rooms.distinct()  # ลบรายการที่ซ้ำกัน

    return render(request, 'chat_list.html', {'rooms': rooms})
