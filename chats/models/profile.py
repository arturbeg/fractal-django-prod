from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
# from chats.api.serializers import ProfileSerializer
User = settings.AUTH_USER_MODEL

from django.core.cache import cache 
import datetime




class Profile(models.Model):
   
    # Media Upload To -> decide how to store media files 
    user 		= models.OneToOneField(User, on_delete=models.CASCADE)
    followers 	= models.ManyToManyField(User, blank=True, related_name="is_following")
    about 		= models.CharField(max_length=200, blank=True)
    avatar 		= models.ImageField(upload_to="profile_avatar", blank=True, null=True)

    timestamp 	= models.DateTimeField(auto_now_add=True)

    # shares      = 

    label       = models.SlugField(unique=True) # redundunt -> delete later (owner didn't really work)

    # Some info about the REST API related to the Profile Class

    
    # methods are below

    def __str__(self):
        return self.user.username

    def get_serialized_profile(self, request):
        from chats.api.serializers import ProfileSerializer
        profileSerializer = ProfileSerializer(self, context={"request": request})
        return profileSerializer.data

    def last_seen(self):
        print(cache.get('seen_%s' % self.user.username))

        return cache.get('seen_%s' % self.user.username)            
    
    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False            
        
    @property
    def owner(self):
        return self.user

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})
        

    def get_absolute_url_for_avatar(self):
        if not self.avatar:
            try:
                return static('chats/default-img/default-user.jpg')
            except:
                import sys
                print(str(sys.exc_info()))    
        else:
            return self.avatar.url
            

    def account_verified(self): # Checks if the user's email address has been verified
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False


    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.user.is_following.count()

    def chatgroups_count(self):
        return self.user.is_member.count()


    def followed(self, request):
        user = request.user
        if self.followers.filter(id=user.id).exists():
            return True
        else:
            return False        

        

def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        profile, is_created = Profile.objects.get_or_create(user=instance, label=instance.username)

post_save.connect(post_save_user_receiver, sender=User)

