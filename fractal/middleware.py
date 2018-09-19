import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.utils.deprecation import MiddlewareMixin

def get_user_jwt(request):
    """
    Replacement for django session auth get_user & auth.get_user for
     JSON Web Token authentication. Inspects the token for the user_id,
     attempts to get that user from the DB & assigns the user on the
     request object. Otherwise it defaults to AnonymousUser.
    This will work with existing decorators like LoginRequired, whereas
    the standard restframework_jwt auth only works at the view level
    forcing all authenticated users to appear as AnonymousUser ;)
    Returns: instance of user object or AnonymousUser object
    """
    user = None
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            # store the first part from the tuple (user, obj)
            user = user_jwt[0]
    except:
        pass

    return user or AnonymousUser()



class ActiveUserMiddleware(MiddlewareMixin):

	def process_request(self, request):
		## Add is_authenticated later...
		user = SimpleLazyObject(lambda : get_user_jwt(request))
		print(user.username)
		current_user = user
		now = datetime.datetime.now()
		cache.set('seen_%s' % (current_user.username), now, 
		settings.USER_LASTSEEN_TIMEOUT)
