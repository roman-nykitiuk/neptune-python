from knox.views import LoginView, LogoutView, LogoutAllView

from api.authentication import CredentialsAuthentication
from api.schema import LoginSchema
from hospital.permissions import HasPhysicianAccess


class LoginAPIView(LoginView):
    """
    post:
    User login by email/password
    """
    authentication_classes = (CredentialsAuthentication,)
    permission_classes = (HasPhysicianAccess,)
    schema = LoginSchema()


class LogoutAPIView(LogoutView):
    """
    post:
    Log the user out of session of current token
    """


class LogoutAllAPIView(LogoutAllView):
    """
    post:
    Log the user out of all sessions
    """
