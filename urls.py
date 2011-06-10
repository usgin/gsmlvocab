from django.conf.urls.defaults import patterns

urlpatterns = patterns('gsmlvocab.views',
    (r'^import/(?P<vocabulary>\d+)$', 'import_vocabulary'),
    (r'^clear/(?P<vocabulary>\d+)$', 'clear_a_vocabulary'),
    (r'^kill/$','kill_them_all'),
)