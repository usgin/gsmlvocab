from importer import import_from_url, clear_all_data, clear_vocabulary_data
from models import Vocabulary
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from urlparse import urljoin, urlparse, ParseResult, urlunparse
from BeautifulSoup import BeautifulSoup
import urllib2, re

# Change this for another version of the vocabularies
trunk_url = 'https://www.seegrid.csiro.au/subversion/CGI_CDTGVocabulary/trunk/Vocabulary201012/'
vocab_suffix = '201012.rdf'

def kill_them_all(request):
    try:
        clear_all_data()
    except Exception as (strerror):
        return HttpResponse('<h2>Failed!</h2><p>Unexpected Server Error.</p><p>' + strerror.args[0] + '</p>')
    else:
        return HttpResponse('<h2>Success! Data Cleared.</h2><a href="/admin/gsmlvocab/">Jump to Administration Page</a>')

def update_them_all(request):
    for vocab in Vocabulary.objects.all():
        if vocab.name == 'MappedFeatureObservationMethod201012': 
            pass
        try:
            import_from_url(vocab.skos_url, vocab)
        except Exception, ex:
            return HttpResponse('<h2>Failed!</h2><p>Unexpected Server Error.</p><p>' + str(ex) + '</p>')
        
    return HttpResponse('<h2>Success!</h2><a href="/admin/gsmlvocab/">Jump to Administration Page</a>')
    
def import_vocabulary(request, vocabulary):
    if vocabulary == 'all': 
        return update_them_all(request)
    
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
    # Kill off everything in the database first
    clear_all_data()
    
    req = urllib2.Request(trunk_url)
    listing = urllib2.urlopen(req)
    
    #Soupify
    soup = BeautifulSoup(listing)
    vocabularies = dict()
    
    # Loop through all the links to RDF files
    tags = soup.findAll('a', href=re.compile('.+\.rdf'))
    for tag in tags:
        # Generate an absolute URL to the RDF file
        vocabularies[tag.text.rstrip(vocab_suffix)] = urljoin(trunk_url, tag['href'])
        
    # Okay, now make all the vocabularies
    for vocab in vocabularies:
        this_one = Vocabulary.objects.create(name=vocab, skos_url=vocabularies[vocab])
        
    return update_them_all(request)

                                  
                                
        
        
        
        
        
        
        
        