import firebase_admin
from django.conf import settings
from firebase_admin import credentials


def firebase_conn():
    """Ensure Firebase is initialized only once and return the Firebase instance."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)

    return firebase_admin
