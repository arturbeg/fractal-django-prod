from django.contrib.auth.models import User
from rest_framework import serializers

from chats.models import ChatGroup, GlobalChat, LocalChat, Topic, Profile
from .validators import lowercase



class ProfileSerializer(serializers.HyperlinkedModelSerializer):
	
	followers_count 	= serializers.SerializerMethodField()	
	following_count		= serializers.SerializerMethodField()
	# posts_count			= serializers.SerializerMethodField()
	chatgroups_count	= serializers.SerializerMethodField()

	followed			= serializers.SerializerMethodField()

	user_id				= serializers.SerializerMethodField()

	online		= serializers.SerializerMethodField()		

	# avatar_url			= serializers.SerializerMethodField()

	class Meta:
		model 				= Profile
		fields 				= [
								'id', 'about', 'label', 'followers_count', 'following_count',
								'chatgroups_count', 'followed', 'user_id', 'avatar', 'online'
							  ] 
		read_only_fields 	= ['id']
		lookup_field		= 'label'

	def get_online(self, obj):
		return obj.online()	

	def get_user_id(self, obj):
		return obj.user.id

	def get_followed(self, obj):
		request = self.context.get("request")
		return obj.followed(request)		
	
	def get_followers_count(self, obj):
		return obj.followers_count()

	def get_following_count(self, obj):
		return obj.following_count()

	def get_chatgroups_count(self, obj):
		return obj.chatgroups_count()	

	# def get_posts_count(self, obj):
	# 	return obj.posts_count()			


class UserSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model  			= User
		fields 			= ['url', 'id', 'username', 'email', 'password']
		lookup_field	= 'username'

		extra_kwargs = {

			"password":		{"write_only":True},
			'url': 			{'lookup_field': 'username'},
		}	


	def create(self, validated_data):
		username = validated_data['username']
		email = validated_data['email']
		password = validated_data['password']

		user = User(username=username, email=email)
		user.set_password(password)
		user.save()

		return validated_data
	# make sure the username is lowercase	
	def validate_username(self, value):

		return lowercase(value)


# class ChatGroupSerializer(serializers.HyperlinkedModelSerializer):

# 	class Meta:
# 		model 				= ChatGroup
# 		fields 				= ['url', 'id', 'owner', 'name', 'about', 'members', 'description', 'label', 'timestamp', 'avatar']
# 		read_only_fields	= ['owner', 'url', 'id', 'label', 'timestamp']
# 		lookup_field		= 'label'
# 		extra_kwargs		= {
# 			'url': 	 	{'lookup_field': 'label'},
# 			'owner': 	{'lookup_field': 'username'},
# 			'members':  {'lookup_field': 'username'},
# 		}

# Used for testing purposes
class ChatGroupSerializer(serializers.HyperlinkedModelSerializer):

	followers_count 	= serializers.SerializerMethodField()
	topics_count		= serializers.SerializerMethodField()
	localchats_count	= serializers.SerializerMethodField()

	owner				= serializers.SerializerMethodField()

	followed   			= serializers.SerializerMethodField()

	class Meta:
		model 				= ChatGroup
		fields 				= ['id', 'name', 'about', 'description', 'label', 'followers_count', 'topics_count', 'localchats_count', 'timestamp', 'owner', 'followed']
		read_only_fields	= ['id', 'label', 'followers_count', 'followed', 'description']
		lookup_field		= 'label'
		# extra_kwargs		= {
		# 	'url': 	 	{'lookup_field': 'label'},
		# 	'owner': 	{'lookup_field': 'username'},
		# 	'members':  {'lookup_field': 'username'},
		# }

	def get_followed(self, obj):
		request = self.context.get("request")
		return obj.followed(request)		

	def get_followers_count(self, obj):
		return obj.followers_count()

	def get_topics_count(self, obj):
		return obj.topics_count()

	def get_localchats_count(self, obj):
		return obj.localchats_count()	

	def get_owner(self, obj):
		owner = obj.ownerProfile() # getting the profile of the owner
		ownerSerializer = ProfileSerializer(owner, context={'request':self.context.get("request")})
		ownerSerializerData = ownerSerializer.data
		return ownerSerializerData



