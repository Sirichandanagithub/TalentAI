import re

DEFAULT_COUNTRY_CODE = "+91"


def normalize_name(name):

    if not name:
        return None

    return " ".join(name.split()).title()


def normalize_email(email):

    if not email:
        return None

    return email.strip().lower()


def normalize_phone(phone):

    if not phone:
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        return DEFAULT_COUNTRY_CODE + digits

    if len(digits) == 12:
        return "+" + digits

    return phone


def normalize_location(location):

    if not location:
        return None

    location = " ".join(location.split())

    location = location.replace(" ,", ",")

    return location.strip()