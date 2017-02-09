from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse, reverse_lazy
from constance import config
from .models import *
from .user import *

from django.contrib.admin.views.decorators import staff_member_required

from django.views import generic
from . import forms 
from natation24h.settings import FKZ_KEY
import time
import json
import hashlib
import ldap3
from .forms import FrankizLogin, Frankiz
from django.utils.http import urlencode
from django.contrib.auth import login,logout

def render(request, template, status=200, **context):
	content = loader.get_template(template)
	context.update(extracontext(request))
	response = HttpResponse(content.render(context, request))
	response.status_code = status
	return response

def extracontext(request):
	context=dict()
	context['logged']=request.session.get('logged',False)
	context['username']=request.session.get('username','')
	if context['logged']:
		context['player']=Player.objects.get(username=context['username'])
	context['config']=config
	return context

def index(request):
	return render(request, "index.html")

def simple(request):
	return render(request, "empty.html")

def summary(request):
	return render(request, "summary.html", activities=Activity.objects.order_by('info'))

def activity(request,activity):
	a = Activity.objects.get(id=activity)
	if a==None:
		raise Http404("L'Activité n'existe pas")
	state=''
	if request.user == None:
		state=''
	elif a in request.user.activites.all():
		state='in'
	elif not a in request.user.activites.all():
		state='out'
	return render(request, "activity.html", activity=a, state=state)

from bulk_update.helper import bulk_update

@staff_member_required
def recompute(request):
	sections_score={}
	binets_score={}
	users = User.objects.all()
	for p in users:
		d = 0
		for nage in Nage.objects.filter(nageur=p):
			d += nage.distance()
			l = nage.pour.count()
			for b in nage.pour.all() :
				binets_score[str(b)]=binets_score.get(str(b),0)+(d/l)
		if p.section!=None:
			sections_score[p.section.id]=sections_score.get(p.section.id,0)+d
		p.distance=d
	bulk_update(users,update_fields=['distance'])
	print(sections_score)
	sections = Section.objects.all()
	for s in sections:
		s.distance = int(sections_score.get(s.id,0))
	bulk_update(sections,update_fields=['distance'])
	binets = Binet.objects.all()
	for b in binets:
		b.distance = int(binets_score.get(str(b),0))
	bulk_update(binets,update_fields=['distance'])

def ranking(request):
	recompute(request)
	s = Section.objects.order_by('-distance')
	section_rank = {'name':'Sections','content':[{'rank':i+1,'data':s[i]} for i in range(0,len(s))]}
	b = Binet.objects.order_by('-distance')[:40]
	binet_rank = {'name':'Binets','content_1':[{'rank':i+1,'data':b[i]} for i in range(0,min(20,len(b)))],'content_2':[{'rank':i+1,'data':b[i]} for i in range(20,min(20,len(b)))]}
	d = User.objects.exclude(distance=0).order_by('-distance')[:20]
	individual_rank = {'name':'Individuels','content':[{'rank':i+1,'data':d[i]} for i in range(0,min(15,len(d)))]}
	return render(request, "ranking.html", section_rank=section_rank,binet_rank=binet_rank,individual_rank=individual_rank)

def optin(request,activity):
	a = Activity.objects.get(id=activity)
	if a==None:
		raise Http404("L'Activité n'existe pas")
	request.user.activites.add(a)
	return HttpResponseRedirect(reverse("activity",args=(activity,)))

def optout(request,activity):
	a = Activity.objects.get(id=activity)
	if a==None:
		raise Http404("L'Activité n'existe pas")
	request.user.activites.remove(a)
	return HttpResponseRedirect(reverse("activity",args=(activity,)))

@staff_member_required
def hackldap(request):
	f=Frankiz()
	connection = ldap3.Connection(f.serveur)
	connection.bind()
	for section in Section.objects.all():
		values = str(section.id).split('_')
		if len(values)>1:
			s = values[0]
			year = values[1]
			sport = "sport_"+s
			connection.search('ou=eleves,dc=frankiz,dc=net','(&(&(objectclass=Person)(brMemberOf='+sport+'))(brMemberOf=promo_x20'+year+'))',attributes=['uid','givenName','sn','brPromo','mail','brMemberOf',])
			for user in connection.entries:
				f.create(user,section.id).save()

