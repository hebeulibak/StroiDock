import sqlite3
from models import ConstructionSite, GeneralJournalEntry, NormativeDocument, NormDocType, PhotoWithLocation, Document

DB_PATH = "construction.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблица объектов
    c.execute('''CREATE TABLE IF NOT EXISTS sites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, address TEXT, customer TEXT, contractor TEXT, 
                  start_date TEXT, end_date TEXT)''')
    
    # Таблица журнала работ
    c.execute('''CREATE TABLE IF NOT EXISTS general_journal
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  site_id INTEGER, date TEXT, work_type TEXT, work_description TEXT,
                  location TEXT, executor TEXT, responsible_person TEXT, workers_count INTEGER, 
                  shift TEXT, start_time TEXT, end_time TEXT, volume REAL, volume_unit TEXT, 
                  equipment_used TEXT, materials_used TEXT, notes TEXT, weather TEXT, 
                  temperature REAL, photo_paths TEXT, created_at TEXT, updated_at TEXT)''')
    
    # Таблица нормативов
    c.execute('''CREATE TABLE IF NOT EXISTS normatives
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  doc_type TEXT, number TEXT, title TEXT, full_title TEXT,
                  status TEXT, actual_date TEXT, tags TEXT, content TEXT, 
                  replaced_by TEXT, is_favorite INTEGER)''')
    
    # Таблица фото
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  site_id INTEGER, photo_path TEXT, 
                  latitude REAL, longitude REAL, timestamp TEXT, 
                  description TEXT, document_section TEXT)''')
    
    # Таблица документов
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  site_id INTEGER, section TEXT, title TEXT, 
                  document_number TEXT, date TEXT, description TEXT, 
                  file_path TEXT, created_at TEXT)''')
    
    # Таблица базы знаний (подсказки)
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_base
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  title TEXT,
                  content TEXT,
                  steps TEXT,
                  materials TEXT,
                  safety TEXT,
                  image_path TEXT,
                  created_at TEXT)''')
    
    conn.commit()
    conn.close()

# ============ ОБЪЕКТЫ ============
def get_all_sites():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [ConstructionSite(**dict(row)) for row in rows]

def get_site_by_id(site_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE id = ?", (site_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return ConstructionSite(**dict(row))
    return None

def add_site(site):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO sites (name, address, customer, contractor, start_date, end_date)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (site.name, site.address, site.customer, site.contractor, 
                    site.start_date, site.end_date))
    conn.commit()
    conn.close()

def delete_site(site_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sites WHERE id = ?", (site_id,))
    cursor.execute("DELETE FROM general_journal WHERE site_id = ?", (site_id,))
    cursor.execute("DELETE FROM photos WHERE site_id = ?", (site_id,))
    cursor.execute("DELETE FROM documents WHERE site_id = ?", (site_id,))
    conn.commit()
    conn.close()

# ============ ЖУРНАЛ РАБОТ ============
def get_journal_entries(site_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM general_journal WHERE site_id = ? ORDER BY date DESC", (site_id,))
    rows = cursor.fetchall()
    conn.close()
    return [GeneralJournalEntry(**dict(row)) for row in rows]

def add_journal_entry(entry):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO general_journal 
        (site_id, date, work_type, work_description, location, executor, responsible_person, 
         workers_count, shift, start_time, end_time, volume, volume_unit, equipment_used, 
         materials_used, notes, weather, temperature, photo_paths, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (entry.site_id, entry.date, entry.work_type, entry.work_description, 
         entry.location, entry.executor, entry.responsible_person, entry.workers_count, 
         entry.shift, entry.start_time, entry.end_time, entry.volume, entry.volume_unit, 
         entry.equipment_used, entry.materials_used, entry.notes, entry.weather, 
         entry.temperature, entry.photo_paths, entry.created_at, entry.updated_at))
    conn.commit()
    conn.close()

def get_journal_entry_by_id(entry_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM general_journal WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return GeneralJournalEntry(**dict(row))
    return None

def update_journal_entry(entry):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''UPDATE general_journal SET 
        date=?, work_type=?, work_description=?, location=?, executor=?, 
        responsible_person=?, workers_count=?, shift=?, start_time=?, end_time=?,
        volume=?, volume_unit=?, equipment_used=?, materials_used=?, notes=?, 
        weather=?, temperature=?, updated_at=?
        WHERE id=?''',
        (entry.date, entry.work_type, entry.work_description, entry.location, 
         entry.executor, entry.responsible_person, entry.workers_count, entry.shift, 
         entry.start_time, entry.end_time, entry.volume, entry.volume_unit, 
         entry.equipment_used, entry.materials_used, entry.notes, entry.weather, 
         entry.temperature, entry.updated_at, entry.id))
    conn.commit()
    conn.close()

