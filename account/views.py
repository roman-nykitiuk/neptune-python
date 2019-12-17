from knox.auth import TokenAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.schema import UserSchema
from account.serializers import UserSerializer, WriteUserSerializer


class UserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = UserSchema()

    def get(self, request):
        """
        Get current user info
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """
        Update default client ID for current user
        """
        serializer = WriteUserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
