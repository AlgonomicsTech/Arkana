# Введіть свій ключ антикаптча
import random

anticaptcha_api_key = ''

waiting_time_otp = 15
timeout = 30
time_break = random.randint(5, 10)

# Не змінювати
home_page = 'https://arkana.gg:443'
url_arkana = 'https://arkana.gg/?refcode='
url_arkana_signin = "https://api-v2.arkana.gg/v2/signin"
url_arkana_verify = 'https://api-v2.arkana.gg/v2/verify'
url_arkana_about_me = 'https://api-v2.arkana.gg/v2/me'
url_arkana_daily_claim = 'https://api-v2.arkana.gg/v2/daily-claim'
data_sitekey = "6LfqK1cjAAAAAJeHWgDadlurPp4_go9e-MrsetlN"

window_sizes = [
    (800, 600), (1024, 768), (1280, 720), (1280, 800),
    (1366, 768), (1440, 900), (1600, 900), (1680, 1050),
    (1920, 1080), (1920, 1200), (2560, 1440), (2560, 1600),
    (3200, 1800), (3840, 2160), (5120, 2880), (800, 1000),
    (900, 1200), (1000, 1400), (1100, 1600), (1200, 1800)
]