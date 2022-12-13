## OpenStackBot
### Установка Docker
```bash
docker build -t osapibot:0.1.3 . 
vim .env # **OS_CREDS and TOKEN
docker run -d --name osapibot --env-file=.env osapibot:0.1.3
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
