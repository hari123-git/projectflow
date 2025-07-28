from django.db import models
from django.contrib.auth.models import AbstractUser


import os
from django.utils.timezone import now


class Company(models.Model):
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('leader', 'Leader'),
        ('member', 'Member'),

    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='developer')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company', null=True, blank=True)
    on_project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='members', null=True, blank=True)

    def __str__(self):
        return self.username
    

class Project(models.Model):
    name = models.CharField(max_length=500)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    abstract = models.TextField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    deadline = models.DateField()
    status=models.CharField(max_length=500,default="Not Started")
    created_at = models.DateTimeField(auto_now_add=True)

    final_file = models.FileField(upload_to='final_files/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class DailyTasks(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dailytasks')
    description = models.TextField()
    deadline = models.DateTimeField()
    status=models.CharField(max_length=500,default="Not Started")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name}_{self.user.username}_{self.created_at.strftime('%Y-%m-%d-%H:%M:%S')}"
    
class DivideTasks(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dividetasks')
    description = models.TextField()
    status=models.CharField(max_length=500,default="Not Started")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name}"

    
class Task(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    file = models.FileField(upload_to='task_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name}_{self.user.username}_{self.created_at.strftime('%Y-%m-%d-%H:%M:%S')}"
    
    def save(self, *args, **kwargs):
            if self.file and not self.pk:
                timestamp = now().strftime('%Y-%m-%d-%H_%M_%S') 
                ext = os.path.splitext(self.file.name)[-1]
                self.file.name = f"{self.project.name}_{self.user.username}_{timestamp}{ext}"

            super().save(*args, **kwargs)


class TaskComment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.project.name}_{self.task.user.username}_{self.created_at.strftime('%Y-%m-%d-%H:%M:%S')}"



class Attendance(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}_{self.project.name}_{self.date}"