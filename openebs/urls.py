from django.conf.urls import patterns, url
from openebs.views import MessageListView, MessageCreateView

urlpatterns = patterns('',
    url(r'^$', MessageListView.as_view(), name="msg_index"),
    url(r'^add$', MessageCreateView.as_view(), name="msg_add")
)