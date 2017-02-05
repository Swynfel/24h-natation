from dal import autocomplete

from .models import Binet
from .user import User

class BinetAutocomplete(autocomplete.Select2QuerySetView):

	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return Binet.objects.none()

		binets=Binet.objects.all()

		if self.q:
			binets = binets.filter(name__contains=self.q)

		return binets

class UserAutocomplete(autocomplete.Select2QuerySetView):

	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return User.objects.none()

		users=User.objects.all()

		if self.q:
			users = users.filter(username__contains=self.q)

		return users


class SectionAutocomplete(autocomplete.Select2QuerySetView):

	def get_queryset(self):
		sections=Section.objects.all()

		if self.q:
			sections = sections.filter(username__contains=self.q)

		return sections