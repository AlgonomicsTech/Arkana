import time

import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
from arkana import *
from imap_valid_checker import check_email
from fake_useragent import UserAgent

def auto_reg(email_address, apps_password, imap):
    if check_email(email_address, apps_password):

        # Створення об'єкта UserAgent
        ua = UserAgent()

        # Вибір випадкових позицій
        random_user_agent = ua.random
        random_size = random.choice(window_sizes)
        PROXY = choose_random('proxy.txt')


        # Налаштування опцій WebDriver
        options = Options()
        options.add_argument(f'user-agent={random_user_agent}')
        options.add_argument(f'--proxy-server={PROXY}')

        options.headless = True  # Запуск браузера у фоновому режимі
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(*random_size)

        try:
            # Відкриття сайту
            driver.get(url_arkana + choose_random('ref.txt'))
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[2]/div/div[1]/div[1]/div[2]/button'))).click()
            time.sleep(time_break)

            email_input = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div/div/form/input'))
            )
            email_input.send_keys(email_address)
            l.info(f'{email_address} | send email')
            time.sleep(time_break)

            WebDriverWait(driver, timeout*10).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="__next"]/div[2]/div/div/form/button'))).click()
            time.sleep(waiting_time_otp)

            otp_input = WebDriverWait(driver, timeout*10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/div/div/form/div/input')))
            l.info(f"{email_address} | input email")
            otp = get_otp(email_address, apps_password, imap)
            otp_input.send_keys(otp)
            l.info(f'{email_address} | input OTP')
            time.sleep(time_break*2)

            WebDriverWait(driver, timeout*2).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="__next"]/div[2]/div/div/form/button'))).click()
            time.sleep(waiting_time_otp*2)

            year_input = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/div/div[5]/div/form/div/div[1]/div[1]/input')))
            year_input.send_keys(random.randint(1985,2007))
            l.info(f"{email_address} | input year of birth")
            time.sleep(time_break)

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="__next"]/div/div[2]/div/div[5]/div/form/div/div[2]/button'))).click()
            time.sleep(time_break)

            account_id = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/div/div[1]/div[2]/div[2]/div/p[2]'))).text

            save_data(email_address, account_id, 1000)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/div[2]/div[2]/div/button'))).click()

            # Очікування для забезпечення копіювання тексту
            driver.implicitly_wait(5)

            # Використання pyperclip для отримання тексту з буфера обміну
            copied_url = pyperclip.paste()
            refcode = re.split("[= ]", copied_url)[-1]

            with open('ref.txt', 'a') as file:
                file.write(refcode + '\n')

            l.info(f"{email_address} | save {refcode} in ref.txt")
            l.success(f"{email_address} | created successfully | {account_id}")


            time.sleep(time_break)
            print()

            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            #     (By.XPATH, '//*[@id="__next"]/div/div[1]/div/div[1]/div[2]/button/div/div/p'))).click()
            # time.sleep(time_break)
            #
            # WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #     (By.XPATH, '//*[@id="__next"]/div/div[1]/div/div[2]/div[2]/div/div[2]/div[6]'))).click()


            time.sleep(waiting_time_otp)
        except Exception as e:
            l.error(f'{email_address} | {str(e)}')
            l.info("go to the next email")
            return False
        finally:
            driver.quit()
    else:
        l.error(f'{email_address} | failed checking email')
        l.info("go to the next email")
