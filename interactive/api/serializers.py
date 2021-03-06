from django.contrib.auth.models import User
from rest_framework import serializers

# Chats App models
# from chats.models import ChatGroup, GlobalChat, LocalChat, Topic, Profile

# Interactive App models
from interactive.models import Message, Post, PostComment, Notification

from chats.models import Topic, Profile

from chats.api.serializers import ProfileSerializer

from django.utils.timesince import timesince



# TODO: change back to HyperLinked
class MessageSerializer(serializers.ModelSerializer):
	
	likers_count 	= serializers.SerializerMethodField()	
	
	topic			= serializers.SlugRelatedField(slug_field='label', queryset=Topic.objects.all())
	# sender -> same as user, but expanded version

	sender			= serializers.SerializerMethodField()
	
	shared			= serializers.SerializerMethodField()

	topic_object 	= serializers.SerializerMethodField()

	timestamp_human	= serializers.SerializerMethodField()

	# subtopics		= serializers.SerializerMethodField()

	# subtopics       = serializers.SlugRelatedField(slug_field='label', queryset=Topic.objects.all(), many=True)

	subtopics    	= serializers.SerializerMethodField()

	seen 			= serializers.SerializerMethodField()

	class Meta:
		model = Message
		# fields = ['url', 'pk', 'user', 'globalchat', 'localchat', 'topic', 'text', 'photo', 
		# 'file', 'flag', 'likers', 'dislikers', 'timestamp']

		# read_only_fields = ['user', 'pk', 'user', 'timestamp']
		# sender is the profile of the user presented in a nested mannder
		fields = ['id', 'text', 'timestamp', 'topic_object', 'user', 'sender', 
		'likers_count', 'shared', 'timestamp_human', 'topic', 
		'subtopics', 'seen', 'photo']

		read_only_fields = ['pk', 'timestamp']

		lookup_field = 'id'

	def get_seen(self, obj):
		request = self.context.get("request")
		user = request.user
		seen = obj.seen_by.filter(id=user.id).exists()
		return seen	

	def get_subtopics(self, obj):
		return [x.label for x in obj.subtopics.all()]

	def get_timestamp_human(self, obj):
		return timesince(obj.timestamp)


	def get_topic_object(self, obj):
		request = self.context.get("request")
		return obj.get_serialized_topic(request)	
		
	def get_shared(self, obj):
		return obj.is_shared()	

	def get_likers_count(self, obj):
		return obj.likers_count()

	def get_sender(self, obj):
		profile = obj.user.profile
		profileSerializer = ProfileSerializer(profile, context={'request':self.context.get("request")})
		profileSerializerData = profileSerializer.data
		return profileSerializerData	
	# validate that the message has content	
	# def validate(self, data):
	# 	photo = data['photo']
	# 	text  = data['text']
	# 	file  = data['photo']
	# 	flag  = data['text']

	# 	if photo is None and text is None and file is None and flag is None:
	# 		raise serializers.ValidationError('The message must contain some nonempty content type')

	# 	return data	

	# if the message is of the text type, make sure it's nonempty

	# def validate_text(self, value):
	# 	if value.isspace():
	# 		raise serializers.ValidationError('The message must contain some nonempty content type')

	# 	return value	


class PostSerializer(serializers.ModelSerializer):
	
	message = MessageSerializer()

	timestamp_human	= serializers.SerializerMethodField()


	class Meta:
		model = Post
		fields = ['message', 'timestamp', 'timestamp_human']

		read_only_fields = ['url', 'pk', 'timestamp', 'message', 'timestamp_human']


	
	def get_timestamp_human(self, obj):
		return timesince(obj.timestamp)	


from chats.api.serializers import ChatGroupSerializer
class NotificationSerializer(serializers.ModelSerializer):

	sender_object   			= serializers.SerializerMethodField()
	receiver_object				= serializers.SerializerMethodField()
	timestamp_human 		    = serializers.SerializerMethodField()
	sender 						= serializers.SlugRelatedField(slug_field='label', queryset=Profile.objects.all())
	receiver 					= serializers.SlugRelatedField(slug_field='label', queryset=Profile.objects.all())
	message   					= MessageSerializer()
	chatgroup 					= ChatGroupSerializer()

	class Meta:
		model = Notification
		fields = ['id', 'text', 'sender', 'receiver', 'timestamp_human', 'sender_object', 'receiver_object', 'message', 'chatgroup']
		read_only_fields = ['id', 'text', 'sender', 'receiver', 'timestamp_human', 'sender_object', 'receiver_object', 'message', 'chatgroup']


	def get_sender_object(self, obj):
		profile = obj.sender
		request = self.context.get("request")
		return profile.get_serialized_profile(request)

	def get_receiver_object(self, obj):
		if obj.receiver:
			profile = obj.receiver
			request = self.context.get("request")
			return profile.get_serialized_profile(request)	
		else:
			return None	

	def get_timestamp_human(self, obj):
		return timesince(obj.timestamp)	







# Do later...

class PostCommentSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Message
		fields = ['url', 'pk', 'user', 'post', 'text', 'likers', 'dislikers', 'timestamp']	

		read_only_fields = ['url', 'pk', 'user', 'timestamp']
