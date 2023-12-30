import time
from os.path import exists
from better_proxy import Proxy
from arkana import *
from loguru import logger as log
from register_with_selenium import main_register_with_selenium
from imap_valid_checker import check_email

log.add("logger.log", format="{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}")

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

    log.success(f'Успішно завантажені {len(accounts_list)} аккаунти для реєстрації | {len(ref_code_list)} реферальні коди')
    log.success(
        f'Успішно завантажені {len(successfully_accounts_list)} успішно зареєстровані аккаунти | {len(proxies_list)} проксі')
    time.sleep(2)


    software_method = int(input('\n1. Реєстрація аккаунтів\n'
                                '2. Фармінг щоденних поінтів\n'
                                '3. Поревірити кількість валідних email\n'
                                '4. Порахувати загальну кількість поінтів з БД\n'
                                'Зроби свій вибір:\n'))
    print()

    if software_method == 1:
        for account in accounts_list:
            email_address, apps_password, imap = account.split(';')
            if is_account_registered(email_address):
                try:
                    main_register_with_selenium(email_address, apps_password, imap)
                    time.sleep(waiting_time_otp*3)
                    print()
                except:
                    time.sleep(waiting_time_otp * 3)
                    continue
            else:
                l.info(f"{email_address} | already regitered")
                l.info("go to the next email")
                time.sleep(1)
                print()
                continue
    elif software_method == 2:
        for account in accounts_list:
            email_adress, apps_password, imap = account.split(';')
            total_daily_claim(email_adress, apps_password, imap)
            time.sleep(time_break)
            print()

    elif software_method == 3:
        log.info("Починаю рахувати..")
        check_pass_success = 0
        total_count_email = len(accounts_list)

        for account in accounts_list:
            email_adress, apps_password, imap = account.split(';')

            if check_email(email_adress, apps_password):
                check_pass_success += 1

        log.success(f'Кількість аккаунтів яка пройшла перевірку | {check_pass_success}/{total_count_email}')
        print()

    elif software_method == 4:
        for account in accounts_list:
            log.error("Ще не інтегровано")

    else:
        log.error("Невідомий метод, оберіть 1, 2, 3 або 4!")

    time.sleep(time_break)
    print()
    log.success('Роботу успішно завершено')

    time.sleep(time_break)
    log.debug('Press Enter to exit...')
    input()


if __name__ == '__main__':
    main()
