from django.shortcuts import render, redirect, HttpResponseRedirect
from django.template import loader
from api.models import Note, Author


def index(request, name=''):
    if 'uid' not in request.session.keys():
        request.session["uid"] = "anonimous"
    languages = []
    with open('notes/templates/ace_modes.txt', 'r') as f:
        languages = f.read().split('\n')
    context = {
        "settings": "disabled",
        "languages": languages
    }
    return render(request, 'index.html', context)
