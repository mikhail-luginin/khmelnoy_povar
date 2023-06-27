from apps.lk.models import Navbar


def get_navbar() -> list:
    rows = []

    # ToDo: Show pages by role

    for item in Navbar.objects.all():
        row = dict()
        row['link'] = item.link
        row['text'] = item.text
        row['app_name'] = item.app_name
        rows.append(row)

    return rows
