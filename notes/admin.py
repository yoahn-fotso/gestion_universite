from django.contrib import admin
from .models import Session, CodeAnonyme, NoteAnonyme, Note

admin.site.register(Session)
admin.site.register(CodeAnonyme)
admin.site.register(NoteAnonyme)
admin.site.register(Note)
