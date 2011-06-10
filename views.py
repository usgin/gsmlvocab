from importer import import_from_url, clear_all_data, clear_vocabulary_data
from models import Vocabulary
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import urllib2

def kill_them_all(request):
    try:
        clear_all_data()
    except Exception as (strerror):
        return HttpResponse('<h2>Failed!</h2><p>Unexpected Server Error.</p><p>' + strerror.args[0] + '</p>')
    else:
        return HttpResponse('<h2>Success! Data Cleared.</h2><a href="/admin/gsmlvocab/">Jump to Administration Page</a>')
    
def import_vocabulary(request, vocabulary):
    this_vocabulary = get_object_or_404(Vocabulary, pk=vocabulary)
    try:
        import_from_url(this_vocabulary.skos_url, this_vocabulary)
        return HttpResponse('It Worked!')
    except Exception, ex:
        return HttpResponse('So Sorry. It Failed: ' + str(ex))

def clear_a_vocabulary(request, vocabulary):
    this_vocabulary = get_object_or_404(Vocabulary, pk=vocabulary)
    try:
        clear_vocabulary_data(this_vocabulary)
    except Exception, ex:
        return HttpResponse('<h2>Failed!</h2><p>Unexpected Server Error.</p><p>' + str(ex) + '</p>')
    else:
        return HttpResponse('<h2>Success! ' + this_vocabulary.name + ' Data Cleared.</h2><a href="/admin/gsmlvocab/">Jump to Administration Page</a>')
         
def scrape_the_trunk(request):
    trunk_url = 'https://www.seegrid.csiro.au/subversion/CGI_CDTGVocabulary/trunk/Vocabulary201012/'