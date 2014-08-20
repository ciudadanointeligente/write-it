## In order to run in heroku we need to

- Create an account
- Install heroku toolbelt (https://toolbelt.heroku.com/)
- Create an app
- Copy the Git Url
- Add heroku as a remote in your project `git remote add heroku git@heroku.com:your-app.git`
- Add heroku postgres (get add-ons) `heroku addons:add heroku-postgresql`
- Push the code over to heroku `git push heroku current_branch:master`
- heroku run python manage.py syncdb --noinput --migrate
- Create a super user `heroku run python manage.py createsuperuser` and answer the questions in the prompt
- Allow google oauth login:

	You'll need to go to google console and get a OAUTH2 new Client ID. And where it says "Redirect URIS" you should add something like http://<your-app>.herokuapp.com/social_auth/complete/google-oauth2/. Remember to change <your-app> for the name of your app.
	Once you've done that run `heroku config:set SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=<YOUR-SECRET> SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=<YOUR-SOCIAL-AUTH-ID>`

- Add postmark as an add-on in heroku and when you're done you should create a postmark signature.

	Make sure to take note which one is the "from email" and that you have access to that email, because a confirmation email is going to be sent to you.
	Now you should run the following command in order to set the environment variables.
	`heroku config:set DEFAULT_FROM_EMAIL=<The email in the postmark signature> DEFAULT_FROM_DOMAIN=<The same domain as in default from email> EMAIL_HOST=<EMAIL_HOST> EMAIL_PORT=<EMAIL_PORT> EMAIL_HOST_USER=<EMAIL_HOST_USER> EMAIL_HOST_PASSWORD=<EMAIL_HOST_PASSWORD> EMAIL_USE_TLS=True EMAIL_USE_SSL=True`

	We also will need to define that every email should go from the single DEFAULT_FROM_EMAIL.
	This is because postmark allows you to have one single email signature or from where the emails will go from.
	`heroku config:set SEND_ALL_EMAILS_FROM_DEFAULT_FROM_EMAIL=True`. If you get to send emails from a bunch of emails with only one domain (for example fiera@domain.com, mouse@domain.com, etc) you don't need this.


## TODO

- Automatically create a contact type for mailit with label_name="Electronic Mail" and name="e-mail"
- Workout inbound email
- It seems that there is a bug when creating a message for someone without contacts =/
- Define default site.
- Define a reply-to when sending a message to a person.

## NOTICE

This is instructions are not ready yet and therefore are very prone to errors please let us know of any.
 