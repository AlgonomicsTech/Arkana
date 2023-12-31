import random
import time
from pyuseragents import random as random_useragent
from config import *
from anticaptchaofficial.recaptchav3proxyless import *
import imaplib
import email
import re
from datetime import datetime, timedelta
from loguru import logger as l
from curl_cffi import requests


session = requests.Session(impersonate="chrome110", timeout=60)
l.add("logger.log", format="{time:YYYY-MM-DD | HH:mm:ss.SSS} | {level} \t| {function}:{line} - {message}")
ref = None


# Обираємо випадковий реф код
def choose_random_code():
    with open('ref.txt', 'r') as file:
        codes = file.readlines()

    # Видалення символів нового рядка
    codes = [code.strip() for code in codes]

    # Повернення випадкового коду
    return random.choice(codes)


# Вирішуємо каптчу
def solve_recaptcha(count_try_solve=0):
    l.info('Captcha found - trying to solve..')

    solver = recaptchaV3Proxyless()
    solver.set_verbose(1)
    solver.set_key(anticaptcha_api_key)
    solver.set_website_url(url_arkana+ref)
    solver.set_website_key(data_sitekey)
    solver.set_page_action(home_page)
    solver.set_min_score(0.9)
    solver.set_soft_id(0)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        time.sleep(2)
        l.success(f"Captcha solved successfully!")
        print()
        return g_response
    else:
        l.error(f"Captcha resolution error | {solver.error_code}!")
        l.info("I am trying to solve the captcha again")
        count_try_solve += 1
        if count_try_solve < 5:
            # Повертайте результат рекурсивного виклику
            return solve_recaptcha(count_try_solve)
        else:
            l.error("All attempts to solve the captcha ended in error")
            return None


# Надсилаємо ОТП
def send_email(email_address, random_useragent):
    token_recaptcha = solve_recaptcha()
    if token_recaptcha is not None:
        payload = {
            'email': email_address,
            'recaptchaToken': token_recaptcha
        }

        headers = {
            'User-Agent': random_useragent,
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://arkana.gg/',
            'Connection': 'keep-alive',
            'DNT': '1',
        }

        try:
            r = session.post(url_arkana_signin, json=payload, headers=headers)
            l.info(f'{email_address} | send email for verification')
            return r.status_code
        except Exception as e:
            l.error(f'{email_address} | error when sending email | {str(e)}')
    else:
        l.error("captcha resolution error | not send email")


