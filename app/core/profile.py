from django.contrib.auth import logout
from django.shortcuts import redirect

from apps.lk.models import Profile, Navbar


def get_profile(request) -> Profile:
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        logout(request)
        return redirect('/login')

    return profile


def get_navbar(user_id: int) -> list:
    rows = []

    profile = Profile.objects.get(user_id=user_id)

    # ToDo: Show pages by role

    for item in Navbar.objects.all():
        row = dict()
        row['link'] = item.link
        row['text'] = item.text
        row['app_name'] = item.app_name
        rows.append(row)

    return rows
