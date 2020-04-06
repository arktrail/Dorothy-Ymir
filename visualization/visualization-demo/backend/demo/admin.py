from django.contrib import admin
from .models import Tree

# Register your models here.


class DemoAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'prob', 'true')


admin.site.register(Tree, DemoAdmin)
