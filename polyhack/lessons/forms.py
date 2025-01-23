from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_content', 'pdf_content', 'has_simulation', 'simulation_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'simulation_url': forms.URLInput(attrs={'placeholder': 'https://phet.colorado.edu/sims/...'}),
        } 