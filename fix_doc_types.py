import sqlite3

DB_PATH = "construction.db"

def fix_document_types():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Смотрим все уникальные типы документов в БД
    cursor.execute("SELECT DISTINCT doc_type FROM normatives")
    types = cursor.fetchall()
    
    print("=" * 50)
    print("Найденные типы документов в БД:")
    print("=" * 50)
    for t in types:
        print(f"  - '{t[0]}'")
    
    print("\n" + "=" * 50)
    print("Исправление типов...")
    print("=" * 50)
    
    # Обновляем типы
    cursor.execute("UPDATE normatives SET doc_type = 'СП' WHERE doc_type = 'Свод правил'")
    print(f"  Свод правил -> СП ({cursor.rowcount} записей)")
    
    cursor.execute("UPDATE normatives SET doc_type = 'СП' WHERE doc_type LIKE '%Свод%'")
    print(f"  Свод... -> СП ({cursor.rowcount} записей)")
    
    cursor.execute("UPDATE normatives SET doc_type = 'ГОСТ' WHERE doc_type = 'ГОСТ'")
    cursor.execute("UPDATE normatives SET doc_type = 'СНиП' WHERE doc_type = 'СНиП'")
    cursor.execute("UPDATE normatives SET doc_type = 'СанПиН' WHERE doc_type = 'СанПиН'")
    
    # Все остальные неизвестные типы заменяем на "Документ"
    cursor.execute("UPDATE normatives SET doc_type = 'Документ' WHERE doc_type NOT IN ('СП', 'ГОСТ', 'СНиП', 'СанПиН', 'Документ', 'Закон', 'Приказ')")
    print(f"  Неизвестные типы -> Документ ({cursor.rowcount} записей)")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Типы документов исправлены!")
    print("=" * 50)

def show_current_types():
    """Показать текущие типы после исправления"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT doc_type, COUNT(*) FROM normatives GROUP BY doc_type")
    rows = cursor.fetchall()
    conn.close()
    
    print("\n" + "=" * 50)
    print("Типы документов после исправления:")
    print("=" * 50)
    for row in rows:
        print(f"  - {row[0]}: {row[1]} документов")

if __name__ == "__main__":
    print("=" * 50)
    print("ИСПРАВЛЕНИЕ ТИПОВ ДОКУМЕНТОВ")
    print("=" * 50)
    
    # Проверяем, сколько документов в БД
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM normatives")
    total = cursor.fetchone()[0]
    conn.close()
    print(f"\n📊 Всего документов в БД: {total}")
    
    if total == 0:
        print("\n❌ В базе данных нет нормативов!")
        print("Сначала импортируйте нормативы через import_from_rnajson.py")
    else:
        # Исправляем
        fix_document_types()
        # Показываем результат
        show_current_types()
        
        print("\n✅ Готово! Перезапустите приложение: python app.py")
