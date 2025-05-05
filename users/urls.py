# from django.urls import path
# from .views import RegisterView, LoginView, UserDetailView, UserListView, UserUpdateView, SelfUpdateView, DeleteUserView, RefreshTokenView

# urlpatterns = [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('login/', LoginView.as_view(), name='login'),

    
#     path('user/', UserDetailView.as_view(), name='user_detail'),
#     path("user/update/", SelfUpdateView.as_view(), name="user-self-update"),
#     # path('user/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
#     # path("delete-user/<int:pk>/", DeleteUserView.as_view(), name="delete-user"),
#     # path('users/', UserListView.as_view(), name='user-list'),
#     path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    


# ]


from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, UserListView, UserUpdateView, SelfUpdateView, DeleteUserView, RefreshTokenView
from django.conf import settings
from django.conf.urls.static import static
 
 
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
 
   
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path("user/update/", SelfUpdateView.as_view(), name="user-self-update"),
    path('user/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path("delete-user/<int:pk>/", DeleteUserView.as_view(), name="delete-user"),
    path('users/', UserListView.as_view(), name='user-list'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
   
 
 
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)