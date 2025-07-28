from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', company_register, name='company_register'),
    path('login/', company_login, name='company_login'),
    path('logout/', logout_user, name='logout'),


    path('add_members/', add_members, name='add_members'),
    path('view_members/', view_members, name='view_members'),
    path('delete_member/<int:id>/', delete_member, name='remove_member'),
    path('edit_member/<int:id>/', edit_member, name='edit_member'), 
    path('add_project/', add_project, name='add_project'),
    path('view_projects',view_projects,name="view_projects"),
    path('add_member_to_project/<int:mid>/<int:pid>/', add_member_to_project, name='add_member_to_project'),
    path('remove_member_from_project/<int:mid>/', remove_member_from_project, name='remove_member_from_project'),



    path('view_project/', myprojects, name='view_project'),
    path('teamtasks/', teamtasks, name='teamtasks'),
    path('task_comment/<int:task_id>', task_comment, name='task_comment'),
    path('tasks/', dailytasks, name='tasks'),
    path('upload_final_file/',upload_final_file,name="upload_final_file")



]