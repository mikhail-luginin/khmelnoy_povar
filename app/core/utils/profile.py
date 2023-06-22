from django.contrib.auth import logout
from django.shortcuts import redirect

from apps.lk.models import Profile


def profile_by_request(request) -> Profile:
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile:
        logout(request)
        return redirect('/login')

    return profile
