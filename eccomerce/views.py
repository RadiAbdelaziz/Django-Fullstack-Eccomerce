from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Brand, Tag , Cart , CartItem, Product , Order, OrderItem , Product, Category
from .forms import ProductForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
# View to list all products (with search/filter)
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category_id:
        products = products.filter(category__id=category_id)

    return render(request, 'eccomerce/product_list.html', {'products': products , 'categories': categories })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'eccomerce/product_detail.html', {'product': product, 'related': related})

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            form.save_m2m()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'eccomerce/product_form.html', {'form': form})

# Update product
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'eccomerce/product_form.html', {'form': form})


def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'eccomerce/product_confirm_delete.html', {'product': product})

def show_products (req):
    return render (req , "eccomerce/show_products.html")

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
        item.save()

    return redirect('view_cart')

def update_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
    return redirect('view_cart')

def remove_from_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.delete()
    return redirect('view_cart')

def view_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    return render(request, 'eccomerce/cart_item.html', {'cart': cart})


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        return redirect('view_cart')

    if request.method == 'POST':
        address = request.POST['address']
        payment_method = request.POST['payment_method']

        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method=payment_method,
            status='Pending'
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock_quantity -= item.quantity
            item.product.save()

        cart.items.all().delete()
        return render(request, 'eccomerce/order_confirmation.html', {'order': order})

    return render(request, 'eccomerce/checkout.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def sales_history(request):
    products = Product.objects.filter(seller=request.user)
    order_items = OrderItem.objects.filter(product__in=products).select_related('order')
    return render(request, 'sales_history.html', {'order_items': order_items})

from django.contrib.auth.decorators import user_passes_test

def is_admin_or_seller(user):
    return user.is_staff or Product.objects.filter(seller=user).exists()

@user_passes_test(is_admin_or_seller)
def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Processing', 'Shipped', 'Delivered']:
            order.status = new_status
            order.save()
        return redirect('sales_history')

    return render(request, 'update_order_status.html', {'order': order})


def homepage(request):
    featured_products = Product.objects.filter(is_featured=True)[:5]
    latest_products = Product.objects.order_by('-id')[:8]
    best_sellers = Product.objects.order_by('-rating')[:8]  # Simulated best sellers
    featured_categories = Category.objects.all()[:4]

    return render(request, 'eccomerce/homepage.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'best_sellers': best_sellers,
        'featured_categories': featured_categories,
    })

from django.db.models import Q

def product_search(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(
        Q(title__icontains=query) |
        Q(tags__name__icontains=query) |
        Q(brand__name__icontains=query)
    ).distinct()
    
    return render(request, 'eccomerce/search_results.html', {'results': results, 'query': query})



@staff_member_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    featured_products = Product.objects.filter(is_featured=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    
    context = {
        'total_products': total_products,
        'approved_products': approved_products,
        'featured_products': featured_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'eccomerce/admin_dashboard.html', context)