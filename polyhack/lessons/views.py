from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Lesson
from .forms import LessonForm
from classes.models import Class
from classes.decorators import teacher_required
from django.http import JsonResponse
from .video_summarizer import generate_video_summary
import os

# Update NGROK_URL to match current tunnel
NGROK_URL = 'https://b43e-41-230-221-34.ngrok-free.app'

@login_required
@teacher_required
def create_lesson(request, class_pk):
    class_obj = get_object_or_404(Class, pk=class_pk, teacher__user=request.user)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.class_instance = class_obj
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' has been created successfully!")
            return redirect('classes:class_detail', pk=class_pk)
    else:
        form = LessonForm()
    
    return render(request, 'lessons/create_lesson.html', {
        'form': form,
        'class': class_obj
    })

@login_required
def lesson_detail(request, pk):
    try:
        if request.user.is_teacher:
            lesson = get_object_or_404(Lesson, 
                pk=pk, 
                class_instance__teacher__user=request.user
            )
        else:
            lesson = get_object_or_404(Lesson, 
                pk=pk, 
                class_instance__enrolled_students=request.user.student_profile
            )
            
        context = {
            'lesson': lesson,
            'is_teacher': request.user.is_teacher,
            'ngrok_url': NGROK_URL,
            'debug_info': {
                'ngrok_url': NGROK_URL,
                'request_path': request.path,
                'full_url': f"{NGROK_URL}{request.path}",
            }
        }
        return render(request, 'lessons/lesson_detail.html', context)
    except Exception as e:
        print(f"Error in lesson_detail: {str(e)}")
        messages.error(request, "Error loading lesson")
        return redirect('classes:list_classes')

@login_required
@teacher_required
def generate_summary(request, pk):
    try:
        lesson = get_object_or_404(Lesson, pk=pk, class_instance__teacher__user=request.user)
        
        if not lesson.video_content:
            return JsonResponse({'error': 'No video content available'}, status=400)

        # Debug prints
        print("Debug Info:")
        print(f"Lesson ID: {lesson.pk}")
        print(f"Video name: {lesson.video_content.name}")
        print(f"Video URL: {lesson.video_content.url}")
        print(f"Video path: {lesson.video_content.path}")
        print(f"File exists: {os.path.exists(lesson.video_content.path)}")
        print(f"Media Root: {settings.MEDIA_ROOT}")

        # Get the absolute file path from the FileField
        video_path = lesson.video_content.path
        
        # Generate summary using the video_summarizer
        summary = generate_video_summary(video_path)
        
        if summary:
            # Save the summary to the lesson
            lesson.video_summary = summary
            lesson.save()
            return JsonResponse({'summary': summary})
        
        return JsonResponse({'error': 'Failed to generate summary'}, status=500)
        
    except Exception as e:
        print(f"Error in generate_summary view: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full traceback
        return JsonResponse({'error': str(e)}, status=500) 