def hackview(request):
	hackldap(request)
	return HttpResponseRedirect(reverse("admin:index"))

def signupview(request):
	form=forms.RegisterForm()
	if request.POST:
		form = forms.RegisterForm(request.POST)
		if form.is_valid():
			form.local_create()
			request.POST=None
			return HttpResponseRedirect(reverse("index"))
		return render(request, "login.html", form=form)
	return render(request, "signup.html", form=form)

def loginview(request):
	form = forms.AuthForm()
	if request.POST:
		form = forms.AuthForm(request.POST)
		if form.is_valid() and form.login(request):
			return HttpResponseRedirect(reverse("index"))
		return render(request, "login.html", form=form)
	return render(request, "login.html", form=form)

def logoutview(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def frankiz_ask(request):
	ts = time.time()
	page = r"http://24hnatation.binets.fr/login/frankiz/answer/"
	r = json.dumps(["names"])
	h = hashlib.md5((str(ts) + str(page) + str(FKZ_KEY) + str(r)).encode('utf-8')).hexdigest()
	return HttpResponseRedirect("https://www.frankiz.net/remote?"+urlencode([('timestamp',ts),('site',page),('hash',h),('request',r)]))

def frankiz_login(request):
	if not "timestamp" in request.GET.keys() or not "response" in request.GET.keys() or not "hash" in request.GET.keys(): 
	    return HttpResponseRedirect(reverse("login"))
	response = request.GET.get("response")
	ts = request.GET.get("timestamp")
	h = request.GET.get("hash")

	if abs(int(round(float(time.time()))) - int(round(float(ts)))) > 600:
		return HttpResponseRedirect(reverse("login"))

	if hashlib.md5((ts + FKZ_KEY + response).encode('utf-8')).hexdigest() != h:
		return HttpResponseRedirect(reverse("login"))

	f = FrankizLogin(str(json.loads(response)['hruid']))
	user = f.frankiz_user()
	login(request,user)

	return HttpResponseRedirect(reverse('index'))

class FormView(generic.UpdateView):
	model = Nage
	form_class = forms.NageForm
	template_name = "form.html"
	success_url = reverse_lazy('form')

	def get_object(self):
		return Nage.objects.first()

class NageFormView(generic.UpdateView):
	model = Nage
	form_class = forms.NageForm
	template_name = 'form.html'
	success_url = reverse_lazy('nage-form')

	def get_object(self):
		return Nage.objects.first()

def nages(request):
	def nagestr(x,y):
		return "nage"+str(x)+"-"+str(y)
	nages = []
	COLORS=('white','red','orange','green','blue')
	LINE_NUM=request.GET.get("line_num",3)
	SWIM_NUM=request.GET.get("swim_num",5)
	for line in range(0,LINE_NUM):
		nages.append([])
		for swim in range(0,SWIM_NUM):
			nages[line].append({'id':nagestr(line,swim),'name':'Ligne '+str(line)+" - Pax "+str(swim),'form':forms.NageForm(prefix=nagestr(line,swim)+":"),'color':COLORS[swim]})
	if request.POST:
		for line in range(0,LINE_NUM):
			for swim in range(0,SWIM_NUM):
				f=forms.NageForm(request.POST,prefix=nagestr(line,swim)+":")
				nages[line][swim]['form']=f
				if ("save-"+nagestr(line,swim) in request.POST) or ("save-all" in request.POST) or ("send-"+nagestr(line,swim) in request.POST):
					if f.is_valid():
						f.save()
					if "send-"+nagestr(line,swim) in request.POST:
						nages[line][swim]['form']=forms.NageForm(prefix=nagestr(line,swim)+":")
	return render(request, 'nages.html', nages=nages)
