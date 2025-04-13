import requests
from bs4 import BeautifulSoup
import telebot
import time
import os
import threading

TOKEN = "8098227772:AAFVn8Zno7oIt38KLwfFdlCQbAakTL6OpqY"
bot = telebot.TeleBot(TOKEN)

URL = "https://lisansustu.beykent.edu.tr/duyurular"
GECMIS_DOSYA = "beykent_duyurular.txt"
KULLANICI_DOSYA = "users.txt"

def kullanicilari_oku():
    if not os.path.exists(KULLANICI_DOSYA):
        return set()
    with open(KULLANICI_DOSYA, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

@bot.message_handler(func=lambda message: True)
def kullanici_ekle(message):
    user_id = str(message.chat.id)
    mevcutlar = kullanicilari_oku()
    if user_id not in mevcutlar:
        with open(KULLANICI_DOSYA, "a", encoding="utf-8") as f:
            f.write(user_id + "\n")
        bot.send_message(user_id, "✅ Beykent duyuru botuna kaydoldun!")
    else:
        bot.send_message(user_id, "📢 Zaten kayıtlısın, yeni duyuruları sana ileteceğim.")

def okunan_duyurular():
    if not os.path.exists(GECMIS_DOSYA):
        return set()
    with open(GECMIS_DOSYA, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def yeni_duyurulari_kontrol_et():
    print("📡 Beykent duyuruları kontrol ediliyor...")
    try:
        r = requests.get(URL, verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        duyurular = soup.select(".haberItem")

        oncekiler = okunan_duyurular()
        yeniler = []

        for duyuru in duyurular:
            try:
                baslik = duyuru.find("a").text.strip()
                link = "https://lisansustu.beykent.edu.tr" + duyuru.find("a")["href"]
                if link not in oncekiler:
                    mesaj = f"🎓 Yeni Duyuru:\n{baslik}\n{link}"
                    for uid in kullanicilari_oku():
                        bot.send_message(uid, mesaj)
                    yeniler.append(link)
            except:
                continue

        if yeniler:
            with open(GECMIS_DOSYA, "a", encoding="utf-8") as f:
                for l in yeniler:
                    f.write(l + "\n")
    except Exception as e:
        print(f"Hata: {e}")

for uid in kullanicilari_oku():
    bot.send_message(uid, "🎓 Beykent duyuru botu yeniden başlatıldı!")

def dongu():
    while True:
        yeni_duyurulari_kontrol_et()
        time.sleep(300)

threading.Thread(target=dongu).start()
bot.polling()
