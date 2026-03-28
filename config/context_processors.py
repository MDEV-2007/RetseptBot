from django.conf import settings


def telegram_bot(request):
    """TELEGRAM_BOT_URL ni barcha templateslarda mavjud qiladi."""
    username = getattr(settings, 'TELEGRAM_BOT_USERNAME', '')
    return {
        'TELEGRAM_BOT_URL': f'https://t.me/{username}' if username else '',
    }
