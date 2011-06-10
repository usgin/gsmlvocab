from django.conf.urls.defaults import patterns

urlpatterns = patterns('gsmlvocab.views',
    (r'^update/(?P<vocabulary>.+)$', 'import_vocabulary'),
    (r'^clear/(?P<vocabulary>\d+)$', 'clear_a_vocabulary'),
    (r'^scrape-trunk/$', 'scrape_the_trunk'),
    (r'^kill/$','kill_them_all'),
)