class TopicSerializer(serializers.ModelSerializer):
	

	# Difference between the arrow_ups and arrow_downs
	rating 								= serializers.SerializerMethodField()
	participants    					= serializers.SerializerMethodField()
	most_recent_message_text			= serializers.SerializerMethodField()
	most_recent_message_sender_avatar 	= serializers.SerializerMethodField()
	# Use chatgroup URL later
	chatgroup_object					= serializers.SerializerMethodField()
	chatgroup							= serializers.SlugRelatedField(slug_field='label', queryset=ChatGroup.objects.all())	

	owner 								= serializers.SerializerMethodField()

	upvoted								= serializers.SerializerMethodField()
	downvoted							= serializers.SerializerMethodField()
	saved								= serializers.SerializerMethodField()

	number_of_unread_messages			= serializers.SerializerMethodField()

	ranking 							= serializers.SerializerMethodField()


	class Meta:
		model 				= Topic
		#fields 				= [ 'url', 'chatgroup', 'id', 'name', 'owner', 'about', 'description', 'label', 'timestamp', 'avatar', 'arrow_ups', 'arrow_downs', 'saves', 'online_participants']
		fields 				= ['id', 'name', 'about', 'label', 'rating', 'chatgroup', 'chatgroup_object', 'participants', 'most_recent_message_text', 'owner', 'upvoted', 'downvoted', 'saved', 'number_of_unread_messages', 'most_recent_message_sender_avatar', 'ranking']
		read_only_fields	= ['label']
		lookup_field		= 'label'
		# extra_kwargs		= {
		# 	'url': 	 				{'lookup_field': 'label'},
		# 	'chatgroup': 	 		{'lookup_field': 'label'},
		# 	'owner': 				{'lookup_field': 'username'},
		# 	'online_participants':  {'lookup_field': 'username'},
		# 	'saves':  				{'lookup_field': 'username'},
		# 	'arrow_ups':  			{'lookup_field': 'username'},
		# 	'arrow_downs':  		{'lookup_field': 'username'},
		# }	

	def get_ranking(self, obj):
		return obj.hot()

	def get_number_of_unread_messages(self, obj):
		from interactive.models import Message
		request = self.context.get("request")
		user = request.user
		# messages in the topic
		topicMessages = Message.objects.filter(topic__id=obj.id)
		total_topic_messages = topicMessages.all().count()
		total_topic_seen_messages = topicMessages.filter(seen_by__id=user.id)
		number_of_unread_messages = total_topic_messages - total_topic_seen_messages.count()
		return number_of_unread_messages

		
	def get_chatgroup_object(self, obj):
		request = self.context.get("request")	
		chatgroup = obj.chatgroup
		chatgroupSerializer = ChatGroupSerializer(chatgroup, context={'request':request})
		return chatgroupSerializer.data

	def get_saved(self, obj):
		request = self.context.get("request")
		return obj.saved(request)	
		
	def get_upvoted(self, obj):
		request = self.context.get("request")
		return obj.upvoted(request)

	def get_downvoted(self, obj):
		request = self.context.get("request")
		return obj.downvoted(request)  	

	def get_most_recent_message_sender_avatar(self, obj):
		return obj.most_recent_message_avatar(self.context.get("request"))


	def get_most_recent_message_text(self, obj):
		return obj.most_recent_message_text(self.context.get("request"))


	def get_rating(self, obj):
		return obj.rating()

	def get_participants(self, obj):
		participants = obj.participants()	
		participantsSerializer = ProfileSerializer(participants, many=True, context={'request':self.context.get("request")})
		participantsSerializerData = participantsSerializer.data
		return participantsSerializerData

	def get_owner(self, obj):
		owner = obj.owner.profile
		ownerSerializer = ProfileSerializer(owner, context={'request':self.context.get("request")})
		ownerSerializerData = ownerSerializer.data

		return ownerSerializerData

						
class LocalChatSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model 				= LocalChat
		fields 				= [ 'url', 'id', 'chatgroup', 'name', 'owner', 'about', 'description', 'label', 'timestamp', 'avatar', 'online_participants', 'saves']
		lookup_field		= 'label'
		extra_kwargs		= {
			'url': 	 				{'lookup_field': 'label'},
			'chatgroup': 	 		{'lookup_field': 'label'},
			'owner': 				{'lookup_field': 'username'},
			'online_participants':  {'lookup_field': 'username'},
			'saves':  				{'lookup_field': 'username'},
		}



class GlobalChatSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model 				= GlobalChat
		fields 				= [ 'url', 'id', 'chatgroup', 'label', 'online_participants'] # add saves to GC model
		lookup_field		= 'label'
		extra_kwargs		= {
			'url': 	 				{'lookup_field': 'label'},
			'chatgroup': 	 		{'lookup_field': 'label'},
			'online_participants':  {'lookup_field': 'username'},
		}

