from django import forms

class ContactInstanceOwnerForm(forms.Form):

    from_email = forms.EmailField()
    message_content = forms.CharField(widget=forms.Textarea)
