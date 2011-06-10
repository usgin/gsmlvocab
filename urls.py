from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^import/(?P<vocabulary>.+)$', 'gsmlvocab.views.import_vocabulary'),
)