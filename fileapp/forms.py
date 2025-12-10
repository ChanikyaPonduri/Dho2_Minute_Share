from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()

class CodeForm(forms.Form):
    code = forms.CharField(max_length=6)
