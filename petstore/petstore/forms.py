from django import forms
from .models import Review,Profile

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = Review
        fields = ['review','rating']
        widgets = {
            'review':forms.Textarea(attrs={'placeholder':'Write your review here...','rows':4}),
            'rating':forms.Select(attrs={'placeholder':'Select a rating'}),
        }


class ProfformCreating(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['image','location']


class ProfformEditing(forms.ModelForm):
    
    class Meta:
       model = Profile
       fields = ['image','location']
       
                