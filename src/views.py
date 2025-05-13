import datetime
def hello():
    current_date_time = datetime.datetime.now()
    hour_now = current_date_time.hour
    if 0 <= hour_now <= 6:
        return "Доброй ночи"
    if 7 <= hour_now <= 11:
        return "Доброе утро"
    if 12 <= hour_now <= 17:
        return "Добрый день"
    if 18 <= hour_now <= 23:
        return "Добрый вечер"

