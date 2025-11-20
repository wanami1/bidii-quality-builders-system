from django.contrib import admin
from .models import Team, Project, Worker, Skill, Payment, Task, TeamMember, JobApplication, TimeLog

admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Worker)
admin.site.register(Skill)
admin.site.register(Payment)
admin.site.register(Task)
admin.site.register(TeamMember)
admin.site.register(JobApplication)
admin.site.register(TimeLog)