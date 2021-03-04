from django import forms


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, label='الموضوع',empty_value=str())
    name = forms.CharField(max_length=100, label='الإسم')
    email = forms.EmailField(label='الإيميل')
    message = forms.CharField(widget=forms.Textarea,label='الرسالة')
