from django.shortcuts import render
from django.http import HttpResponse
import json
import codecs
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import FormView
from .forms import ContactForm


def index(request):

    with codecs.open('my_posts.json' , 'r' , 'utf-8') as f:
        feeds = json.load(f)

    context = {
        'feeds':feeds,
        }
    return render(request, 'student_app/index.html' ,context)

def contact(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = request.POST['name']
            email = request.POST['email']
            message = request.POST['message']
            ms = name + email + message
            send_mail('Contact Form' , ms , settings.EMAIL_HOST_USER , ['alarefabdo1@gmail.com'] , fail_silently=False,)
    else:
        form = ContactForm(request.POST)

    context = {
        'form': form,
    }


    return render(request,'student_app/contact.html' , context)

# class ContactUs(ContactForm):
#     # form = ContactForm
#     template_name = 'student_app/contact.html'

#     # def get_success_url(self):
#     #     return reverse('success_view')

#     def form_valid(self, form):
#         name = form.cleaned_data.get('name')
#         email = form.cleaned_data.get('email')
#         password = form.cleaned_data.get('message')

#         send_mail('Contact Form',ms,settings.EMAIL_HOST_USER,['alarefabdo1@gmail.com'],fail_silently=False,)


