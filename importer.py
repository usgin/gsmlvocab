from lxml import etree
from models import Concept, Language, LanguageRelation, DefaultLabel, AltLabel, ConceptRelation
from django.conf import settings
import urllib2, psycopg2

test_file_name = '/home/rclark/Documents/git/gsmlvocab/skos/SimpleLithology201012.rdf'

ns = {'base': "&cgi;simplelithology",
      'dc': "http://purl.org/dc/elements/1.1/",
      'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
      'owl2xml': "http://www.w3.org/2006/12/owl2-xml#",
      'cgi': "http://resource.geosciml.org/classifierscheme/cgi/201012/",
      'SimpleLithology': "http://resource.geosciml.org/classifier/cgi/lithology/",
      'owl': "http://www.w3.org/2002/07/owl#",
      'xsd': "http://www.w3.org/2001/XMLSchema#",
      'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      'skos': "http://www.w3.org/2004/02/skos/core#",
      'xml': "http://www.w3.org/XML/1998/namespace",}

# These dictionaries make it a little easier to refer to fully-qualified element and attribute names
subeles = {'type': '{%s}type' % ns['rdf'],
          'source': '{%s}source' % ns['dc'],
          'prefLabel': '{%s}prefLabel' % ns['skos'],
          'definition': '{%s}definition' % ns['skos'],
          'narrower': '{%s}narrower' % ns['skos'],
          'broader': '{%s}broader' % ns['skos'],
          'related': '{%s}related' % ns['skos'],
          'inScheme': '{%s}inScheme' % ns['skos'],
          'altLabel': '{%s}altLabel' % ns['skos'],
          'seeAlso': '{%s}seeAlso' % ns['rdfs'],}

attribs = {'lang': '{%s}lang' % ns['xml'],
           'about': '{%s}about' % ns['rdf'],
           'resource': '{%s}resource' % ns['rdf'],}

def db_connection():
    dbname = settings.DATABASES['default']['NAME']
    username = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    return psycopg2.connect('dbname=%s user=%s password=%s' % (dbname, username, password))

def clear_all_data():
    db = db_connection()
    
    tables = ['gsmlvocab_altlabel',
              'gsmlvocab_concept',
              'gsmlvocab_concept_symmetric_concepts',
              'gsmlvocab_conceptrelation',
              'gsmlvocab_defaultlabel',
              'gsmlvocab_language',
              'gsmlvocab_languagerelation',
              'gsmlvocab_vocabulary'
        ]
    
    curs = db.cursor()
    curs.execute('TRUNCATE TABLE ' + ', '.join(tables))
    
    db.commit()
    
def clear_vocabulary_data(vocabulary):
    # Deleting a concept deletes anything with a foreign key pointing at it
    Concept.objects.filter(vocabulary=vocabulary).delete()
    
    # The only things that shouldn't have been removed are DefaultLabels. These I have
    #  to run through and find any that have no LanguageRelation
    for label in DefaultLabel.objects.all():
        if len(LanguageRelation.objects.filter(default_label=label)) == 0:
            label.delete()

def get_concept_uri(concept):
    try:
        return concept.attrib[attribs['about']]
    except Exception, ex:
        # If there's no rdf:about attribute, then skip it.
        return None
        
def create_concepts(items, vocabulary):
    # Given the results of an XPath query for either skos:Concepts or owl:Things, 
    #  gather the URI and description of each, create a Concept
    
    # Assumes that the RDF file is valid, and that URIs are unique!
    
    for item in items:
        uri = get_concept_uri(item)
        if uri is not None:
            definition = item.xpath('skos:definition', namespaces=ns)
            if len(definition) > 0:
                new_concept = Concept(uri=uri, definition=definition[0].text, vocabulary=vocabulary)
                new_concept.save()

def create_languages(doc):
    # Create a unique list of all Languages in the parsed document
    languages= list()
    path = '//@xml:lang'
    
    for result in doc.xpath(path, namespaces=ns):
        if result not in languages:
            languages.append(result)
            
    for lang in languages:
        if len(Language.objects.filter(abbreviation=str(lang))) == 0:
            new_language = Language(abbreviation=str(lang))
            new_language.save()
        
