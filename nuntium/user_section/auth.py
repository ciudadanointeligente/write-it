# handle various auth tasks that social-auth requires us to
# implement ourselves
from social.exceptions import AuthFailed


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
