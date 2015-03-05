# coding=utf-8
from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex
from .models import Message, Answer


class MessageIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    writeitinstance = indexes.IntegerField(model_attr='writeitinstance__id')

    def get_model(self):
        return Message

    def index_queryset(self, using=None):
        return self.get_model().public_objects.all()


class AnswerIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    writeitinstance = indexes.IntegerField(model_attr='message__writeitinstance__id')

    def get_model(self):
        return Answer

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(message__in=Message.public_objects.all())
