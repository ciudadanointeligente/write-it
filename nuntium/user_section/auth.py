# handle various auth tasks that social-auth requires us to
# implement ourselves
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse


from social.exceptions import AuthFailed
from social.pipeline.partial import partial


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if strategy.request.backend.name != 'email':
        return

    if is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('require_email')


def send_validation(strategy, backend, code):
    url = '{0}?verification_code={1}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code
    )
    url = strategy.request.build_absolute_uri(url)
    send_mail('Validate your account', 'Validate your account {0}'.format(url),
              settings.DEFAULT_FROM_EMAIL, [code.email], fail_silently=False)


def user_password(strategy, user, is_new=False, *args, **kwargs):
    if strategy.request.backend.name != 'email':
        return

    password = strategy.request_data().get('password')
    if is_new:
        user.is_active = False
        user.set_password(password)
        user.save()
    elif not user.check_password(password):
        raise AuthFailed(strategy.request.backend, 'Username or password wrong')


def set_active(strategy, user, is_new=False, *args, **kwargs):
    if strategy.request.backend.name != 'email':
        return

    user.is_active = True
    user.save()
