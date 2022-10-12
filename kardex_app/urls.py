from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),

    # Authentication
    path('register/', views.register, name="register"),
    path('signIn/', views.signIn, name="signIn"),
    path('changePassword/', views.changePassword, name="changePassword"),
    path('forgotPassword/', views.forgotPassword, name="forgotPassword"),

    # End of Authentication

    #Kardex 
    path('dashboard/', views.dashboard, name="dashboard"),
    path('createKardex/', views.createKardex, name="createKardex"),
    path('updateKardex/<str:pk>', views.updateKardex, name="updateKardex"),
    path('viewKardex/<str:pk>', views.viewKardex, name="viewKardex"),
    path('deleteKardex/<str:pk>', views.deleteKardex, name="deleteKardex"),

    #End of Kardex

    #Generate Reports
    path('generateReports/', views.generateReports, name="generateReports"),
    #End of Generate Reports
]