def delete_journal_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM general_journal WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_journal_summary(site_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM general_journal WHERE site_id = ?", (site_id,))
    total = cursor.fetchone()[0]
    cursor.execute('''SELECT date, COUNT(*) FROM general_journal 
                      WHERE site_id = ? AND date >= date('now', '-7 days') 
                      GROUP BY date ORDER BY date''', (site_id,))
    weekly = cursor.fetchall()
    conn.close()
    return {"total_entries": total, "weekly_stats": weekly}

# ============ ФОТО ============
def add_photo(photo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO photos (site_id, photo_path, latitude, longitude, timestamp, description, document_section)
                      VALUES (?,?,?,?,?,?,?)''',
                   (photo.site_id, photo.photo_path, photo.latitude, photo.longitude, 
                    photo.timestamp, photo.description, photo.document_section))
    conn.commit()
    conn.close()

def get_photos_by_site(site_id, section=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if section:
        cursor.execute("SELECT * FROM photos WHERE site_id = ? AND document_section = ? ORDER BY timestamp DESC", 
                       (site_id, section))
    else:
        cursor.execute("SELECT * FROM photos WHERE site_id = ? ORDER BY timestamp DESC", (site_id,))
    rows = cursor.fetchall()
    conn.close()
    return [PhotoWithLocation(**dict(row)) for row in rows]

def delete_photo(photo_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    conn.commit()
    conn.close()

# ============ ДОКУМЕНТЫ ============
def add_document(doc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO documents (site_id, section, title, document_number, date, description, file_path, created_at)
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (doc.site_id, doc.section, doc.title, doc.document_number, 
                    doc.date, doc.description, doc.file_path, doc.created_at))
    conn.commit()
    conn.close()

def get_documents_by_site(site_id, section=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if section:
        cursor.execute("SELECT * FROM documents WHERE site_id = ? AND section = ? ORDER BY date DESC", 
                       (site_id, section))
    else:
        cursor.execute("SELECT * FROM documents WHERE site_id = ? ORDER BY date DESC", (site_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Document(**dict(row)) for row in rows]

def delete_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

# ============ НОРМАТИВЫ ============
def get_all_normatives(doc_type=None, search=""):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM normatives"
    params = []
    conditions = []
    
    if doc_type and doc_type != "Все" and doc_type != "":
        conditions.append("doc_type = ?")
        params.append(doc_type)
    
    if search:
        conditions.append("(number LIKE ? OR title LIKE ? OR tags LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY is_favorite DESC, number"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        row_dict = dict(row)
        row_dict['doc_type'] = NormDocType(row_dict['doc_type'])
        result.append(NormativeDocument(**row_dict))
    return result

def get_normative_by_id(doc_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM normatives WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        row_dict = dict(row)
        row_dict['doc_type'] = NormDocType(row_dict['doc_type'])
        return NormativeDocument(**row_dict)
    return None

def toggle_favorite(doc_id, is_favorite):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE normatives SET is_favorite = ? WHERE id = ?", (1 if is_favorite else 0, doc_id))
    conn.commit()
    conn.close()

# ============ ПОИСК И ФИЛЬТРАЦИЯ В ЖУРНАЛЕ ============

def get_journal_entries_filtered(site_id, search='', date_from='', date_to='', work_type='', responsible=''):
    """Получить записи журнала с фильтрацией"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM general_journal WHERE site_id = ?"
    params = [site_id]
    
    # Поиск по тексту (ищем в описании, типе работ, месте, примечаниях)
    if search:
        query += " AND (work_description LIKE ? OR work_type LIKE ? OR location LIKE ? OR notes LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
    
    # Фильтр по дате начала
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    
    # Фильтр по дате окончания
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    
    # Фильтр по типу работ
    if work_type:
        query += " AND work_type = ?"
        params.append(work_type)
    
    # Фильтр по ответственному
    if responsible:
        query += " AND responsible_person = ?"
        params.append(responsible)
    
    query += " ORDER BY date DESC, id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [GeneralJournalEntry(**dict(row)) for row in rows]

def get_distinct_work_types(site_id):
    """Получить уникальные типы работ для объекта"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT work_type FROM general_journal WHERE site_id = ? AND work_type != '' ORDER BY work_type", (site_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_distinct_responsible(site_id):
    """Получить уникальных ответственных для объекта"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT responsible_person FROM general_journal WHERE site_id = ? AND responsible_person != '' ORDER BY responsible_person", (site_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]