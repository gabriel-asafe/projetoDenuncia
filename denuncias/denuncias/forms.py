from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import FileExtensionValidator

from .models import Denuncia
from django.contrib.auth import get_user_model

User = get_user_model()

class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CadastroUsuarioForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
class DenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        exclude = [
                   ]
        
        widgets = {
            'data_ocorrencia': forms.DateInput(attrs={'type': 'date'}),
            'hora_ocorrencia': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
      
        self.fields['imagem'].validators.append(
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])
        )
        self.fields['video'].validators.append(
            FileExtensionValidator(['mp4', 'avi', 'mpeg', 'mov'])
        )
        
     
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
