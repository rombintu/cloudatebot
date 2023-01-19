## OpenStackBot
### Установка Docker
```bash
docker build -t osapibot:latest . 
vim .env # **OS_CREDS and TOKEN
docker run -d --name osapibot --env-file=.env -v $PWD/store:/opt/store osapibot:latest
```

### Установка Linux
Python3 >= 3.8
```bash
python3 -m venv venv
source ./venv/bin/activate
pip install -r deps.txt
vim .env # **OS_CREDS and TOKEN
# PRERUN
python3 main.py

# TODO
sudo cp ./system/cloudatebot.service /etc/systemd/system/cloudatebot.service
sudo systemctl daemon-reload
sudo systemctl enable --now cloudatebot.service
```

### Примеры
    Команда /start 

![img](./screenshots/c_start.png)

    Команда /services - мониторинг всех сервисов 

![img](./screenshots/c_services.png)

    Команда /servers - выбор серверов, пролистывание\обновление через колбек 

![img](./screenshots/c_servers_1.png)
![img](./screenshots/c_servers_2.png)

    Колбек на определенный сервер 

![img](./screenshots/c_server_1.png)