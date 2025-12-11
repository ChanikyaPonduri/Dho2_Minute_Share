from django import forms

class UploadForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class CodeForm(forms.Form):
    code = forms.CharField(max_length=6)
