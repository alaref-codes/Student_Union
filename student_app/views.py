from django.shortcuts import render,redirect
from django.http import HttpResponse
import json
import codecs
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import FormView
from .forms import ContactForm
from . import main


def index(request):

    main.main()

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
            subject = request.POST['subject']
            name = request.POST['name']
            email = request.POST['email']
            message = request.POST['message']
            ms = name + email + message
            send_mail(subject , ms , settings.EMAIL_HOST_USER , ['alarefabdo1@gmail.com'] , fail_silently=False,)

    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request,'student_app/contact.html' , context)

