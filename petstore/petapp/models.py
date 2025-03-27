from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class PetsQuerySet(models.QuerySet):
    def dog_list(self):
        return self.filter(animal_type = 'D')
    def cat_list(self):
        return self.filter(animal_type = 'C')
      
class CustomManager(models.Manager):
    def get_pets_price_range(self,r1,r2):
        return super().get_queryset().filter(price__range=(r1,r2))

    def get_queryset(self) -> models.QuerySet:
        return PetsQuerySet(self.model,using = self._db)
    
    def dog_list(self):
        return self.get_queryset().dog_list()
    
    def cat_list(self):
        return self.get_queryset().cat_list()

class Pet(models.Model):
    petapp_owner = models.ForeignKey(
        User,
        on_delete = models.CASCADE, 
        default = 1,
        ) 
    added_by = models.CharField( max_length = 50,default = 'user')
    gender_choices = (('male','Male'),('female','Female'))
    animal_type = models.CharField(max_length=1,choices=(('D','Dog'),('C','Cat')), null=False)
    image = models.ImageField(upload_to='media/')
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=30,choices= gender_choices)
    description = models.CharField(max_length=400)
    objects = models.Manager() 
    pets = CustomManager()
    pet = PetsQuerySet.as_manager()
    
    class Meta:
        db_table = 'Pet'
    
    def __str__(self) -> str:
        return f'{self.name}({self.species})'
 
    
    

    
    





      
        
        
        


        