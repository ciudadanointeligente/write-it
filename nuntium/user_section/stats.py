from django.db.models import Count
from django.db.models import Q
from nuntium.user_section.views import WriteItInstanceDetailBaseView


class StatsPerInstance(object):
    def __init__(self, writeitinstance=None):
        self.writeitinstance = writeitinstance

    def get_stats(self):
        return [
            ('amount_of_messages', self.amount_of_messages),
            ('amount_of_public_messages', self.amount_of_public_messages),
            ('amount_of_private_messages', self.amount_of_private_messages),
            ('public_messages_with_answers', self.public_messages_with_answers),
            ('public_confirmed_messages', self.public_confirmed_messages),
        ]

    @property
    def amount_of_messages(self):
        return self.writeitinstance.message_set.count()

    @property
    def amount_of_public_messages(self):
        return self.writeitinstance.message_set.filter(public=True).count()

    @property
    def amount_of_private_messages(self):
        return self.writeitinstance.message_set.filter(public=False).count()

    @property
    def public_messages_with_answers(self):
        return (self.writeitinstance.message_set
            .annotate(num_answers=Count('answers'))
            .filter(public=True, num_answers__gt=0)
            .count())

    @property
    def public_confirmed_messages(self):
        return self.writeitinstance.message_set.filter(public=True, confirmated=True).count()


class StatsView(WriteItInstanceDetailBaseView):
    template_name = 'nuntium/profiles/stats.html'

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context['stats'] = StatsPerInstance(writeitinstance=self.object)
        return context
