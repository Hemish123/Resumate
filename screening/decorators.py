from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def logout_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # If user is logged in, redirect to some other view (e.g., home page)
            return redirect('parsing-home')
        return view_func(request, *args, **kwargs)
    return wrapped_view