from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hospital.serializers import ClientSerializer


class ClientListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        List clients of current user
        """
        clients = request.user.clients.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)
