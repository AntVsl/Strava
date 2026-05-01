https://t.me/flowofthoughts/118

Как массово обновить тип тренировок в Strava 🥳

Если хочется сохранить историческую статистику без разрывов при смене девайса, типа тренировок или при ошибочном выборе активности на разных устройствах, это можно автоматизировать через API

Официальной кнопки для массового изменения нет, но Strava API позволяет делать это скриптом на Python с учетом лимитов: по умолчанию 200 запросов за 15 минут и 2000 запросов в день

Step-by-Step 😯

Детализирую только неочевидное

• Создаем API application для своего кода: Strava API settings. Заполняем поля: website — https://www.strava.testapp.com, authorization callback domain — localhost, остальное — произвольно
• Проверяем доступ к API на простом запросе к /api/v3/athlete с Bearer-токеном
postman request 'https://www.strava.com/api/v3/athlete' \
  --header 'Authorization: Bearer YOURACCESSTOKEN'
• Получаем временный OAuth-код через authorize endpoint со scope activity:read_all,activity:write
https://www.strava.com/oauth/authorize
  ?client_id=YOURCLIENTID
  &response_type=code
  &redirect_uri=http://localhost/exchange_token
  &approval_prompt=force
  &scope=activity:read_all,activity:write
• Обмениваем code на refresh_token и access_token через OAuth token exchange
postman request POST 'https://www.strava.com/oauth/token?client_id=YOURCLIENTID&client_secret=YOURCLIENTSECRET&code=AUTHORIZATIONCODE&grant_type=authorization_code' \
  --header 'Content-Type: application/json' \
  --body '{
  "name": "Add your name in the body"
}'

• Забираем скрипт GitHub. В коде задаем CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, SOURCE_SPORT_TYPE и TARGET_SPORT_TYPE, затем сначала запускаем в DRY RUN = True, чтобы посмотреть список найденных активностей, и только потом — в боевом режиме

Документация:
• Strava API reference
• Strava rate limits

Enjoy обновленной статистикой тренировок в Strava

#strava #script 
@flowofthoughts
