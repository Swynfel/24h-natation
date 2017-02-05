from django.contrib import admin
from .user import User, UserAdmin
from .models import *

admin.site.register(User)
admin.site.register(Binet)
admin.site.register(Section)
admin.site.register(Nage)
admin.site.register(Activity)
admin.site.register(Equipe)