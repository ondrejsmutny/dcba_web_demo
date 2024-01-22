from django import forms
from .models import User, GeneralData
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields["password1"].label = "Heslo"
        self.fields["password1"].help_text = "*Vaše heslo musí mít alespoň 8 znaků, nesmí být podobné osobním údajům," \
                                             " běžným heslům a nesmí být pouze číselné."
        self.fields["password2"].label = "Heslo znovu"
        self.fields["password2"].help_text = "*Napište stejné heslo jako výše, pro ověření."

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginUserForm(AuthenticationForm):

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields["password"].label = "Heslo"

class SetPasswordUserForm(SetPasswordForm):

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SetPasswordUserForm, self).__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nové heslo"
        self.fields["new_password1"].help_text = "*Vaše heslo musí mít alespoň 8 znaků, nesmí být podobné osobním" \
                                                 " údajům, běžným heslům a nesmí být pouze číselné."
        self.fields["new_password2"].label = "Nové heslo znovu"
        self.fields["new_password2"].help_text = "*Napište stejné heslo jako výše, pro ověření."


class UserForm(forms.ModelForm):
    '''
    Old user creation form.
    '''
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["email", "password"]

class LoginForm(forms.Form):
    '''
    Old user login form.
    '''
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        fields = ["email", "password"]

class GeneralDataForm(forms.ModelForm):

    class Meta:
        model = GeneralData
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(GeneralDataForm, self).__init__(*args, **kwargs)

        # Unsetting required fields
        self.fields["name"].required = False
        self.fields["surname"].required = False
        self.fields["telephone_number"].required = False
        self.fields["company_name"].required = False
        self.fields["register_id"].required = False
        self.fields["vat_id"].required = False
        self.fields["street"].required = False
        self.fields["building_number"].required = False
        self.fields["zip_code"].required = False
        self.fields["city"].required = False
        self.fields["country"].required = False
