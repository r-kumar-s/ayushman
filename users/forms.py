from django import forms
from .models import User, PatientFollowup
from django.forms import inlineformset_factory

class UserForm(forms.ModelForm):
    dob = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = User
        fields = [
            'fname', 'lname', 'phone', 'email',
            'address', 'dob', 'referred_by'
        ]

class PatientFollowupForm(forms.ModelForm):
    class Meta:
        model = PatientFollowup
        exclude = ['user']
        fields = [
            'user',
            'diagnosis',
            'treatments',
            'prescription_file',
            'invoice_file',
            'followup_date',
        ]


PatientFollowupFormSet = inlineformset_factory(
    User,
    PatientFollowup,
    fields=['diagnosis', 'treatments', 'prescription_file', 'invoice_file','followup_date'],
    extra=1,   # extra empty form
    can_delete=True
)