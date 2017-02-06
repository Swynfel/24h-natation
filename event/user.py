from .models import *
from django.db.models import CharField, ManyToManyField, ForeignKey, IntegerField
from django.contrib.auth import admin,forms
from django.contrib.auth import models as defaultmodels

class User(defaultmodels.AbstractUser):
	nickname = CharField("Pseudo",max_length=64)
	section = ForeignKey(Section,blank=True,null=True)
	binets = ManyToManyField(Binet,blank=True)
	activites = ManyToManyField(Activity,blank=True)
	telephone = IntegerField(blank=True,null=True)
	distance = IntegerField(blank=True,null=True)

class UserChangeForm(forms.UserChangeForm):
	class Meta(forms.UserChangeForm.Meta):
		model = User

class UserAdmin(admin.UserAdmin):
	form = UserChangeForm

	fieldsets = admin.UserAdmin.fieldsets + ((None, {'fields' : (
			'nickname',
			'binets',
		)}),)