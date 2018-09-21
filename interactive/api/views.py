from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import generics, mixins
from rest_framework.decorators import detail_route, list_route

from chats.models import ChatGroup, GlobalChat, LocalChat, Topic, Profile
from interactive.models import Message, Post, PostComment, Notification


from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import MessageSerializer, PostSerializer, PostCommentSerializer, NotificationSerializer


from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from .pagination import CustomPageNumberPagination
# Configure post saves + add post_save signals where necessary
# Reconfigure permissions if necessary

class NotificationViewSet(viewsets.ModelViewSet):
	serializer_class 	= NotificationSerializer
	queryset 	     	= Notification.objects.all()
	pagination_class	= CustomPageNumberPagination
	permission_classes	= [IsAuthenticated]
	lookup_field		= 'id'
	filter_backends 	= [SearchFilter, OrderingFilter]
	search_fields 		= ['sender']

	def perform_create(self, serializer):
		serializer.save(sender=self.request.user.profile)
	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)
	def get_serializer_context(self):
		return {'request':self.request}	
	def get_queryset(self, *args, **kwargs):
		queryset_list 	= Notification.objects.all()
		query 		  	= self.request.GET.get('receiver')
		chatgroup_query = self.request.GET.get('chatgroup_label')
		if query:
			queryset_list = Notification.objects.filter(receiver__label=query)
		elif chatgroup_query:
			queryset_list = Notification.objects.filter(chatgroup__label=chatgroup_query)	
		return queryset_list




class MessageViewSet(viewsets.ModelViewSet):
	serializer_class 	= MessageSerializer
	queryset 			= Message.objects.all()

	filter_backends 	= [SearchFilter, OrderingFilter]
	search_fields 		= ['text']
	pagination_class	= CustomPageNumberPagination
	permission_classes	= [IsOwnerOrReadOnly]
	lookup_field		= 'id'	

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)		

	def get_queryset(self, *args, **kwargs):
		queryset_list = Message.objects.all()
		query         = self.request.GET.get('topic')
		if query:
			queryset_list = Message.objects.filter(topic__label=query)	

		return queryset_list	


	def get_serializer_context(self):
		return {'request': self.request}	


	@detail_route(methods=['post'], permission_classes = [IsAuthenticated])	
	def new_subtopic(self, request, *args, **kwargs):
		message = self.get_object()
		topic_label = request.data['topic_label']
		print(request.data)
		# print("This is the topic label " + topic_label)
		topic = Topic.objects.get(label=topic_label)
 
		message.subtopics.add(topic)

		messageSerializer = MessageSerializer(message, context={'request': self.request})	

		return Response(messageSerializer.data)

	@detail_route(methods=['post', 'get'], permission_classes = [IsAuthenticated])
	def like(self, request, *args, **kwargs):
		from interactive.models import Notification
		user = request.user
		message = self.get_object()

		if message.likers.filter(id=user.id).exists():
			message.likers.remove(user)

			messageSerializer = MessageSerializer(message, context={'request': self.request})
			messageSerializerData = messageSerializer.data

			return Response(messageSerializerData)
		else:
			message.likers.add(user)
			### NOTIFICATION ###
			Notification.objects.create(
				text="LIK",
				sender=user.profile,
				receiver=message.user.profile,
				message=message
			)
			### NOTIFICATION FINISHED ###	
			messageSerializer = MessageSerializer(message, context={'request': self.request})
			messageSerializerData = messageSerializer.data

			return Response(messageSerializerData)


	@detail_route(methods=['post', 'get'], permission_classes = [IsAuthenticated])
	def share(self, request, *args, **kwargs):

		user = request.user
		message = self.get_object()



		if Post.objects.filter(message=message).exists():
			Post.objects.filter(message=message).delete()
			
			messageSerializer = MessageSerializer(message, context={'request': self.request})
			messageSerializerData = messageSerializer.data

			return Response(messageSerializerData)
		else:
			post = Post.objects.create(message=message)
			post.save()

			messageSerializer = MessageSerializer(message, context={'request': self.request})
			messageSerializerData = messageSerializer.data

			return Response(messageSerializerData)

			

	

class PostViewSet(viewsets.ModelViewSet):
	serializer_class 	= PostSerializer
	queryset 			= Post.objects.all()

	filter_backends 	= [SearchFilter, OrderingFilter]
	search_fields 		= ['message__text']

	permission_classes	= [IsOwnerOrReadOnly]



class PostCommentViewSet(viewsets.ModelViewSet):
	serializer_class 	= PostCommentSerializer
	queryset 			= PostComment.objects.all()

	filter_backends 	= [SearchFilter, OrderingFilter]
	search_fields 		= ['text']

	permission_classes	= [IsOwnerOrReadOnly]		