def import_from_url(url, vocabulary):
    # First, clear the vocabulary
    clear_vocabulary_data(vocabulary)
    
    # Get the RDF doc
    req = urllib2.Request(url)
    content = urllib2.urlopen(req)
                
    # Parse the mofo
    doc = etree.parse(content)
    
    # First time through, need to create objects without populating relationships.
    #  This means creating Languages and Concepts.
    # We can't create the relationships on the first go because the related objects
    #  may not exist yet.
    
    # Languages:
    create_languages(doc)
    
    # Concepts:
    paths = ['/rdf:RDF/skos:Concept', '/rdf:RDF/owl:Thing']
    for path in paths:
        results = doc.xpath(path, namespaces=ns)
        create_concepts(results, vocabulary)
    
    # Now that Languages and Concepts exist, we can build relationships between them
    # Loop through the Concepts in the document again, this time gathering relationship and label info
    for path in paths:
        results = doc.xpath(path, namespaces=ns)
        for concept in results:            
            # Lookup this Concept
            uri = get_concept_uri(concept)
            if uri is not None:
                try:
                    this_concept = Concept.objects.get(uri=uri)
                except Exception, ex:
                    # If we didn't find it, that's because the builder said it wasn't worthy. Skip it.
                    pass
                else:
                    # Dictionaries and lists for the various labels
                    default_labels = dict()
                    alt_labels = list()
                    
                    # Lists for narrower, broader and related concepts
                    narrower = list()
                    broader = list()
                    related = list()
                    
                    # Cycle through the subelements of the concept
                    for prop in concept:
                        # Here are the three kinds of labels
                        if prop.tag == subeles['prefLabel']:
                            default_labels[prop.attrib.get(attribs['lang'], 'en')] = prop.text
                        if prop.tag == subeles['altLabel']:
                            alt_labels.append({'lang': prop.attrib.get(attribs['lang'], 'en'), 'label': prop.text, 'type': 'alt'})
                        if prop.tag == subeles['seeAlso']:
                            alt_labels.append({'lang': prop.attrib.get(attribs['lang'], 'en'), 'label': prop.text, 'type': 'see_also'})
                            
                        # Here are the different kinds of relationships between concepts
                        if prop.tag == subeles['narrower']:
                            narrower.append(prop.attrib.get(attribs['resource']))
                        if prop.tag == subeles['broader']:
                            broader.append(prop.attrib.get(attribs['resource']))
                        if prop.tag == subeles['related']:
                            related.append(prop.attrib.get(attribs['resource']))
                            
                    # Build Default Label relationships
                    for lang in default_labels:
                        # Create the DefaultLabel first
                        new_def_label = DefaultLabel(label = default_labels[lang])
                        new_def_label.save()
                        
                        # Get the Language
                        this_language = Language.objects.get(abbreviation=lang)
                        
                        # Make the LanguageRelation
                        new_lang_rel = LanguageRelation(concept=this_concept, language=this_language, default_label=new_def_label)
                        new_lang_rel.save()
                        
                    # Build the Alt and SeeAlso Labels
                    for label in alt_labels:
                        # Find the appropriate LanguageRelation
                        try:
                            the_lang_rel = LanguageRelation.objects.filter(concept=this_concept).get(language__abbreviation=label['lang'])
                        except Exception, ex:
                            # There's no default label for this particular language. Need to make a new LanguageRelation
                            the_lang_rel = LanguageRelation(concept=this_concept, language=Language.objects.get(abbreviation=label['lang']))
                            the_lang_rel.save()
                        
                        # Make the AltLabel
                        new_alt = AltLabel(alt_type=label['type'], language_relation=the_lang_rel, label=label['label'])
                        new_alt.save()
                        
                    # Build the Related Concepts
                    for concept in related:
                        # Check if the relationship has already been built
                        if len(this_concept.symmetric_concepts.filter(uri=concept)) == 0:
                            # Build the relationship
                            this_concept.symmetric_concepts.add(Concept.objects.get(uri=concept))
                    
                    # Build the Broader Relationships
                    for concept in broader:
                        # Check if the relationship has already been built
                        if len(this_concept.broader.filter(broader_concept__uri=concept)) == 0:
                            # Build the relationship
                            this_concept.broader.add(ConceptRelation.objects.create(broader_concept=Concept.objects.get(uri=concept), narrower_concept=this_concept))
                    
                    # Build the Narrower Relationships
                    for concept in narrower:
                        if len(this_concept.narrower.filter(narrower_concept__uri=concept)) == 0:
                            this_concept.narrower.add(ConceptRelation.objects.create(narrower_concept=Concept.objects.get(uri=concept), broader_concept=this_concept))      
                    
                
                    
                 
                    
                    