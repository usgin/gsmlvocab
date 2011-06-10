from django.contrib import admin
from models import Concept, DefaultLabel, AltLabel, Language, ConceptRelation, LanguageRelation, Vocabulary

class NarrowerAdmin(admin.TabularInline):
    model = ConceptRelation
    fk_name = 'broader_concept'
    extra = 1
    verbose_name = 'Narrower Concept'
    
class BroaderAdmin(admin.TabularInline):
    model = ConceptRelation
    fk_name = 'narrower_concept'
    extra = 1
    verbose_name = 'Broader Concept'
    
class LangRelAdmin(admin.TabularInline):
    model = LanguageRelation
    extra = 1
    verbose_name = 'Language'
    
class ConceptAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'definition', 'uri']
    list_filter = ['vocabulary']
    search_fields = ['uri', 
                     'definition', 
                     'languagerelation__default_label__label',
                     'languagerelation__altlabel__label']
    fields = ['uri', 'definition']
    readonly_fields = ['uri', 'definition']
    #inlines = [LangRelAdmin, NarrowerAdmin, BroaderAdmin]

admin.site.register(Concept, ConceptAdmin)
#admin.site.register(DefaultLabel)
#admin.site.register(AltLabel)
#admin.site.register(Language)
admin.site.register(Vocabulary)