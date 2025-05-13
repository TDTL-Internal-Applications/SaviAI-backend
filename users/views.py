from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdminUser  # optional, if you created it

User = get_user_model()


class RegisterView(generics.CreateAPIView):  # Registration
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(generics.GenericAPIView):  # Login
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
            'redirect_to': f"/dashboard/{user.role}"  # for frontend use
        })


class UserDetailView(generics.RetrieveAPIView):  # Get Current User
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class SelfUpdateView(generics.RetrieveUpdateAPIView):  # Update Own Profile
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):  # Admin Update Any User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return User.objects.get(pk=user_id)


class DeleteUserView(generics.DestroyAPIView):  # Admin Delete Any User
    queryset = User.objects.all()
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class UserListView(generics.ListAPIView):  # All Users, with ?role=ceo filter
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        role = self.request.query_params.get('role')
        if role:
            return CustomUser.objects.filter(role=role)
        return CustomUser.objects.all()


@method_decorator(csrf_exempt, name='dispatch')
class RefreshTokenView(generics.GenericAPIView):  # Refresh Access Token
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            return Response({
                'access': access_token
            }, status=status.HTTP_200_OK)

        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception:
            return Response({'detail': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
