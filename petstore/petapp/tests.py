from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Pet

# Create your tests here.

class PetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser",password="password123")
        
        self.pet = Pet.objects.create(
            petapp_owner = self.user,
            added_by = "testuser",
            animal_type = "D",
            image = "media/dog.jpg",
            name = "Buddy",
            price = 5000,
            species = "Dog",
            breed = "Labrador",
            age = 3,
            gender = "male",
            description = "a friendly labarador"
            
        )
    
    def test_pet_creation(self):
        
        self.assertEqual(self.pet.name,"Buddy")
        self.assertEqual(self.pet.price,5000)
        self.assertEqual(self.pet.gender,"male")
        self.assertEqual(self.user,User.objects.get(username="testuser"))
        self.assertEqual(self.pet.added_by,"testuser")
        
    def test_str_method(self):
        
        self.assertEqual(str(self.pet),"Buddy(Dog)")  
        
    def test_animal_type_choices(self):
        
        self.assertEqual(self.pet.animal_type,"D")     
            
            
        