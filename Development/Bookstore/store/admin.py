from django.contrib import admin

from .models import Books,Author

class BookModels(admin.ModelAdmin):


    list_display = ('title','Auther','Publish_date','Prize','stack')

class AuthorModels(admin.ModelAdmin):
    list_display = ('first_name','middle_name','last_name')

admin.site.register(Books,BookModels)
admin.site.register(Author,AuthorModels)
