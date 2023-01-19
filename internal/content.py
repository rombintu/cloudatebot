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
    /admin - Запросить права * deprecated
    
    /servers - Список виртуальных машин
    /services - Список сервисов
    
    /settings - Настройки *"""

access_warn = "*Заполни файл и отправь обратно*\nВнимание: данные не защищены ⚠️\n_В разработке_"
access_err = "❗️ Ожидается файл формата _.txt_"
access_updated = "Доступы обновлены. /help"

def get_last_update_format():
    return f"Последнее обновление: \n\t{dt.now().strftime('%d %B в %H:%M')}"

def get_default_creds_file():
    return open(os.path.join(os.getcwd(), "env-default.txt"), "rb")