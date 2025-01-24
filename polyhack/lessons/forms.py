from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_content', 'pdf_content', 
                 'has_simulation', 'simulation_url', 
                 'has_3d_model', 'model_file', 'model_poster']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'simulation_url': forms.URLInput(attrs={'placeholder': 'https://phet.colorado.edu/sims/...'}),
            'has_3d_model': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'model_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.glb,.gltf'}),
            'model_poster': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        has_3d_model = cleaned_data.get('has_3d_model')
        model_file = cleaned_data.get('model_file')

        # Automatically set has_3d_model to True if a model file is uploaded
        if model_file and not has_3d_model:
            cleaned_data['has_3d_model'] = True
        
        # Require model file if has_3d_model is checked
        if has_3d_model and not model_file:
            self.add_error('model_file', 'Please upload a 3D model file when enabling 3D model feature.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set has_3d_model based on whether there's a model file
        if instance.model_file:
            instance.has_3d_model = True
        elif not instance.model_file:
            instance.has_3d_model = False
            
        if commit:
            instance.save()
        return instance 