from random import choice
from .models import Note, Author
from string import ascii_letters, digits
from os import remove, path
from django.db.models import Q


def generate_notename():
    name = "".join(choice(ascii_letters + digits) for _ in range(4))
    while Note.objects.filter(name=name).exists():
        name = "".join(choice(ascii_letters + digits) for _ in range(4))
    return name


def generate_authorname():
    name = "".join(choice(ascii_letters + digits) for _ in range(16))
    while Author.objects.filter(uid=name).exists():
        name = "".join(choice(ascii_letters + digits) for _ in range(16))
    return name


def author_retrieve_or_create(request):
    author = None
    if "uid" in request.session.keys():
        author = Author.objects.filter(uid=request.session["uid"])
        if not author.exists():
            author = None
        else:
            author = author[0]
    if author == None:
        author = Author(uid=generate_authorname())
        request.session['uid'] = author.uid
        author.save()
    return author, request


def note_create(author):
    note = Note(
        name=generate_notename(),
        author=author,
        language='ace/mode/plain_text',
    )
    note.save()
    with open(f'sources/{note.name}', 'w+') as f:
        f.write('')
    return note


def note_retrieve(notename, session):
    note = None
    author = None

    if "uid" in session.keys():
        author = Author.objects.filter(uid=session["uid"])
        if not author.exists():
            author = None
        else:
            author = author[0]
    if author != None:
        note = Note.objects.filter(Q(name=notename) & Q(author=author))
        if note.exists():
            note = note[0]
        else:
            note = None
            author = None

    if note == None:
        note = Note.objects.filter(Q(name=notename) & Q(published=True))
        author = None
        if note.exists():
            note = note[0]
        else:
            note = None

    return note, author != None


def note_update(payload, note):
    allowed_keys = ['language', 'published', 'protected', 'collaborator_link']
    for key in payload.keys():
        if key in allowed_keys:
            setattr(note, key, payload[key])
    note.save()
    if 'source' in payload.keys():
        with open(f'sources/{note.name}', 'w+') as f:
            f.write(f'{payload["source"]}')
    if "onclose" in payload.keys() and payload["onclose"]:
        if len(payload["source"]) == 0:
            if path.exists(f'sources/{note.name}'):
                remove(f'sources/{note.name}')
            note.delete()


def note_delete(note):
    if path.exists(f'sources/{note.name}'):
        remove(f'sources/{note.name}')
    note.delete()
