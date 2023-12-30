from multiprocessing.dummy import Pool
from sys import stderr

from imap_tools import MailBox
from imap_tools.errors import MailboxLoginError
from loguru import logger as log

log.add("logger.log", format="{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}")


def get_imap_host(email: str) -> str:
    # Визначення домену електронної пошти
    domain = email.split('@')[-1]

    # Словник з відповідностями доменів та IMAP-серверів
    imap_servers = {
        'gmail.com': 'imap.gmail.com',
        'rambler.ru': 'imap.rambler.ru',
        'ukr.net': 'imap.ukr.net',
        'outlook.com': 'imap-mail.outlook.com',
        # Додайте інші домени та відповідні IMAP-сервери за потреби
    }

    # Повернення IMAP-сервера для відповідного домену або стандартного значення
    return imap_servers.get(domain, 'default-imap-server.com')


def check_email(email: str, imap_password: str) -> bool:
    try:
        imap_host = get_imap_host(email)
        with MailBox(imap_host).login(email, imap_password):
            log.info(f'{email} | active')

            return True

    except MailboxLoginError as error:
        log.error(f'Login failed for {email} | {error}')
        return False

    except Exception as error:
        log.error(f'Unexpected error for {email} | {error}')
        return False




