from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import MethodNotAllowed, AuthenticationFailed


class CredentialsAuthentication(BaseAuthentication):
    """
    User authentication against email/password in a JSON form
    """
    def authenticate(self, request):
        """
        Returns a `User` if a correct email address and password have been supplied
        in the POST request's body in JSON format.  Otherwise returns `None`.
        """
        if request.method != 'POST':
            raise MethodNotAllowed(request.method)

        credentials = request.data
        email = credentials.get('email')
        password = credentials.get('password')

        if email and password:
            return self.authenticate_credentials(email, password)
        else:
            msg = _('Email address and password are required.')
            raise AuthenticationFailed(msg)

    def authenticate_credentials(self, email, password):
        """
        Authenticate the user against email address and password.
        """
        user = authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed(_('Invalid email/password.'))

        return user, None
