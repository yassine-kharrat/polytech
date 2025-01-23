from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'teacher':
            messages.error(request, "Only teachers can access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 