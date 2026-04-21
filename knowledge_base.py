# knowledge_base.py
import sqlite3
from datetime import datetime

DB_PATH = "construction.db"

# Предустановленные подсказки для строителя
DEFAULT_TIPS = [
    {
        "category": "Фундаментные работы",
        "title": "Как правильно залить ленточный фундамент",
        "content": "Ленточный фундамент заливается при температуре не ниже +5°C. Бетон должен быть марки не ниже М300.",
        "steps": "1. Разметка участка\n2. Рытьё траншеи\n3. Установка опалубки\n4. Армирование\n5. Заливка бетона\n6. Уход за бетоном",
        "materials": "Цемент М400, песок, щебень, арматура d12, доска для опалубки",
        "safety": "Использовать перчатки, защитные очки. Не работать в одиночку."
    },
    {
        "category": "Кровельные работы",
        "title": "Монтаж металлочерепицы",
        "content": "Листы поднимаются на крышу по 2-3 штуки. Нахлёст должен быть не менее 10 см.",
        "steps": "1. Устройство стропильной системы\n2. Установка обрешётки\n3. Пароизоляция\n4. Укладка металлочерепицы\n5. Монтаж конька и торцевых планок",
        "materials": "Металлочерепица, саморезы с резиновой шайбой, гидроизоляция",
        "safety": "Работать со страховочным тросом. В обуви с мягкой подошвой."
    },
    {
        "category": "Электромонтажные работы",
        "title": "Установка розетки",
        "content": "Цветовая маркировка: коричневый/чёрный - фаза, синий - ноль, жёлто-зелёный - земля.",
        "steps": "1. Отключить электричество\n2. Зачистить провода\n3. Подключить к клеммам (фаза-ноль-земля)\n4. Закрепить в подрозетнике\n5. Установить крышку",
        "materials": "Розетка, индикаторная отвёртка, изолента",
        "safety": "ОБЯЗАТЕЛЬНО отключить автомат! Проверить отсутствие напряжения индикатором."
    },
    {
        "category": "Штукатурные работы",
        "title": "Штукатурка стен по маякам",
        "content": "Толщина слоя штукатурки не более 20-30 мм за один проход.",
        "steps": "1. Грунтовка стен\n2. Установка маячков\n3. Нанесение раствора\n4. Выравнивание правилом\n5. Затирка",
        "materials": "Штукатурная смесь, маячки 6 мм, правило, грунтовка",
        "safety": "Использовать перчатки, респиратор при замешивании."
    },
    {
        "category": "Сантехнические работы",
        "title": "Монтаж унитаза",
        "content": "Расстояние от стены до унитаза должно быть не менее 30 см.",
        "steps": "1. Установка гофры\n2. Разметка креплений\n3. Сверление отверстий\n4. Установка унитаза\n5. Подключение воды\n6. Герметизация стыка",
        "materials": "Унитаз, гофра, силиконовый герметик, дюбели",
        "safety": "Проверить отсутствие протечек после подключения."
    },
    {
        "category": "Бетонные работы",
        "title": "Правильное армирование фундамента",
        "content": "Защитный слой бетона должен быть 50-70 мм. Арматура не должна касаться опалубки.",
        "steps": "1. Подготовка арматуры\n2. Вязка сетки\n3. Установка фиксаторов\n4. Монтаж в опалубку\n5. Проверка защитного слоя",
        "materials": "Арматура d12-d16, вязальная проволока, крючок для вязки",
        "safety": "Работать в перчатках. Не ходить по арматуре."
    }
]

def init_knowledge_base():
    """Инициализация базы знаний начальными данными"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем, пустая ли таблица
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    count = cursor.fetchone()[0]
    
    if count == 0:
        for tip in DEFAULT_TIPS:
            cursor.execute('''INSERT INTO knowledge_base 
                (category, title, content, steps, materials, safety, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (tip['category'], tip['title'], tip['content'], 
                 tip['steps'], tip['materials'], tip['safety'],
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

def get_all_tips(category=None, search=None):
    """Получить все подсказки с фильтрацией"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM knowledge_base"
    params = []
    conditions = []
    
    if category and category != "Все" and category != "":
        conditions.append("category = ?")
        params.append(category)
    
    if search:
        conditions.append("(title LIKE ? OR content LIKE ? OR steps LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY id"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_tip_by_id(tip_id):
    """Получить одну подсказку по ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_base WHERE id = ?", (tip_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_tip(category, title, content, steps, materials, safety):
    """Добавить новую подсказку"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO knowledge_base 
        (category, title, content, steps, materials, safety, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (category, title, content, steps, materials, safety,
         datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def get_categories():
    """Получить все категории"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM knowledge_base")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]