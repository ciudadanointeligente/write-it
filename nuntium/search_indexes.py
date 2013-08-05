# coding=utf-8
from haystack import indexes
from nuntium.models import Message, Answer

class MessageIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	rendered = indexes.CharField(use_template=True, indexed=False, template_name='nuntium/message/message_in_search_list.html')

	def get_model(self):
		return Message

	def index_queryset(self, using=None):
		return self.get_model().objects.public()


class AnswerIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	rendered = indexes.CharField(use_template=True, indexed=False, template_name='nuntium/answer/answer_in_search_list.html')

	def get_model(self):
		return Answer

	def index_queryset(self, using=None):
		return self.get_model().objects.filter(message__in=Message.objects.public())