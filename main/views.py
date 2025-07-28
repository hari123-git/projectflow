from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.db.models import Q 

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.utils.timezone import now

from django.urls import reverse

from django.contrib.auth.decorators import login_required



# Create your views here.
@login_required()
def home(request):

    if request.user.role == 'leader':
        project = Project.objects.filter(members=request.user).first()
        tasks = DivideTasks.objects.filter(project=project).order_by('-id')
        if request.GET.get('tid'):
            task = DivideTasks.objects.get(id=request.GET.get('tid'))
            task.status = 'Completed'
            task.save()

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='Completed').count()

        if total_tasks > 0:
            project.progress = (completed_tasks / total_tasks) * 100
        else:
            project.progress = 0  

        if project.progress == 100:
            project.status = "Completed"
        elif project.progress > 0:
            project.status = "On Going"
        else:
            project.status = "Not Started"

        project.save()


        attendance=Attendance.objects.filter(project=project)


        context = {
            'project': project,
            'tasks': tasks,
            'attendance':attendance
        }

        return render(request, 'index.html', context)
    if request.user.role == 'developer':
        project = Project.objects.filter(members=request.user).first()

        user=request.user
        tasks=DailyTasks.objects.filter(project=project).filter(user=user).order_by('-status')
        if request.GET.get('tid'):
            dtask=DailyTasks.objects.get(id=request.GET.get('tid'))
            dtask.status="Completed"
            dtask.save()
            return redirect('home')


        context = {
            'project': project,
            'tasks': tasks
        }
        return render(request, 'index.html', context)
    
    if request.user.role == 'manager':
        return redirect('view_projects')

    return render(request, 'index.html')


