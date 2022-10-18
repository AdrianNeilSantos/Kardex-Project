from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),

    # Authentication
    path('register/', views.register, name="register"),
    path('sign-in/', views.signIn, name="sign-in"),
    path('sign-out/', views.signOut, name="sign-out"),
    path('change-password/', views.changePassword, name="change-password"),
    path('forgot-password/', views.forgotPassword, name="forgot-password"),

    # End of Authentication

    #Kardex 
    path('dashboard/', views.dashboard, name="dashboard"),
    path('create-kardex/', views.createKardex, name="create-kardex"),
    path('update-kardex/<str:pk>', views.updateKardex, name="update-kardex"),
    path('view-kardex/<str:pk>', views.viewKardex, name="view-kardex"),
    path('delete-kardex/<str:pk>', views.deleteKardex, name="delete-kardex"),

    #End of Kardex
    path('nurse-dashboard/', views.nurseDashboard, name="nurse-dashboard"),
    path('create-nurse/', views.createNurse, name="create-nurse"),
    path('update-nurse/<str:pk>', views.updateNurse, name="update-nurse"),
    path('view-nurse/<str:pk>', views.viewNurse, name="view-nurse"),
    path('delete-nurse/<str:pk>', views.deleteNurse, name="delete-nurse"),
    #Nurse

    #End of Nurse

    #Generate Reports
    path('generate-reports/', views.generateReports, name="generate-reports"),
    #End of Generate Reports
]