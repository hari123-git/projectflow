from django.contrib import admin


from .models import *
# Register your models here.

admin.site.register(Company)
admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TaskComment)
admin.site.register(DailyTasks)
admin.site.register(DivideTasks)
admin.site.register(Attendance)