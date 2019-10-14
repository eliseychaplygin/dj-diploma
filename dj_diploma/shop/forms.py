from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ReviewForm(forms.Form):
    name = forms.CharField(
        min_length=2,
        max_length=128,
        label='Имя',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'name',
                'aria-describedby': 'nameHelp',
                'name': 'name',
                'data-cip-id': 'name',
                'placeholder': 'Представьтесь',
            })
    )
    content = forms.CharField(
        label='Содержание',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'id': 'content',
                'name': 'description',
                'placeholder': 'Содержание',
                'rows': '',
                'cols': ''
            })
    )
    rating = forms.ChoiceField(
        label='',
        choices=(('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)),
        widget=forms.RadioSelect(
            attrs={
                'class': 'form-check-input'
            }
        )
    )

    def clean_content(self):
        content = self.cleaned_data['content']

        if content:
            words = content.split(' ')

            if len(words) < 2 or len(words) == len(list(filter(lambda x: len(x) == 1, words))):
                raise forms.ValidationError(
                    'Отзыв должен содержать развернутое мнение о товаре'
                )

        return content

class CustomerLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email адрес'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            customer = User.objects.filter(email=email).first()

            if not customer:
                raise forms.ValidationError('Покупатель с таким адресом email не зарегистрирован')

            else:
                username = customer.username

                user = authenticate(username=username, password=password)

                if not user:
                    raise forms.ValidationError('Неверный адрес email или пароль')

        return super().clean()


class CustomerRegisterForm(UserCreationForm):
    email = forms.CharField(
        label='Email адрес:',
        widget=forms.EmailInput(
            attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите ваш email'}
        )
    )
    password1 = forms.CharField(
        label='Пароль:',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg', 'placeholder': 'Придумайте пароль'}
        )
    )
    password2 = forms.CharField(
        label='Повторите пароль:',
        strip=False,
        widget= forms.PasswordInput(
            attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите пароль еще раз'}
        )
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user