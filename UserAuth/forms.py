from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from UserAuth.models import Review

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email','first_name','last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.is_active = False
        if commit:
            user.save()
        return user

class ReviewForm(forms.ModelForm):
    title = forms.CharField(max_length=100,
                            required=True,
                            widget=forms.TextInput()
                            )

    text = forms.CharField(widget=forms.Textarea)
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1,6)],
                               widget=forms.RadioSelect
                               )
    class Meta:
        model = Review
        fields = ['title', 'text', 'rating']
