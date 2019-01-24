from django import forms

class ReviewForms(forms.Form):
        text=forms.CharField(widget=forms.Textarea, label='')
