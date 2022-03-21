from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Токен бота
ADMINS = env.list("ADMINS")  # Список администраторов
VK_LINK = "https://vk.com/emma_sport_analytics_bot"
SPORTS = {"football" : "⚽Футбол⚽",# Список доступных видов спорта
          "hockey" : "🏒Хоккей",
          "basketball" : "🏀Баскетбол🏀"}
DATE_F = r"%Y-%m-%d"
HEADERS = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"}
MC_URL = "https://www.championat.com/stat/{date}.json"
BASE_URL = "https://www.championat.com"
FORECAST_RATE = {'Удары по воротам' : 1,
                 'Удары в створ' : 1,
                 'Штрафные удары' : 1,
                 'Предупреждения' : 1,
                 'Удаления' : 1,
                 'win' : 1}