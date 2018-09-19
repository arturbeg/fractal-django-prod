from django.db import models
from .chatgroup import ChatGroup
from django.conf import settings
from rest_framework.reverse import reverse as api_reverse
from .localchat import LocalChat
from .utilities import unique_label_generator
from django.db.models.signals import post_save, pre_save
from .topic_ranking import *
import datetime

User = settings.AUTH_USER_MODEL


class Topic(models.Model):
	chatgroup = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="topic_chatgroup")  # the parent chat group
	name = models.CharField(max_length=200)
	about = models.CharField(max_length=200, blank=True)
	description = models.TextField(blank=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to="topic_avatar", blank=True)

	saves = models.ManyToManyField(User, blank=True, related_name="topic_saves")
	timestamp = models.DateTimeField(auto_now_add=True)
	label = models.SlugField(unique=True) # Unique way to name a topic/localchat in the URL

	# change to Profile if needed
	online_participants = models.ManyToManyField(User, blank=True, related_name="topic_online")

	arrow_ups 	= models.ManyToManyField(User, blank=True, related_name='arrow_ups')
	arrow_downs = models.ManyToManyField(User, blank=True, related_name='arrow_downs')


	def __str__(self):
		return self.name

	def hot(self):
		date = self.timestamp
		## CONFIGURE TIMEZONES... (SEPARATE DJANGO RESEARCH)
		date = date.replace(tzinfo=None)
		return hot(self.arrow_ups.count(), self.arrow_downs.count(), date)
					
	def rating(self):
		return self.arrow_ups.count() - self.arrow_downs.count()

	def most_recent_message_text(self, request):
		try:
			message = self.topic_messages.latest('id')
			message_text = message.text
			return message_text
		except:
			return None

	def most_recent_message_avatar(self, request):
		try:
			message = self.topic_messages.latest('id')
			message_avatar = message.user.profile.avatar.url
			return message_avatar
		except:
			return None	
				
	def messages(self):
		# all the messages in the topic
		from interactive.models import Message
		messages = Message.objects.filter(topic__id=self.id)		
		return messages

	def serialized_topic(self, request):
		from chats.api.serializers import TopicSerializer
		topicSerializer = TopicSerializer(self, context={"request": request})
		return topicSerializer.data
		

	# not elegant	
	def participants(self):
		participants = []
		for participant in self.online_participants.all():
			participants.append(participant.profile)
		
		return participants

	def upvoted(self, request):
		user = request.user
		if self.arrow_ups.filter(id=user.id).exists():
			return True
		else:
			return False				

	def downvoted(self, request):
		user = request.user
		if self.arrow_downs.filter(id=user.id).exists():
			return True
		else:
			return False

	def saved(self, request):
		user = request.user
		if self.saves.filter(id=user.id).exists():
			return True
		else:
			return False


def pre_save_topic_receiver(sender, instance, created, *args, **kwargs):
	if created:
		topic_label = unique_label_generator(instance)
		instance.label = topic_label
		instance.save()

post_save.connect(pre_save_topic_receiver, sender=Topic)

