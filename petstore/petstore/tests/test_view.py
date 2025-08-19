from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from petapp.models import Pet
from petstore.forms import ReviewForm
from petstore.models import Review
from petapp.forms import ItemForm
 
class RegisterViewTestCase(TestCase):
    def test_register_get(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petstore/register.html')
    
    def test_register_post_valid(self):
        url = reverse('register')
        data = {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!"
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('login'))    
        self.assertTrue(User.objects.filter(username="newuser").exists())
    
    def test_register_post_invalid(self):
        url = reverse('register')
        data = {
            "username": "baduser",
            "password1": "pass",
            "password2": "mismatch"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petstore/register.html')
        self.assertFalse(User.objects.filter(username="baduser").exists())
        
class LoginViewTestCase(TestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        self.super_user = User.objects.create_superuser(
            username="admin",
            password="adminpass123"
        )  
        self.client.login(username="testuser", password="testpass123")
        
    def test_login_get(self):
        url = reverse('login')              
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petstore/login.html')
        
    def test_login_post_invalid(self):
        url = reverse('login')
        data = {"username": "wrong", "password": "wrong"}
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('login'))    
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid login" in str(m) for m in messages))
    
    def test_login_post_normal_user(self):
        url = reverse('login')
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('pet_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Welcome" in str(m) for m in messages))
    
    def test_login_post_super_user(self): 
        url = reverse('login')
        data = {"username": "admin", "password": "adminpass123"}
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('pet_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Welcome Superuser" in str(m) for m in messages))      

    def test_logout_get_request(self):
        url = reverse('logout')
        response = self.client.get(url)  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petstore/logout.html')
        self.assertContains(response, "logout")  # Verify template content
        
    def test_logout_post_request(self):
        url = reverse('logout')
        self.assertTrue('_auth_user_id' in self.client.session)     
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('pet_list'))
        self.assertFalse('_auth_user_id' in self.client.session)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("logged out successfully" in str(m) for m in messages))
    
    def test_logout_message_contains_username(self):
        url = reverse('logout')
        response = self.client.post(url, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("testuser" in str(m) for m in messages),
            f"Expected username in message. Got: {[str(m) for m in messages]}"
        )
        
class PetEditReviewViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        
        self.pet = Pet.objects.create(
            petapp_owner=self.user,
            animal_type = 'D',
            name='Test Pet',
            added_by='user',
            price=1000,
            species='Dog',
            breed='Labrador',
            age=3,
            gender='male',
            description='Test description',
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )
        
        self.valid_edit_data = {
            'petapp_owner' : self.user.id,
            'animal_type' : 'D',
            'added_by':'user',
            'name': 'Updated Pet',
            'price': 1500,
            'species': 'Dog',
            'breed': 'Golden Retriever',
            'age': 4,
            'gender': 'female',
            'description': 'Updated description'
        }
        
        self.valid_review_data = {
            'rating': 5,
            'review': 'Great pet!'
        }
        
    def test_edit_pet_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit', args=[self.pet.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)        
        self.assertTemplateUsed(response, 'petstore/pet_edit.html')
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertEqual(response.context['pet'], self.pet)
        
    def test_edit_pet_post_valid(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit', args=[self.pet.pk])
        print(url) 
        response = self.client.post(url, self.valid_edit_data, follow=True)
        # Debug output
        if hasattr(response, 'context') and 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        self.pet.refresh_from_db()   
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.pet.name, 'Updated Pet')
        self.assertRedirects(response, reverse('pet_detail', args=[self.pet.pk]))
            
    def test_edit_pet_post_invalid(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('edit', args=[self.pet.pk])   
        invalid_data = self.valid_edit_data.copy() 
        invalid_data['name'] = ''
        
        response = self.client.post(url, invalid_data)

        # Make sure page reloaded instead of redirect
        self.assertEqual(response.status_code, 200)

    # Access form directly
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('This field is required.', form.errors['name'])
            
    def test_edit_pet_unauthenticated(self):
        url = reverse('edit', args=[self.pet.pk])
        response = self.client.get(url)
    
        # Should return 302 redirect
        self.assertEqual(response.status_code, 302)
    
    # Get the actual redirect URL from response
        actual_redirect = response.url
        print(f"Actual redirect: {actual_redirect}")
    
    # Verify it contains both the login URL and next parameter
        login_url = reverse('login')
        self.assertIn(login_url, actual_redirect)
        self.assertIn(f"?next={url}", actual_redirect)
        
        # Pet Review Tests
    def test_pet_review_get(self):
        self.client.login(username='testuser', password='testpass123') 
        url = reverse('review', args=[self.pet.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petstore/pet_review.html')
        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertEqual(response.context['pet'], self.pet)
        
    def test_pet_review_post_valid(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('review', args=[self.pet.pk])
        response = self.client.post(url, self.valid_review_data, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('pet_detail', args=[self.pet.pk]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("submitted successfully" in str(m) for m in messages))
        
    def test_pet_review_post_invalid(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('review', args=[self.pet.pk])
        invalid_data = self.valid_review_data.copy()
        invalid_data['rating'] = 6 
    
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, 200)
    
    # Access form directly from context
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('Select a valid choice', str(form.errors['rating']))

    
    def test_pet_review_unauthenticated(self):
        url = reverse('review', args=[self.pet.pk])
        response = self.client.post(url, self.valid_review_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to login        