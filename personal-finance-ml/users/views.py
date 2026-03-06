from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)  # Anyone can register

    @extend_schema(
        summary="Register New User & Profile",
        description="Creates a new User and automatically instantiates a linked UserProfile containing ML baseline demographics (Salary, City Tier, Savings Goal)."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User Created Successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    retrieve=extend_schema(summary="Get Current User Profile", description="Retrieves the authenticated user's profile and ML baseline data."),
    update=extend_schema(summary="Update User Profile", description="Updates the baseline demographics. Pushing updates here will recalibrate the ML Budget Regressor outputs globally."),
    partial_update=extend_schema(summary="Partial Update User Profile")
)
class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        from .serializers import UserDetailSerializer
        return UserDetailSerializer

    def get_object(self):
        return self.request.user
