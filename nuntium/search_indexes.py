# coding=utf-8
from haystack import indexes
from nuntium.models import Message

class MessageIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True)

	def get_model(self):
		return Message