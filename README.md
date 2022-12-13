## OpenStackBot

### Установка (Linux)
```bash
sudo git clone https://github.com/rombintu/openstack-bot.git /opt/cloudatebot
sudo chown $USER:$USER -R /opt/cloudatebot
cd /opt/cloudatebot
python3 -m venv venv
source ./venv/bin/activate
pip install -r deps.txt

sudo cp ./system/cloudatebot.service /etc/systemd/system/cloudatebot.service
sudo systemctl daemon-reload
sudo systemctl enable --now cloudatebot.service
```
