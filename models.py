from django.db import models

class Language(models.Model):
    # A language for a particular label
    abbreviation = models.CharField(max_length=10)
    
    def __unicode__(self):
        return self.abbreviation
    
class ConceptRelation(models.Model):
    # Relationship between concepts
    broader_concept = models.ForeignKey('Concept', related_name='narrower')
    narrower_concept = models.ForeignKey('Concept', related_name='broader')
    
class LanguageRelation(models.Model):
    concept = models.ForeignKey('Concept')
    language = models.ForeignKey('Language')
    default_label = models.ForeignKey('DefaultLabel', blank=True, null=True)

class DefaultLabel(models.Model):
    # Default labels for concepts in a given language
    label = models.CharField(max_length=255)
    
    def __unicode__(self):
        return 'Default: ' + self.label
    
ALT_LABEL_CLASSES = [('alt', 'Alt'), ('see_also', 'See Also')]
class AltLabel(models.Model):
    # Alt and see also labels for concepts in a specific language
    alt_type = models.CharField(max_length=10, choices=ALT_LABEL_CLASSES)
    label = models.CharField(max_length=255)
    language_relation = models.ForeignKey('LanguageRelation')
    
    def __unicode__(self):
        return self.alt_type + ': ' + self.label

class Vocabulary(models.Model):
    class Meta:
        verbose_name_plural = 'Vocabularies'
        
    # A Vocabulary
    name = models.CharField(max_length=255)
    skos_url = models.URLField()
    
    def __unicode__(self):
        return self.name
    
class Concept(models.Model):
    # A vocabulary term
    definition = models.TextField()
    related_concepts = models.ManyToManyField('Concept', through=ConceptRelation)
    symmetric_concepts = models.ManyToManyField('Concept', related_name='Related Conc')
    languages = models.ManyToManyField('Language', through=LanguageRelation)
    uri = models.CharField(max_length=255)
    vocabulary = models.ForeignKey('Vocabulary')
    
    def __unicode__(self):
        en = self.languagerelation_set.get(language__abbreviation = 'en')
        return en.default_label.label


