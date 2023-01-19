from datetime import datetime as dt
import os

md = "markdown"

start_message = """Cloudate OpenStack

    ⌛️ | 🔄 - Обновить данные
    ⬅️ | ➡️ - Пролистать данные
    🖥 - Открыть удаленный доступ (noVnc)
    ⚙️ - Настройки экземпляра
    ▶️ - Запуск экземпляра
    ⏹ - Остановка экземпляра
    🔁 - Перезагрузка экземпляра
    🔂 - Жесткая перезагрузка экземпляра

    /access - Обновить доступы
    
    /servers - Список виртуальных машин
    /services - Список сервисов
    
    /settings - Настройки*
    
    Пожелания и фиксы: @rombintu"""

access_warn = "*Заполни текст и отправь обратно*\nВнимание: данные не защищены ⚠️\n_В разработке_ /cancel - Отменить"
access_info = """```OS_PROJECT_DOMAIN_NAME=Default
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_NAME=
OS_TENANT_NAME=
OS_USERNAME=
OS_PASSWORD=
OS_AUTH_URL=http://<IP_ADDR_MGT>:35357/v3
OS_INTERFACE=internal
OS_IDENTITY_API_VERSION=3
OS_REGION_NAME=RegionOne
OS_AUTH_PLUGIN=password```"""
access_cancel = "Отмена операции"
access_err = "❗️ Ожидается файл формата _.txt_"
access_updated = "Доступы обновлены. /help"

ERROR = "{}\n\nПопробуйте обновить доступы /access"

def get_last_update_format():
    return f"Последнее обновление: \n\t{dt.now().strftime('%d %B в %H:%M')}"

def get_default_creds_file():
    return open(os.path.join(os.getcwd(), "env-default.txt"), "rb")