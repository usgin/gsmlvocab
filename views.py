from importer import import_from_url
from models import Vocabulary
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def import_vocabulary(request, vocabulary):
    this_vocabulary = get_object_or_404(Vocabulary, name=vocabulary)
    try:
        import_from_url(this_vocabulary.skos_url, this_vocabulary)
        return HttpResponse('It Worked!')
    except Exception, ex:
        return HttpResponse('So Sorry. It Failed: ' + str(ex))