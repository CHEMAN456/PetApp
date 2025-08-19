from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from petapp.models import Pet
from django.contrib.messages import get_messages
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import force_authenticate

class ViewTests(TestCase):
    def setUp(self):
        for i in range(5):
            image_file = SimpleUploadedFile(f"test{i}.jpg", b"file_content", content_type="image/jpeg")
            self.user = User.objects.create_user(
            username=f"testuser{i}",
            password="password1234"
            )
            pet = Pet.objects.create(
                petapp_owner = self.user,
                animal_type="D" if i % 2 == 0 else "C",
                image=image_file,
                name=f"Pet {i}",
                price=800 + (i * 100),
                species="Dog" if i % 2 == 0 else "Cat",
                breed="Labrador" if i % 2 == 0 else "Persian",
                age=2 + i,
                gender="male" if i % 2 == 0 else "female",
                description="Test pet description"
            )
            if i == 2:  # Save the first one for detail view test
                self.dog1 = pet
            elif i == 4:
                self.dog2 = pet
            elif i == 0:
                self.dog = pet
            elif i == 1:
                self.cat1 = pet            
            else:
                self.cat2 = pet
                
        
    def test_pet_list_view_pagination(self):
        
        response = self.client.get(reverse('pet_list'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'petapp/pet_list.html')
        
        self.assertEqual(len(response.context['page_obj']),3)
        
        response_page_2 = self.client.get(reverse('pet_list') + '?page=2')
        self.assertEqual(len(response_page_2.context['page_obj']), 2)
      
    def test_pet_detail_view_exists(self):
        url = reverse('pet_detail',args=[self.dog1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,self.dog1.name)
    
    def test_pet_detail_view(self):
        url = reverse('pet_detail',args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)
        
    def test_dog_list_view(self):
        url = reverse('dog-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,self.dog1.name)         
        self.assertContains(response,self.dog2.name)   
          
    def test_cat_list_view(self):
        url = reverse('cat_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,self.cat1.name)         
    
    def test_pet_range_default_values(self):
        url = reverse('pet-range')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for pet_name in ["Pet 0","Pet 1","Pet 2"]:
            self.assertContains(response, pet_name)
    
    def test_pet_range_custom_values(self):
        url = reverse('pet-range') + '?r1=1000&r2=1500'
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response,"Pet 1")    
        self.assertContains(response,"Pet 2")
        self.assertContains(response,"Pet 4")
    
    def test_pet_delete_get_request(self):
        url = reverse('delete', args=[self.dog1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petapp/pet_delete.html')
        self.assertContains(response, "Pet 2")
    
    def test_pet_delete_post_request(self):
        url = reverse('delete', args=[self.dog1.pk])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('pet_list'))
        self.assertFalse(Pet.objects.filter(pk=self.dog1.pk).exists())
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Pet Deleted Successfully" in str(m) for m in messages))
    
class CreateItemViewTestCase(TestCase):
    def setUp(self):
        # Create test user once for all test methods
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        ) 
        
    def test_create_item_get(self):
        url = reverse('add_item')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petapp/additem.html')
        
    def test_create_item_post_valid(self):
        url = reverse('add_item')
        
        # Create test image
        from io import BytesIO
        from PIL import Image
        image = BytesIO()
        Image.new("RGB", (1, 1)).save(image, 'JPEG')
        image.seek(0)
        image_file = SimpleUploadedFile(
            "test.jpg",
            image.read(),
            content_type="image/jpeg"
        )
        
        # Test data
        pet_name = "New Pet3"
        data = {
            "petapp_owner": self.user.id,
            "added_by": "user",
            "animal_type": "D",
            "image": image_file,
            "name": pet_name,
            "price": 2500,
            "species": "Dog",
            "breed": "Labrador",
            "age": 3,
            "gender": "male",
            "description": "Cute Pet"
        }
        
        # Login user
        self.client.force_login(self.user)
        
        # Make request
        response = self.client.post(url, data, follow=True)
        
        # Debug output
        print("Status code:", response.status_code)
        if hasattr(response, 'context') and 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Pet.objects.filter(name=pet_name).exists(),
            f"Pet with name '{pet_name}' should exist but doesn't"
        )
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Pet Added Successfully" in str(m) for m in messages),
            "Success message not found"
        )    
    
    def test_create_item_post_invalid(self):
        url = reverse('add_item')
        
        data = {
            "name":"",
        }    
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'petapp/additem.html')
        self.assertFalse(Pet.objects.exists())

class PetListCreateAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )
        self.image_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.pet1 = Pet.objects.create(
            petapp_owner=self.user,
            added_by="testuser",
            animal_type="D",  # 'D' for Dog
            image=self.image_file,
            name="Pet A",
            price=1200,
            species="Dog",
            breed="Golden Retriever",
            age=3,
            gender="male",
            description="Friendly and playful golden retriever"
        ) 
        self.pet2 = Pet.objects.create(
            petapp_owner=self.user,
            added_by="testuser",
            animal_type="C",  # 'C' for Cat
            image=self.image_file,
            name="Pet B",
            price=900,
            species="Cat",
            breed="Persian",
            age=2,
            gender="female",
            description="Calm and affectionate Persian cat"
        )      
        self.url = reverse('pet-list-create')   
    
    def test_list_pets(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)     
    
    def test_create_pet(self):
        from io import BytesIO
        from PIL import Image
        image = BytesIO()
        Image.new("RGB", (1, 1)).save(image, 'JPEG')
        image.seek(0)
        image_file = SimpleUploadedFile(
            "test.jpg",
            image.read(),
            content_type="image/jpeg"
        )
        
        data = {
        "petapp_owner": self.user.id,
        "added_by": "testuser",
        "animal_type": "D",  # 'D' for Dog, 'C' for Cat
        "image": image_file,
        "name": "New Pet",
        "price": 1500,
        "species": "Dog",
        "breed": "Labrador",
        "age": 3,
        "gender": "male",  # must match the choice key
        "description": "A playful Labrador, great with kids."
    }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Pet.objects.filter(name="New Pet").exists())

class PetRetrieveUpdateDestroyAPITestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="owner", password="password123")
        self.pet = Pet.objects.create(petapp_owner= self.user,added_by="owner",
                                    animal_type = "C" , name="Whiskers", species="Cat", price=2000,
                                    image = SimpleUploadedFile(name="test_image1.jpg",content=b"file_content",content_type="image/jpeg"),
                                     age = 4, gender = "female",description = "Loyal Persian Cat",breed="Persian"                           
                                    )
        self.url = reverse('pet_detail_api', args=[self.pet.pk]) 
        
    def test_retrieve_pet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Whiskers")            
    
    def test_update_pet(self):
        
        from io import BytesIO
        from PIL import Image
        
        image = BytesIO()
        Image.new('RGB', (1, 1)).save(image, 'JPEG')
        image.seek(0)
        image_file = SimpleUploadedFile(
        "test_image.jpg",
        image.read(),
        content_type="image/jpeg"
    )
        data = {  # Assuming default user with ID 1 exists
                "petapp_owner":self.user.id,
                "added_by": "admin",
                "image":image_file,
                "animal_type": "D",  # 'D' for Dog, 'C' for Cat
                "name": "Updated Pet",
                "price": 2500,
                "species": "Dog",
                "breed": "Golden Retriever",
                "age": 4,
                "gender": "male",
                "description": "A friendly golden retriever who loves to play." }
        
        response = self.client.patch(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Updated Pet")
    
    def test_delete_pet(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)   
        self.assertFalse(Pet.objects.filter(pk=self.pet.pk).exists())       