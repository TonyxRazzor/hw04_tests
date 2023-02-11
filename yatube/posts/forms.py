from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        label = {
            'text': ('Текст поста'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа чей пост'),
        }


def clean_text(self):
    data = self.cleaned_data['text']
    if len(data.lower()) == 0:
        raise forms.ValidationError('Это поле не может быть пустым')
    return data
