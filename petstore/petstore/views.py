from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Sum,Count
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.views import View
from petapp.models import Pet
from petstore.models import Review,Cart,Order,Profile,User
from django.urls import reverse
from petapp.forms import ItemForm
from petstore.forms import ReviewForm,ProfformCreating,ProfformEditing,Profile
from django.contrib.auth.forms import UserCreationForm



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()    
            return redirect('login')  # Redirect after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'petstore/register.html', {'form': form})

def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        
        user = authenticate(request,username = username,password=password)
        
        
        if user is None:
            
            messages.error(
                request,
                'Invalid login,try again'.format(user)
            )
            return redirect('login')
        
        elif user.is_superuser:
            login(request,user)     # Links the user to the current session
            messages.success(
                request,
                'Welcome Superuser {},you have been logged in  successfully'.format(user)
            )
            return redirect('pet_list')
            
        
        elif user is not None:              
            login(request,user)
            messages.success(
                request,
                ' Welcome {}, you have been logged in successfully'.format(user)
            )
            return redirect('pet_list')
       
    return render(request, 'petstore/login.html' )




def logout_view(request):
    
    if request.method == 'POST':
        user = request.user.username
        logout(request)
        messages.success(
                request,
                ' {}, you have been logged out successfully'.format(user)
            )
        return redirect('pet_list')
    
    return render(request,'petstore/logout.html')





def edit_pet(request, pk):
    pet = get_object_or_404(Pet, pk=pk)  # Get the specific pet by its primary key
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('pet_detail', pk=pet.pk)  # Redirect back to pet detail after saving
    else:
        form = ItemForm(instance=pet)
    return render(request, 'petstore/pet_edit.html', {'form': form, 'pet': pet})




def pet_review(request, pk):
    # Get the pet object
    pet = get_object_or_404(Pet, pk=pk)
    
    if request.method == 'POST':
        # Create a form instance with POST data
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            # Save the review instance but don't commit yet
            review = form.save(commit=False)
            review.pet = pet  # Assign the review to the pet
            review.user = request.user  # Optionally assign the user
            review.save()
            
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('pet_detail', pk= pet.pk)  # Redirect back to pet detail page
    else:
        # Initialize an empty form for GET requests
        form = ReviewForm()

    # Render the review template
    return render(request, 'petstore/pet_review.html', {'pet': pet, 'form': form})

def add_to_cart(request,pk):
    pet = get_object_or_404(Pet, pk=pk)
    cart_item,created = Cart.objects.get_or_create(user=request.user,pet=pet)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')  
  

def view_cart(request):
    
    cart_items = Cart.objects.filter(user=request.user)
    cart_data = []
    total_price = 0

    for item in cart_items:
        item_total = item.pet.price * item.quantity
        total_price += item_total
        cart_data.append({
            'item': item,
            'total': item_total,
        })

    return render(request, 'petstore/add_cart.html', {'cart_data': cart_data, 'total_price': total_price})


def update_cart(request, pk):
    
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, pk=pk , user=request.user)
        
        try:
            quantity = int(request.POST.get('quantity', 0))
            if 0 <= quantity <= 3:
                if quantity == 0:
                    cart_item.delete()
                    messages.success(request, f"'{cart_item.pet.name}' removed from your cart.")
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, f"Quantity for '{cart_item.pet.name}' updated to {quantity}.")
            else:
                messages.error(request, "Quantity must be between 0 and 3.")
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number.")
           
        return redirect('view_cart')

def payment(request):
    
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You need to log in to confirm the order.")
            return redirect('login')

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('view_cart')

        # Calculate total amount
        total_amount = sum(item.pet.price * item.quantity for item in cart_items)

        # Create the order
        order = Order.objects.create(user=user, total_amount=total_amount)
        order.cart_items.set(cart_items)
        order.save()

        # Clear the user's cart
        cart_items.delete()

        messages.success(request, f"Order #{order.id} has been placed successfully!")
        return redirect('pet_list')  # Replace with your success page

    return render(request, 'petstore/payment.html')


        
        
def update_cart(request,pk):
    
    if request.method == 'POST':
        
        cart_item = get_object_or_404(Cart,user = request.user, pk=pk)
                    
        try:
            quantity = int(request.POST.get('quantity',0))
            
            if 0 <= quantity <= 3:
                if quantity == 0:
                    cart_item.delete()
                    messages.success(request,f'Cart Item Deleted Successfully for {cart_item.pet.id} ')
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request,f'Quantity Updated Successfully for {cart_item.pet.id}')
            else:
                messages.error(request,'Quantity must be between 0 and 3 ')
        
        except ValueError:
            messages.error(request,'Invalid Quantiy,Please Enter in digits')
        
        return redirect('view_cart')
    

@login_required
def paypal_payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.pet.price * item.quantity for item in cart_items)

    if total_amount == 0:
        messages.error(request, "Your cart is empty!")
        return redirect('view_cart')

    context = {
        "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        "total_amount": total_amount,
    }
    return render(request, "petstore/paypal_payment.html", context)

@login_required
def payment_success(request):
    # Clear the cart after payment
    Cart.objects.filter(user=request.user).delete()
    messages.success(request, "Payment successful!")
    return redirect('pet_list')

@login_required
def payment_cancel(request):
    messages.error(request, "Payment was cancelled.")
    return redirect('view_cart')

def is_superuser(user):
    return user.is_superuser  # ✅ Just return True or False


@login_required
@user_passes_test(is_superuser)     
def sales_dashboard(request):
    total_revenue = Order.objects.filter(status="Completed").aggregate(Sum('total_amount'))['total_amount__sum'] or 0      

    best_selling_products = (
    Order.objects.filter(status="Completed")
    .values("cart_items__pet__name")  # Get pet names
    .annotate(total_sold=Sum("cart_items__quantity"))  # Sum quantities across orders
    .order_by("-total_sold")[:5]  # Top 5 products
    )

    
    product_names = [item["cart_items__pet__name"] for item in best_selling_products]
    product_sales = [item["total_sold"] for item in best_selling_products]
    
    return render(request,'petstore/dashboard.html',{
        'total_revenue':total_revenue,
        'best_selling_products': best_selling_products,
        'product_names':product_names,
        'product_sales': product_sales,
    })

@login_required
def Profile_Create(request):
    user = request.user  # Get the logged-in user

    # Try to fetch the existing profile or create one if it doesn't exist
    prof, created = Profile.objects.get_or_create(user=user)  

    if request.method == "POST":
        form = ProfformCreating(request.POST, request.FILES, instance=prof)  # ✅ Use instance=prof
        if form.is_valid():
            form.save()  # ✅ Updates the existing profile instead of creating a new one
            messages.success(request,f'Profile {user} Updated Successfully')
            return redirect("profile_view")  # Redirect after saving

    else:
        form = ProfformCreating(instance=prof)  # ✅ Prefill form with existing data

    context = {"form": form, "prof": prof}
    return render(request, "petstore/prof_create.html", context)
    
    
@login_required
def profile_view(request):
    try:
        profile = Profile.objects.get(user = request.user)  
    except Profile.DoesNotExist():
        return redirect('profile')
    
    return render(request,'petstore/prof_view.html',{'profile':profile})

      
    
    
    
    
    
    
    
                    
            
        
        
                
        
        
        
          
    
         
        
            
            
                 
        
        
        
                
        
         
            

 
 
        
        
            
        
            
    
          
    
        
    
        
        
    
      
            
            
            
            
            
         




    

        
        
        
    
    
        
            
            
            
            
        
    
    
        
        
        
        
        

        


    
        
        
        
                
        
        
        
        
           
            
        
        
            
        
