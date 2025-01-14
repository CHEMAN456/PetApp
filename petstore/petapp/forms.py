from django import forms 
from petapp.models import Pet

class ItemForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['petapp_owner','added_by','animal_type','image','name','price','species','breed','age','gender','description']