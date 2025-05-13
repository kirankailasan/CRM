from django.http import HttpResponseForbidden

def verified_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if request.user.adminprofile.is_verified:
                    return view_func(request, *args, **kwargs)
            except:
                pass
        return HttpResponseForbidden("You are not authorized to access this page.")
    return wrapper
