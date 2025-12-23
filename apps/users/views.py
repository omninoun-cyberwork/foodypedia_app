# accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserRegistrationSerializer
from rest_framework.permissions import AllowAny # Permettre l'accès sans être connecté

class RegisterView(APIView):
    """
    Vue pour l'enregistrement de nouveaux utilisateurs.
    """
    permission_classes = [AllowAny] # Tout le monde doit pouvoir s'inscrire

    def post(self, request):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Vous pouvez ajouter ici l'envoi d'un token JWT juste après l'inscription si nécessaire
            
            return Response(
                {"message": "Inscription réussie.", "user": serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)