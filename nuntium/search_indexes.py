# coding=utf-8
from haystack import indexes
from nuntium.models import Message

class MessageIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)

	def get_model(self):
		return Message

	def index_queryset(self, using=None):
		return self.get_model().objects.filter(public=True, confirmated=True)