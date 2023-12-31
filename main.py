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

    log.success(f'Downloaded successfully {len(accounts_list)} accounts for registration | {len(ref_code_list)} referral codes')
    log.success(
        f'Downloaded successfully {len(successfully_accounts_list)} successfully registered accounts | {len(proxies_list)} proxy')
    time.sleep(2)


    software_method = int(input('\n1. Реєстрація аккаунтів\n'
                                '2. Фармінг щоденних поінтів\n'
                                '3. Поревірити кількість валідних email\n'
                                '4. Порахувати загальну кількість поінтів\n'
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
        log.info("I start counting..")
        check_pass_success = 0
        total_count_email = len(accounts_list)

        for account in accounts_list:
            email_adress, apps_password, imap = account.split(';')

            if check_email(email_adress, apps_password):
                check_pass_success += 1

        log.success(f'The number of accounts that passed the check | {check_pass_success}/{total_count_email}')
        print()

    elif software_method == 4:

        ref_points = len(successfully_accounts_list) * 1000
        total_points = [int(account_successfully.split(';')[2]) for account_successfully in successfully_accounts_list]

        log.success(f"Approximate number of points already received | {ref_points + sum(total_points)}")

    else:
        log.error("Unknown method, choose 1, 2, 3 or 4!")

    time.sleep(time_break)
    print()
    log.success('Work completed successfully')

    time.sleep(time_break)
    log.debug('Press Enter to exit...')
    input()


if __name__ == '__main__':
    main()
