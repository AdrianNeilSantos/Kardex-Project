from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.home, name="home"),

    # Authentication
    path('register/', views.register, name="register"),
    path('sign-in/', views.signIn, name="sign-in"),
    path('sign-out/', views.signOut, name="sign-out"),
    path('password-change/', views.changePassword, name="password-change"),
    path('password-forgot/', views.forgotPassword, name="password-forgot"),

    path("password-reset", views.password_reset_request, name="password-reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='kardex_app/Authentication/password-reset-done.html'), name='password-reset-done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='kardex_app/Authentication/password-reset-confirm.html', success_url = reverse_lazy('password-reset-complete')), name='password-reset-confirm'),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='kardex_app/Authentication/password-reset-complete.html'), name='password-reset-complete'),   
    # End of Authentication

    #Kardex 
    path('dashboard/', views.dashboard, name="dashboard"),
    path('create-kardex/', views.createKardex, name="create-kardex"),
    path('update-kardex/<str:pk>', views.updateKardex, name="update-kardex"),
    path('view-kardex/<str:pk>', views.viewKardex, name="view-kardex"),
    path('delete-kardex/<str:pk>', views.deleteKardex, name="delete-kardex"),

    #Kardex REST API
    path('api/v1/kardex/', views.KardexList.as_view()),
    path('api/v1/kardex/paginated/', views.PaginatedKardexList.as_view()),
    path('api/v1/kardex/search/', views.kardex_search),

    #End of Kardex
    #Nurse
    path('profile/<str:pk>', views.profile, name="profile"),
    path('view-profile/', views.viewProfile, name="view-profile"),
    path('nurse-dashboard/', views.nurseDashboard, name="nurse-dashboard"),
    path('create-nurse/', views.createNurse, name="create-nurse"),
    path('update-nurse/<str:pk>', views.updateNurse, name="update-nurse"),
    path('view-nurse/<str:pk>', views.viewNurse, name="view-nurse"),
    path('delete-nurse/<str:pk>', views.deleteNurse, name="delete-nurse"),

    #Kardex REST API
    path('api/v1/nurse/', views.NurseList.as_view()),
    path('api/v1/nurse/paginated/', views.PaginatedNurseList.as_view()),
    path('api/v1/nurse/search/', views.nurse_search),

    #End of Nurse

    #Generate Reports
    path('generate-reports/', views.generateReports, name="generate-reports"),
    path('diet_list_PDF/', views.diet_list_PDF, name="diet_list_PDF"),
    path('bed_tags_PDF/', views.bed_tags_PDF, name="bed_tags_PDF"),
    path('intravenous_fluid_tags_PDF/', views.intravenous_fluid_tags_PDF, name="intravenous_fluid_tags_PDF"),
    path('medication_cards_PDF/', views.medication_cards_PDF, name="medication_cards_PDF"),
    path('medication_endorsement_sheet_PDF/', views.medication_endorsement_sheet_PDF, name="medication_endorsement_sheet_PDF"),
    path('nursing_endorsement_sheet_PDF/', views.nursing_endorsement_sheet_PDF, name="nursing_endorsement_sheet_PDF"),
    path('special_notes_PDF/', views.special_notes_PDF, name="special_notes_PDF"),
    path('ward_census_PDF/', views.ward_census_PDF, name="ward_census_PDF"),
    path('generate-census-XLSX/<str:department>', views.generate_census_XLSX, name="generate-census-XLSX"),
    #End of Generate Reports
]