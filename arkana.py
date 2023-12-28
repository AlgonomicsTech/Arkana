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

    global ref
    ref = choose_random_code()
    l.info('Знайдена каптча - намагаюсь вирішити!')
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
        l.success(f"Каптча вирішено успішно!")
        print()
        return g_response
    else:
        l.error(f"Помилка вирішення каптчі: {solver.error_code}!")
        l.info("Намагаюсь вирішити каптчу повторно")
        count_try_solve += 1
        if count_try_solve < 5:
            # Повертайте результат рекурсивного виклику
            return solve_recaptcha(count_try_solve)
        else:
            l.error("Всі спроби вирішення капчі завершились помилкою")
            return None


# Надсилаємо ОТП
def send_email(email_address):
    token_recaptcha = solve_recaptcha()
    if token_recaptcha is not None:
        payload = {
            'email': email_address,
            'recaptchaToken': token_recaptcha
        }

        headers = {
            'User-Agent': random_useragent(),
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://arkana.gg/',
            'Connection': 'keep-alive',
            'DNT': '1',

        }

        try:
            r = requests.post(url_arkana_signin, json=payload, headers=headers)
            l.info(f'Надсилаю лист для верифіції на {email_address}')
            return r.status_code
        except Exception as e:
            l.error(f'Помилка при надсиланні листа: {str(e)}')
    else:
        l.error("Помилка вирішення каптчі. Не відправлено емейл.")


# Отримуємо ОТП з вказаної адреси
def get_otp(email_address, password, imap_server):
    try:
        # Підключення до поштового сервера
        mail = imaplib.IMAP4_SSL('imap.' + imap_server)

        # Вхід до поштового ящика
        mail.login(email_address, password)

        # Вибір поштової папки
        mail.select("inbox")

        # Пошук останніх або конкретних листів
        status, messages = mail.search(None, '(FROM "auth@arkana.gg" SUBJECT "Verify Your Arkana Account")')
        messages = messages[0].split()

        if not messages:
            l.error("Лист не знайдено в поштовій скринці")
            raise ValueError("Немає листів відповідно до фільтру")

        # Вибір останнього листа
        latest_mail_id = messages[-1]

        # Отримання вмісту останнього листа
        _, msg_data = mail.fetch(latest_mail_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode('utf-8')

                # Використання більш специфічного регулярного виразу
                verification_code_match = re.search(r"(?!([A-Z0-9])\1{5})[A-Z0-9]{6}", html_content)
                verification_code = verification_code_match.group(0) if verification_code_match else None

                if verification_code:
                    return verification_code
                else:
                    l.error('OTP код не знайдено')
                    raise ValueError("OTP код не знайдено")

    except Exception as err:
        l.error(f"Помилка отримання ОТП з {email_address}: {err}")
    finally:
        mail.logout()

    return None

# Вводимо ОТП
def input_otp(otp):
    l.success(f'Код ОТП отримано успішно: {otp}')
    data = {
        "code": otp
    }


    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://arkana.gg',
        'Referer': 'https://arkana.gg/'
    }

    # Making the POST request
    response = requests.post(url_arkana_verify, json=data, headers=headers)
    print(response.json())
    # Checking the response
    if response.status_code == 200:
        response_data = response.json()
        l.info("Вводимо код авторизації")
        auth_token = response_data['message']['token']
        acount_id = response_data['message']['account_id']
        return auth_token, acount_id
    else:
        l.error(f"Помилка при вводі ОТП: {response.status_code}")
        return False


# Вказуємо свій вік
def send_about_me(auth_token):

    data = {
        "display_name": "",
        "twitter": "",
        "instagram": "",
        "birthday": random.randint(1985,2007)
    }

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://arkana.gg',
        'Referer': 'https://arkana.gg/',
        'Authorization': auth_token
    }

    response = requests.put(url_arkana_about_me, json=data, headers=headers)

    # Checking the response
    if response.status_code == 200:
        l.success(f"Інформація про користувача заповнена успішно {response.json()}")
        return True
    else:
        l.info(response.json())
        l.error(f"Помилка при заповненні інформації про користувача: {response.status_code}")
        return False

# Зберігаємо дані
def save_data(mail, account_id, count_points=0):

    file_path = 'successfully_registered.txt'
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    data_line = f"{mail};{account_id};{count_points};{current_time}\n"

    with open(file_path, 'a') as file:
        file.write(data_line)
    l.info(f"Дані {file_path} успішно збережені")
    print()


# Перевірка чи адресу ще не зараєстровано
def is_account_registered(email_address):
    with open('successfully_registered.txt', 'r') as file:
        for line in file:
            if email_address in line.split(';')[0]:
                return False
    return True


# Створуємо аккаунти
def make_arkana_acounts(email, password, imap, count_try_create=0):
    if is_account_registered(email):
        send_email(email)
        time.sleep(15)
        otp = get_otp(email, password, imap)
        auth_token, account_id = input_otp(otp)
        if account_id is not None:
            send_about_me(auth_token)

            l.success(f"Аккаунт успішно створено: {account_id}:{email}")
            save_data(email, account_id, 1000)
        else:
            l.error(f"Попилка при створенні нового аккаунту з {email}")
            l.info("Намагаюсь створити аккаунт повторно")
            count_try_create += 1
            if count_try_create < 3:
                return make_arkana_acounts(email, password, imap, count_try_create)
            else:
                l.error(f"Всі спроби зареєструвати {email} завершились помилкою")
                l.info("Переходжу до наступної адреси")
                return False
    else:
        l.info(f"Акаунт {email} вже зареєстровано.")
        l.info("Переходжу до наступної адреси")


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
                    l.info("З минулого клейму пройшло більше 24 годин")
                    return True
                else:
                    remaining_time = timedelta(days=1) - (current_time - last_time)
                    hours, remainder = divmod(remaining_time.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    l.info(f"{email_address}|Залишилось часу до наступного клейму|{hours}:{minutes}:{seconds}")
                    return False

    l.error(f"Email {email_address} не знайдено.")
    return False




# Забираємо щоденну винагороду
def daily_claim(auth_token):
    # Заголовки для запиту
    headers = {
        'Authorization': auth_token,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': random_useragent(),
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://arkana.gg/',
        'Connection': 'keep-alive',
        'DNT': '1',
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
                file.write(line + '\n')
    return found


# Щоденний клейм
def total_daily_claim(email_address, password, imap):
    if check_time_elapsed(email_address):
        send_email(email_address)
        time.sleep(60)
        otp = get_otp(email_address, password, imap)
        auth_token, account_id = input_otp(otp)
        if auth_token is not None:
            daily_claim(auth_token)
            l.success(f"Щоденні поінти {email_address} отримано успішно!")

            if update_points_and_timestamp(email_address):
                l.info(f"Дані {email_address} оновлено")
            else:
                l.error(f"Email {email_address} не знайдено у файлі.")
        else:
            l.error("Щось пішло не так, переходимо на наступної адреси")
    else:
        l.info("Переходимо на наступної адреси")