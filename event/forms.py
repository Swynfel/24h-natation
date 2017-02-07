from django import forms

from dal import autocomplete

from .user import User
from .models import *

class BinetForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('__all__')
		widgets= {
			'binets': autocomplete.ModelSelect2Multiple(url='autocomplete-binet'),
		}

class NageForm(forms.ModelForm):
	class Meta:
		model = Nage
		fields = ('__all__')
		widgets= {
			'pour': autocomplete.ModelSelect2Multiple(url='autocomplete-binet'),
			'nageur': autocomplete.ModelSelect2(url='autocomplete-user'),
		
		}

import ldap3
from django.contrib.auth import authenticate, login

class Frankiz(object):
	serveur = ldap3.Server("frankiz.eleves.polytechnique.fr:389")

	def can_auth(self,username,password):
		connection = ldap3.Connection(self.serveur, 'uid='+username+',ou=eleves,dc=frankiz,dc=net', password)
		b = connection.bind()
		return b

	def get_info(self,username):
		connection = ldap3.Connection(self.serveur)
		connection.bind()
		connection.search('uid='+username+',ou=eleves,dc=frankiz,dc=net','(objectclass=Person)',attributes=['uid','givenName','sn','brPromo','mail','brMemberOf',])
		info = connection.entries[0]
		for group in info["brMemberOf"]:
			if len(group)>6 and group[:6]=='sport_':
				return (info,group[6:])
		return (info,'')

	def create(self,data,sport="none"):
		s,r=Section.objects.get_or_create(id=sport)
		if r:
			s.name=sport.title()
		s.save()
		if User.objects.filter(username=str(data['uid'])).exists():
			return User.objects.get(username=str(data['uid']))
		return User(username=str(data['uid']),section=s,first_name=str(data['givenName']),last_name=str(data['sn']),email=str(data['mail']))

class AuthForm(forms.Form):
	username = forms.CharField(label="Identifiant")
	password = forms.CharField(label="Mot de Passe",widget=forms.TextInput(attrs={'type':'password'}))
	
	def login(self,request):
		user = authenticate(username=self.cleaned_data['username'],password=self.cleaned_data['password'])
		if user is not None :
			login(request,user)
			return True
		return False

class RegisterForm(forms.Form):
	username = forms.CharField(label="Identifiant")
	first_name = forms.CharField(label="Prénom")
	last_name = forms.CharField(label="Nom")
	password = forms.CharField(label="Mot de Passe",widget=forms.TextInput(attrs={'type':'password'}))
	password_again = forms.CharField(label="Retappez votre Mot de Passe",widget=forms.TextInput(attrs={'type':'password'}))
	mail = forms.CharField(label="Mail")
	telephone = forms.CharField(label="Numéro de Téléphone")

	def is_valid(self):
		valid = super(forms.Form, self).is_valid()

		if not valid:
			return valid

		if self.cleaned_data['password']!=self.cleaned_data['password_again']:
			self._errors['password_match'] = 'Les mots de passes ne se correspondent pas'
			return False

		return True

	def local_create(self):
		data=self.cleaned_data
		section,c=Section.objects.get_or_create(id='ext',name="Exté")
		user = User(username=data['username'],nickname=data['username'],section=section,first_name=data['first_name'],last_name=data['last_name'],email=data['mail'],telephone=data['telephone'])
		user.set_password(password=data['password'])
		section.save()
		user.save()

class FrankizLogin(object):
	username = ''
	f=Frankiz()

	def __init__(self,username):
		self.username = username

	def frankiz_create(self):
		user=User.objects.none()
		data,sport = self.f.get_info(self.username)
		user=f.create(data,sport)
		user.save()

	def frankiz_user(self):
		user=User.objects.none()
		if not (self.frankiz_auth()):
			return user
		if not User.objects.filter(username=self.username).exists():
			self.frankiz_create()

	def frankiz_log(self,request):
		self.frankiz_user()
		user=User.objects.get(username=self.username)
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)