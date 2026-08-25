import re


def validate_name(name):

    if not name:
        return None

    if len(name) < 3:
        return None

    if re.search(r"\d", name):
        return None

    return name


def validate_email(email):

    if not email:
        return None

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email):
        return email

    return None


def validate_phone(phone):

    if not phone:
        return None

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        return phone

    if len(digits) == 12 and digits.startswith("91"):
        return phone

    return None


def validate_url(url):

    if not url:
        return None

    pattern = r"^(https?://)?(www\.)?.+"

    if re.match(pattern, url):
        return url

    return None