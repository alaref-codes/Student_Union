from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse,JsonResponse
import json,codecs,time,requests
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import FormView
from .forms import ContactForm
from .utils import main
from django.contrib import messages

def index(request):

    main()
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
            ms = name + '\n' + email + '\n' + message
            send_mail(subject , ms , settings.EMAIL_HOST_USER , ['alarefabdo1@gmail.com'] , fail_silently=False,)
            form = ContactForm()


    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request,'student_app/contact.html' , context)
