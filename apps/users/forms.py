from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    telegram_id = forms.IntegerField(
        label='Telegram ID',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Telegram ID',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        telegram_id = cleaned_data.get('telegram_id')
        password = cleaned_data.get('password')

        if telegram_id and password:
            user = authenticate(telegram_id=telegram_id, password=password)
            if user is None:
                raise forms.ValidationError('Invalid Telegram ID or password.')
            if not user.is_active:
                raise forms.ValidationError('This account is inactive.')
            cleaned_data['user'] = user
        return cleaned_data