def company_register(request):
    if request.method == 'POST':
        cname = request.POST.get('cname')
        uname = request.POST.get('uname')
        passw = request.POST.get('pass')
        cpass = request.POST.get('cpass')

        if Profile.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('company_register')

        if passw == cpass:
            company = Company.objects.create(name=cname)
            user = Profile.objects.create_user(username=uname, password=passw, company=company, role='manager')
            user.save()
            login(request, user)
            messages.success(request, 'User  created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('company_register')

    return render(request, 'reg.html')

def company_login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        passw = request.POST.get('pass')
        
        user = authenticate(username=uname, password=passw)  # Secure authentication
        if user is not None:
            login(request, user)

            if user.role == 'developer':
                project = Project.objects.filter(members=user).first()
                if project:
                    date=now()
                    if not Attendance.objects.filter(user=user, project=project,date=date).exists():
                        Attendance.objects.create(user=user, project=project,date=now())


            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('company_login')

    return render(request, 'log.html')


def logout_user(request):
    logout(request)
    return redirect('company_login')



def add_members(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        passw = request.POST.get('pass')
        role = request.POST.get('role')
        company= request.user.company
        user = Profile.objects.create_user(username=uname, password=passw, role=role, company=company)
        user.save()
        messages.success(request, 'User created successfully!')
        return redirect('home')
    return render(request, 'add_members.html')

def view_members(request):
    company = request.user.company
    members = Profile.objects.filter(company=company)
    return render(request, 'view_members.html', {'members': members})

def delete_member(request, id):
    member = Profile.objects.get(id=id)
    member.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('view_members')

def edit_member(request, id):
    member = Profile.objects.get(id=id)
    if request.method == 'POST':
        role = request.POST.get('role')
        uname = request.POST.get('uname')
        if request.POST.get('pass') != '':
            passw = request.POST.get('pass')
            member.set_password(passw)
        member.username = uname
        member.role = role
        member.save()
        messages.success(request, 'User updated successfully!')
        return redirect('view_members')
    return render(request, 'edit_member.html', {'member': member})

def add_project(request):
    if request.method == 'POST':
        pname = request.POST.get('pname')
        deadline = request.POST.get('deadline')
        abstract= request.POST.get('abstract')
        company = request.user.company
        project = Project.objects.create(name=pname, deadline=deadline, company=company,abstract=abstract)
        project.save()
        messages.success(request, 'Project created successfully!')
        return redirect('home')
    return render(request, 'add_project.html')

def view_projects(request):
    projects = Project.objects.filter(company=request.user.company)
    members = Profile.objects.filter(company=request.user.company).filter(
        Q(on_project__isnull=True) | Q(on_project__company=request.user.company)
    ).exclude(role="manager").exclude(role="admin").exclude(role="member")

    if request.method == 'POST':
        name=request.POST.get('name')

        status=request.POST.get('status')
        project_id=request.POST.get('project_id')
        abstract=request.POST.get('abstract')
        project=Project.objects.get(id=project_id)
        project.name=name
        if request.POST.get('deadline') != '':
            deadline=request.POST.get('deadline')
            project.deadline=deadline
        project.abstract=abstract
        project.status=status
        project.save()
        messages.success(request, 'Project updated successfully!')
        return redirect('view_projects')
    
    return render(request, "view_projects.html", {'projects': projects, 'members': members})

def add_member_to_project(request,mid,pid):
    project = Project.objects.get(id=pid)
    member = Profile.objects.get(id=mid)
    member.on_project = project
    member.save()
    messages.success(request, 'Member added to project successfully!')
    return redirect('view_projects')

def remove_member_from_project(request,mid):
    member = Profile.objects.get(id=mid)
    member.on_project = None
    member.save()
    messages.success(request, 'Member removed from project successfully!')
    return redirect('view_projects')



def myprojects(request):
    projects = Project.objects.filter(members=request.user).first()
    tasks=Task.objects.filter(project=projects).filter(user=request.user).order_by('-id')
    mytasks=DailyTasks.objects.filter(project=projects).filter(status="Not Started").filter(user=request.user).order_by('-id')
    if request.GET.get('tid'):
        dtask=DailyTasks.objects.get(id=request.GET.get('tid'))
        dtask.status="Completed"
        dtask.save()
        return redirect('view_project')

    if request.method == 'POST':
        description = request.POST.get('desc')
        file=request.FILES.get('file')
        user=request.user

        Task.objects.create(user=user, project=projects, description=description, file=file)
        messages.success(request, 'Task created successfully!')
        return redirect('view_project')


    return render(request, 'myprojects.html', {'projects': projects,'tasks':tasks,'mytasks':mytasks})



def teamtasks(request):
    projects = Project.objects.filter(members=request.user).first()
    tasks=Task.objects.filter(project=projects).order_by('-id')
    return render(request, 'teamtasks.html', {'tasks': tasks,'projects':projects})

def task_comment(request,task_id):
    task = Task.objects.get(id=task_id)
    comments=TaskComment.objects.filter(task=task).order_by('-id')
    context = {
        'task': task,
        'comments': comments,
        'task_id': task_id
    }
    messages.success(request, 'Comment added successfully!')
    if request.method == 'POST':
        comment = request.POST.get('comment')
        user = request.user
        TaskComment.objects.create(user=user, task=task, comment=comment)
        return redirect('task_comment', task_id=task_id)
    return render(request, 'task_comment.html',context)


def dailytasks(request):
    
    user=request.user
    if user.role == 'admin' or user.role == 'manager':
        pid=request.GET.get('pid')
        projects=Project.objects.get(id=pid)
        if request.method == 'POST':
            desc=request.POST.get('desc')
            DivideTasks.objects.create(project=projects,description=desc)
            messages.success(request, 'Task created successfully!')
            return redirect(f"{reverse('tasks')}?pid={pid}")

        tasks=DivideTasks.objects.filter(project=projects).order_by('-id')
        return render(request, 'dividetask.html', {'tasks': tasks,'pid':pid})
    
    if user.role == 'leader':
        projects=Project.objects.filter(members=request.user).first()
        members=Profile.objects.filter(on_project=projects)
        
        if request.method == 'POST':
            desc=request.POST.get('desc')
            uid=request.POST.get('uid')
            deadline=request.POST.get('deadline')



            DailyTasks.objects.create(project=projects,description=desc,user_id=uid,deadline=deadline)
            messages.success(request, 'Task created successfully!')
            return redirect('tasks')
        tasks=DailyTasks.objects.filter(project=projects).order_by('-id')
        return render(request, 'dailytasks.html', {
                                                    'projects': projects,
                                                    'members':members,
                                                    'tasks': tasks
                                                   })

def upload_final_file(request):
    projects = Project.objects.filter(members=request.user).first()
    if request.method=="POST":
        file=request.FILES.get('file')
        projects.final_file=file
        projects.save()
    return redirect('home')


