
#!/usr/bin/env python

"""Django's command-line utility for administrative tasks."""

import os
import sys

# 1) получаем директорию, где лежит manage.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


sys.path.insert(0, os.path.join(BASE_DIR, 'optimassfit', 'optimassfit'))

def main():
    # теперь DJANGO_SETTINGS_MODULE указывает просто на settings.py в этой подпапке
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optimassfit.setting")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что виртуальное окружение активно."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
