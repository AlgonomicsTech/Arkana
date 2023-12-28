import time
from os.path import exists
from better_proxy import Proxy
from arkana import *
from loguru import logger as lo

l.add("logger.log", format="{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}")

def main():
    if exists(path='proxy.txt'):
        proxies_list = [proxy.as_url for proxy in Proxy.from_file(filepath='proxy.txt')]
    else:
        proxies_list = []

    if exists(path='email_data.txt'):
        with open(file='email_data.txt', mode='r', encoding='utf-8-sig') as file:
            accounts_list = [row.strip() for row in file]
    else:
        accounts_list = []

    if exists(path='successfully_registered.txt'):
        with open(file='successfully_registered.txt', mode='r', encoding='utf-8-sig') as file:
            successfully_accounts_list = [row.strip() for row in file]
    else:
        successfully_accounts_list = []

    if exists(path='ref.txt'):
        with open(file='ref.txt', mode='r', encoding='utf-8-sig') as file:
            ref_code_list = [row.strip() for row in file]
    else:
        ref_code_list = []

    lo.success(f'Успішно завантажені {len(accounts_list)} аккаунти для реєстрації | {len(ref_code_list)} реферальні коди')
    lo.success(
        f'Успішно завантажені {len(successfully_accounts_list)} успішно зареєстровані аккаунти | {len(proxies_list)} проксі')
    time.sleep(2)


    software_method = int(input('\n1. Реєстрація аккаунтів\n'
                                '2. Фармінг щоденних поінтів\n'
                                'Зроби свій вибір:\n'))
    print()

    if software_method == 1:
        for account in accounts_list:
            email_adress, apps_password, imap = account.split(';')
            make_arkana_acounts(email_adress, apps_password, imap)
            time.sleep(3)
            print()
    elif software_method == 2:
        for account in accounts_list:
            email_adress, apps_password, imap = account.split(';')
            total_daily_claim(email_adress, apps_password, imap)
            time.sleep(31)
            print()
    else:
        lo.error("Невідомий метод, оберіть 1 або 2!")

    time.sleep(5)
    print()
    lo.success('Роботу успішно завершено')

    time.sleep(5)
    input('\nPress Enter to Exit..')


if __name__ == '__main__':
    main()
