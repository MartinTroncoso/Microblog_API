from django.contrib import admin
import Microblog_API.models as models

admin.site.register(models.Post)
admin.site.register(models.Comment)