from arkana import *

# Отримуємо ОТП з вказаної адреси
def get_otp_1(email_address, password, imap_server):
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


print(get_otp_1('jamarzpfred@outlook.com', 'Ii68illei', 'outlook.com'))