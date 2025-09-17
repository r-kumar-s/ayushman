# import the standard Django Forms
# from built-in library
from django import forms

# creating a form
class ContactUsForm(forms.Form):
  fname = forms.CharField(max_length=200,required=True)
  lname = forms.CharField(max_length=200,required=False)
  sender = forms.EmailField(required=True)
  phone = forms.CharField(max_length=20,required=False)
  subject = forms.CharField(max_length=200,required=False)
  message = forms.CharField(widget=forms.Textarea,required=True)  
  cc_myself = forms.BooleanField(required=False)
