from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    pet = models.ForeignKey('petapp.Pet',on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User,on_delete=models.CASCADE, null= True,blank=True)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    created_at = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self):
        return f"Review for{self.pet.name} by {self.user.username if self.user else 'Customer'}"
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="cart_items")
    pet = models.ForeignKey('petapp.Pet', on_delete= models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.pet.name} (x{self.quantity}) - {self.user.username}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    cart_items = models.ManyToManyField('petstore.Cart', related_name="order_items")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ],
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    

class Profile(models.Model):
    
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    image = models.ImageField(default='profilepic.jpg', upload_to = 'pictures/profilepic')
    location = models.CharField(default='location',max_length=100)
    user_type = models.CharField(max_length=50)
    
    def save(self,*args, **kwargs):
        if self.user.is_superuser:
            self.user_type = 'superuser'
        elif self.user.is_staff:
            self.user_type = 'staff'
        else:
            self.user_type = 'customer'        

        super().save(*args, **kwargs)  # ✅ Forwards extra arguments safely
                                        # ✅ Saves the Profile instance
    
    def __str__(self):
        return f'{self.user.username}'

    
    
       
     



    
     
    
    
    
    