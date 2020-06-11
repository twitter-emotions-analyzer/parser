# Установка
Для установки парсера выполните следующие действия:
Загрузить файлы репозитория. Установить необходимые зависимости для библиотеки GetOldTweets. 
```
cd GetOldTweets-python-master
pip install -r requirements.txt
```
Установка Selenium
```
pip install selenium
```
Скачать webdriver, соответствующий вашей операционной системе и браузеру. Для тестирования использовался Chrome 83 на Ubuntu. Указать путь к директории с драйвером в PATH.
Установка остальных зависимостей:
```
pip install pika
pip install psycopg2
pip install flask
pip install flask_cors
```

# Запуск
Запуск веб интерфейса: 
```
cd static
sudo python -m SimpleHTTPServer [port]
```

Запуск сервера парсера
```
python run.py
```
