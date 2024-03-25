from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('create-listing/', views.createListing, name="create-listing"),
    path('listing/<int:id>/', views.showListing, name="listing"),
    path('like/', views.likeComment, name="like-comment"),
    path('reply/', views.postReply, name="reply"),
    path('get-replies/', views.getReplies, name="get-replies"),
]