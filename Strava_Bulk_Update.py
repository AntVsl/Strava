import time
import requests
from datetime import datetime, timezone

# === НАСТРОЙКИ: заполни своими данными ===
CLIENT_ID = "YOURCLIENTID"
CLIENT_SECRET = "YOURCLIENTSECRET"
REFRESH_TOKEN = "YUORREFRESH_TOKEN"

# dry-run: если True — только выводим, что бы обновили, без реальных PUT-запросов
DRY_RUN = True

# год и типы
YEAR = 2026
FROM_DATE = int(datetime(YEAR, 1, 1, tzinfo=timezone.utc).timestamp())
TO_DATE = int(datetime(YEAR + 1, 1, 1, tzinfo=timezone.utc).timestamp())

SOURCE_SPORT_TYPE = "Workout"
TARGET_SPORT_TYPE = "PhysicalTherapy"  # строка из списка Supported Sport Types

# === Служебные функции ===

def refresh_access_token():
    url = "https://www.strava.com/api/v3/oauth/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    token_info = resp.json()
    return token_info["access_token"]

def get_activities_2026(access_token):
    activities = []
    page = 1
    per_page = 50

    while True:
        url = "https://www.strava.com/api/v3/athlete/activities"
        params = {
            "page": page,
            "per_page": per_page,
            "after": FROM_DATE,
            "before": TO_DATE,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        page_data = resp.json()

        if not page_data:
            break

        activities.extend(page_data)
        page += 1
        time.sleep(0.2)  # небольшой sleep, чтобы не упираться в лимиты[web:23]

    return activities

def update_activity_sport_type(access_token, activity_id, new_sport_type):
    if DRY_RUN:
        print(f"[DRY RUN] Обновили бы активность {activity_id} → {new_sport_type}")
        return

    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "sport_type": new_sport_type
    }
    resp = requests.put(url, headers=headers, data=data)
    if resp.status_code != 200:
        print(f"Ошибка обновления {activity_id}: {resp.status_code}, {resp.text}")
    else:
        print(f"Обновлена активность {activity_id} → {new_sport_type}")

# === Основной код ===

def main():
    access_token = refresh_access_token()
    print("Access token обновлён")

    activities = get_activities_2026(access_token)
    print(f"Найдено активностей за {YEAR}: {len(activities)}")

    to_update = [
        a for a in activities
        if a.get("sport_type") == SOURCE_SPORT_TYPE
    ]
    print(f"Активностей с sport_type = {SOURCE_SPORT_TYPE}: {len(to_update)}")

    if DRY_RUN:
        print("Режим DRY_RUN включён: никаких изменений в Strava не будет выполнено.")

    for i, act in enumerate(to_update, start=1):
        act_id = act["id"]
        update_activity_sport_type(access_token, act_id, TARGET_SPORT_TYPE)

        # защита от rate limit Strava API[web:23]
        if not DRY_RUN:
            if i % 90 == 0:
                print("Пауза 15 минут из-за rate limit...")
                time.sleep(15 * 60)
            else:
                time.sleep(0.4)

if __name__ == "__main__":
    main()
