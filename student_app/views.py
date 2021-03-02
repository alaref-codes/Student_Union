from django.shortcuts import render
from django.http import HttpResponse
import json
import codecs
from django.core.mail import send_mail
from django.conf import settings


def index(request):

    with codecs.open('my_posts.json' , 'r' , 'utf-8') as f:
        feeds = json.load(f)

    context = {
        'feeds':feeds,
        }
    return render(request, 'student_app/index.html' ,context)

def contact(request):

    if request.method == 'POST':
        message = request.POST['message']
        send_mail('Contact Form',message,settings.EMAIL_HOST_USER,['alarefabdo1@gmail.com'],fail_silently=False,)

    return render(request,'student_app/contact.html')
