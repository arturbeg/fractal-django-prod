from django.db import models
from chats.models import ChatGroup, LocalChat, Topic, GlobalChat, Profile
from django.conf import settings
from .message import Message
from .post import Post
from .postcomment import PostComment

User = settings.AUTH_USER_MODEL


# Notification system 1.0

class Notification(models.Model):
	NOTIFICATION_TEXT_CHOICES = [
		('FOL', 'follow'),
		('LIK', 'like'),
		('FOLCG', 'follow chatgroup')
	]
	text 			= models.CharField(
							max_length=5,
							choices=NOTIFICATION_TEXT_CHOICES
						)
	sender 			= models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="notifications_sent")
	receiver 		= models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="notifications_received") 
	# The Notification is related to a message object, analogously for the post and post_comment fields
	chatgroup 		= models.ForeignKey(ChatGroup, on_delete=models.CASCADE, blank=True, null=True)
	message 		= models.ForeignKey(Message, on_delete=models.CASCADE, blank=True, null=True)
	post 			= models.ForeignKey(Post, 	 on_delete=models.CASCADE, blank=True, null=True)
	postcomment 	= models.ForeignKey(PostComment, on_delete=models.CASCADE, blank=True, null=True)

	timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

	def __str__(self):
		return self.text + " : " + self.sender.user.username	