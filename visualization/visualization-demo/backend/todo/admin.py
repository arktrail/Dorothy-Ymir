from django.contrib import admin
from .models import Todo  # add this


class TodoAdmin(admin.ModelAdmin):  # add this
    list_display = ('title', 'description', 'completed')  # add this


# Register your models here.
admin.site.register(Todo, TodoAdmin)  # add this
