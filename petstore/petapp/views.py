from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.core.paginator import Paginator
from rest_framework import generics
from .serializers import Petserializer
from django.http import Http404
from django.views import View
from django.contrib import messages
from .models import Pet
from .forms import ItemForm

# Create your views here.

def home(request):
    
    return HttpResponse('This is a function based view')

class MyView(View):
    
    def get(self,request):
        return HttpResponse('Hello from class based view')
    
    
def pet_list(request):
    mymodels = Pet.objects.all().order_by('price')
    
    paginator = Paginator(mymodels,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request,'petapp/pet_list.html',{'page_obj':page_obj})


def pet_detail_view(request,pk=None,*args, **kwargs):
    
    qs = Pet.objects.filter(id=pk)
    if qs.exists() and qs.count() == 1:
        instance = qs.first()
    else:
        raise Http404("Pet doesn't exists")
    
    context = {
        'pet':instance
    }
    
    return render(request,'petapp/pet_detail.html',context)

def dog_list_view(request):
    dogs = Pet.pets.dog_list().order_by('price')
    
    paginator = Paginator(dogs,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'petapp/pet_list.html',{'page_obj':page_obj})

def cat_list_view(request):
    cats = Pet.pets.cat_list().order_by('price')
    
    paginator = Paginator(cats,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'petapp/pet_list.html',{'page_obj':page_obj})


def pet_range_view(request):
    r1 = request.GET.get('r1', 0)
    r2 = request.GET.get('r2', 20000)
    items_per_page = request.GET.get('per_page') or 3 

    try:
        r1, r2 = int(r1), int(r2)
        items_per_page = int(items_per_page)
    except ValueError:
        r1, r2, items_per_page = 0, 20000, 3

    pet_range = Pet.pets.get_pets_price_range(r1, r2).order_by('price','name')
    paginator = Paginator(pet_range, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'petapp/pet_list.html', {
        'page_obj': page_obj,
        'request': request  # Pass request explicitly to the template
    })


def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST,request.FILES)
        
        if form.is_valid():
            pet=form.save(commit=False)
            pet.save()
            messages.success(
                request,
                ' {}, Pet Added Successfully'.format(pet.name)
            )
            return redirect('pet_list')  # Redirect to a success page after saving
    else:
        form = ItemForm()
    return render(request, 'petapp/additem.html', {'form': form})  # Ensure you're rendering a template or returning an HttpResponse


def pet_delete(request,pk=None):
    
    pet = Pet.objects.get(pk=pk)
    
    if request.method == 'POST':
        pet.delete()
        messages.success(
            request,
            '{},Pet Deleted Successfully'.format(pet.name)
            
        )
        return redirect('pet_list')

    context = {
        'pet':pet     
    }
    return render(request,'petapp/pet_delete.html',context)


class PetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = Petserializer


class PetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pet.objects.all() 
    serializer_class = Petserializer   
            









        
          
          
        
    
    
    
    
         
        

    
            
            

    
        
    
    


    
    
    
         
    
        
           

        
    
        
    
    
    
    
    
    
    
                
        
    
    
           
        
         
    