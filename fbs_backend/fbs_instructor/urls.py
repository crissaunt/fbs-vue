from django.urls import path
from . import views
from .views import (
    Login_view, 
    instructor_dashboard, 
    section_details, 
    register_view, 
    EnrollStudentView, 
    Enroll_Student_list,
    create_activity,
    delete_activity,
    activity_details,
    activate_activity,
    student_activity_details,  # ? ADD THIS
    student_dashboard,         # ? ADD THIS
    get_activity_submissions,  # ? ADD THIS
)

urlpatterns = [
    # Authentication
    path('login/', Login_view, name='Login_view'),
    path('register/', register_view, name='register'),
    
    # Dashboard
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),

    # Section Management
    path('instructor/sections/<int:section_id>/', section_details, name='section_details'),
    path('instructor/sections/<int:section_id>/enroll/', EnrollStudentView.as_view(), name='enroll-student'),
    path('instructor/sections/<int:section_id>/students/', Enroll_Student_list, name='Enroll_Student_list'),
    
    # Activity Management - Create & Delete
    path('instructor/sections/<int:section_id>/activities/create/', create_activity, name='api_create_activity'),
    path('instructor/sections/<int:section_id>/activities/<int:activity_id>/delete/', delete_activity, name='delete_activity'),
    
    # Activity Details & Activation
    path('instructor/activities/<int:activity_id>/', activity_details, name='activity-details'),
    path('instructor/activities/<int:activity_id>/submissions/', get_activity_submissions, name='activity-submissions'),
    path('instructor/activity/<int:activity_id>/activate/', activate_activity, name='activate_activity'),

    # ============================================
    # STUDENT URLS - ? FIXED
    # ============================================
    
    # Student Dashboard
    path('student/dashboard/data/', student_dashboard, name='student_dashboard_data'),
    
    # ? FIXED: Main student activity endpoint (matches frontend)
    path('student/activities/<int:activity_id>/details/', student_activity_details, name='student_activity_details'),
    
    # ? REMOVED: Non-existent views (commented out - create these views later if needed)
    # path('student/activities/<int:activity_id>/submit/', views.submit_activity, name='student_submit_activity'),
    # path('student/activities/<int:activity_id>/status/', views.update_activity_status, name='student_update_status'),
    # path('student/activities/<int:activity_id>/submission/', views.get_activity_submission, name='student_get_submission'),
    # path('student/activities/<int:activity_id>/draft/', views.save_draft, name='student_save_draft'),
    
    # ? KEEP: Legacy URL for backward compatibility
    path('student/activity/<int:activity_id>/', student_activity_details, name='student_activity_details_legacy'),


    
]