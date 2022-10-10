from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),

    # Authentication Thingz
    path('register', views.register, name="register"),
    path('signIn', views.signIn, name="signIn"),
    path('changePassword', views.changePassword, name="changePassword"),
    path('forgotPassword', views.forgotPassword, name="forgotPassword"),
    path('dashboard', views.dashboard, name="dashboard"),

    # End of Authentication Thingz


]