# Отримуємо ОТП з вказаної адреси
def get_otp(email_address, password, imap_server):

    try:
        # Підключення до поштового сервера
        mail = imaplib.IMAP4_SSL('imap.' + imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        for _ in range(15):
            status, messages = mail.search(None, '(FROM "auth@arkana.gg" SUBJECT "Verify Your Arkana Account")')
            messages = messages[0].split()

            if not messages:
                l.error(f"{email_address} | email with OTP code not found")
                time.sleep(waiting_time_otp)  # Затримка перед наступною спробою
                continue

            latest_mail_id = messages[-1]
            _, msg_data = mail.fetch(latest_mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode('utf-8')
                    verification_code_match = re.search(r"(?!([A-Z0-9])\1{5})[A-Z0-9]{6}", html_content)
                    verification_code = verification_code_match.group(0) if verification_code_match else None

                    if verification_code:
                        l.info(f"{email_address} | {verification_code}")
                        return verification_code
                    else:
                        l.error('OTP code not found')
                        time.sleep(time_break)

        # Якщо OTP код так і не знайдено
        raise ValueError("email with  OTP code not found after 10 attempts")

    except Exception as err:
        l.error(f"{email_address} | error get OPT | {err}")
    finally:
        mail.logout()

    return None


# Вводимо ОТП
def input_otp(otp, random_useragent):
    l.success(f'get OTP code | {otp}')

    if ref == False:
        data = {
            "code": otp,
        }

    # Headers
    headers = {
    'authority': 'api-v2.arkana.gg',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'uk,ru;q=0.9,ru-RU;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://arkana.gg',
    'referer': 'https://arkana.gg/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': random_useragent,
    }


    # Making the POST request
    response = session.post(url_arkana_verify, json=data, headers=headers)

    #print(response.json())
    # Checking the response
    if response.status_code == 200:
        response_data = response.json()
        l.info("input OTP code")
        auth_token = response_data['message']['token']
        acount_id = response_data['message']['account_id']
        return auth_token, acount_id
    else:
        l.error(f"Error when entering OTP | {response.status_code}")
        return False


# Зберігаємо дані
def save_data(mail, account_id, count_points=0):

    file_path = 'successfully_registered.txt'
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    data_line = f"{mail};{account_id};{count_points};{current_time}\n"

    with open(file_path, 'a') as file:
        file.write(data_line)
    l.info(f"{email} | data save in {file_path}")



# Перевірка чи адресу ще не зараєстровано
def is_account_registered(email_address):
    with open('successfully_registered.txt', 'r') as file:
        for line in file:
            if email_address in line.split(';')[0]:
                return False
    return True


# Перевірка часу на повторний клейм
def check_time_elapsed(email_address):
    with (open('successfully_registered.txt', 'r') as file):
        for line in file:
            parts = line.strip().split(';')
            if email_address == parts[0]:
                last_time_str = parts[3]
                last_time = datetime.strptime(last_time_str, "%d-%m-%Y %H:%M:%S")
                current_time = datetime.now()
                if current_time - last_time >= timedelta(days=1):
                    l.info("check for 24 hours | True")
                    return True
                else:
                    remaining_time = timedelta(days=1) - (current_time - last_time)
                    hours, remainder = divmod(remaining_time.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    l.info(f"{email_address} | try again {hours}:{minutes}:{seconds}")
                    return False

    l.error(f"{email_address} | not found")
    return False




# Забираємо щоденну винагороду
def daily_claim(random_useragent):
    # Заголовки для запиту
    headers = {
        'authority': 'api-v2.arkana.gg',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'uk,ru;q=0.9,ru-RU;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://arkana.gg',
        'referer': 'https://arkana.gg/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random_useragent,
    }

    # Виконуємо POST-запит
    response = requests.post(url_arkana_daily_claim, headers=headers)

    # Перевіряємо відповідь
    if response.status_code == 200:
        return response.json()
    else:
        return f"Failed with status code: {response.status_code}"


# Оновлюємо кількість отриманих поінтів і дату останнього клейму в файлі, після щоденнної претензії
def update_points_and_timestamp(email_address, points_to_add=500):
    updated_lines = []
    found = False

    with open('successfully_registered.txt', 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:  # Перевіряємо, чи рядок не є пустим
                if email_address in stripped_line:
                    parts = stripped_line.split(';')
                    if len(parts) >= 3:
                        parts[2] = str(int(parts[2]) + points_to_add)  # Оновлення поінтів
                        parts[3] = time.strftime("%d-%m-%Y %H:%M:%S")  # Оновлення часу та дати
                        line = ';'.join(parts)
                        found = True
                updated_lines.append(line)

    if found:
        with open('successfully_registered.txt', 'w') as file:
            for line in updated_lines:
                file.write(line+ '\n')
    return found


# Щоденний клейм
def total_daily_claim(email_address, password, imap, random_useragent=random_useragent()):
    if check_time_elapsed(email_address):
        send_email(email_address, random_useragent)
        time.sleep(waiting_time_otp)
        otp = get_otp(email_address, password, imap)
        auth_token, account_id = input_otp(otp, random_useragent)
        if auth_token is not None:
            daily_claim(random_useragent)
            l.success(f"{email_address} | daily points received successfully")

            if update_points_and_timestamp(email_address):
                l.info(f"{email_address} | data update")
            else:
                l.error(f"{email_address} | not found")
        else:
            l.error("unknown error | go to the next email")
    else:
        l.info("go to the next email")

