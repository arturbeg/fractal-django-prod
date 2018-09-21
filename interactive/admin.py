from django.contrib import admin
from .models import Message, Post, PostComment, Notification
# Register your models here.


admin.site.register(Message)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(Notification)




