from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from datetime import datetime
import json
import sqlite3
import os
import base64
from werkzeug.utils import secure_filename

from database import init_db, get_all_sites, add_site, delete_site, get_site_by_id
from database import get_journal_entries, add_journal_entry, delete_journal_entry, get_journal_entry_by_id, update_journal_entry, get_journal_summary
from database import get_all_normatives, get_normative_by_id, toggle_favorite
from database import add_photo, get_photos_by_site, delete_photo
from database import add_document, get_documents_by_site, delete_document
from normatives import init_normatives
from models import ConstructionSite, GeneralJournalEntry, PhotoWithLocation, Document
from work_types_db import WORK_CATEGORIES

app = Flask(__name__)

# Папка для сохранения фото
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()
init_normatives()

# ============ ГЛАВНАЯ ============
@app.route('/')
def index():
    sites = get_all_sites()
    return render_template('index.html', sites=sites)

@app.route('/site/<int:site_id>')
def site_detail(site_id):
    site = get_site_by_id(site_id)
    if not site:
        return redirect(url_for('index'))
    return render_template('site_detail.html', site=site)

# ============ РАБОТА С ОБЪЕКТАМИ ============
@app.route('/site/add', methods=['POST'])
def add_site_route():
    site = ConstructionSite(
        id=0,
        name=request.form['name'],
        address=request.form.get('address', ''),
        customer=request.form.get('customer', ''),
        contractor=request.form.get('contractor', ''),
        start_date=request.form.get('start_date', datetime.now().strftime('%Y-%m-%d')),
        end_date=request.form.get('end_date', '')
    )
    add_site(site)
    return redirect(url_for('index'))

@app.route('/site/delete/<int:site_id>')
def delete_site_route(site_id):
    delete_site(site_id)
    return redirect(url_for('index'))

# ============ ЖУРНАЛ ОБЩИХ РАБОТ ============
@app.route('/journal/<int:site_id>')
def journal(site_id):
    site = get_site_by_id(site_id)
    entries = get_journal_entries(site_id)
    stats = get_journal_summary(site_id)
    stats['weekly_count'] = len(stats.get('weekly_stats', []))
    return render_template('journal.html', site=site, entries=entries, stats=stats, work_categories=WORK_CATEGORIES)

@app.route('/journal/add', methods=['POST'])
def add_journal_entry_route():
    data = request.form
    entry = GeneralJournalEntry(
        id=0, site_id=int(data['site_id']), date=data['date'], work_type=data['work_type'],
        work_description=data['work_description'], location=data.get('location', ''),
        executor=data.get('executor', ''), responsible_person=data.get('responsible_person', ''),
        workers_count=int(data.get('workers_count', 0)), shift=data.get('shift', '1'),
        start_time=data.get('start_time', ''), end_time=data.get('end_time', ''),
        volume=float(data.get('volume', 0)), volume_unit=data.get('volume_unit', 'м³'),
        equipment_used=data.get('equipment_used', ''), materials_used=data.get('materials_used', ''),
        notes=data.get('notes', ''), weather=data.get('weather', ''),
        temperature=float(data.get('temperature', 0)) if data.get('temperature') else 0,
        photo_paths='[]', created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    add_journal_entry(entry)
    return redirect(url_for('journal', site_id=int(data['site_id'])))

@app.route('/journal/delete/<int:entry_id>')
def delete_journal_entry_route(entry_id):
    entry = get_journal_entry_by_id(entry_id)
    if entry:
        delete_journal_entry(entry_id)
        return redirect(url_for('journal', site_id=entry.site_id))
    return redirect(url_for('index'))

@app.route('/journal/get/<int:entry_id>')
def get_journal_entry(entry_id):
    entry = get_journal_entry_by_id(entry_id)
    if entry:
        return jsonify({'id': entry.id, 'date': entry.date, 'work_type': entry.work_type,
            'work_description': entry.work_description, 'location': entry.location,
            'executor': entry.executor, 'responsible_person': entry.responsible_person,
            'workers_count': entry.workers_count, 'shift': entry.shift, 'start_time': entry.start_time,
            'end_time': entry.end_time, 'volume': entry.volume, 'volume_unit': entry.volume_unit,
            'equipment_used': entry.equipment_used, 'materials_used': entry.materials_used,
            'notes': entry.notes, 'weather': entry.weather})
    return jsonify({})

@app.route('/journal/update', methods=['POST'])
def update_journal_entry_route():
    data = request.form
    entry = get_journal_entry_by_id(int(data['entry_id']))
    if entry:
        entry.date = data['date']
        entry.work_type = data['work_type']
        entry.work_description = data['work_description']
        entry.location = data.get('location', '')
        entry.executor = data.get('executor', '')
        entry.responsible_person = data.get('responsible_person', '')
        entry.workers_count = int(data.get('workers_count', 0))
        entry.shift = data.get('shift', '1')
        entry.start_time = data.get('start_time', '')
        entry.end_time = data.get('end_time', '')
        entry.volume = float(data.get('volume', 0))
        entry.volume_unit = data.get('volume_unit', 'м³')
        entry.equipment_used = data.get('equipment_used', '')
        entry.materials_used = data.get('materials_used', '')
        entry.notes = data.get('notes', '')
        entry.weather = data.get('weather', '')
        entry.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_journal_entry(entry)
    return redirect(url_for('journal', site_id=entry.site_id))

# ============ ФОТО С ГЕОЛОКАЦИЕЙ (КАК TIMESTAMP) ============
@app.route('/photos/<int:site_id>')
def photos_page(site_id):
    site = get_site_by_id(site_id)
    section = request.args.get('section', '')
    photos = get_photos_by_site(site_id, section)
    return render_template('photos.html', site=site, photos=photos, section=section)

@app.route('/photo/add', methods=['POST'])
def add_photo_route():
    data = request.json
    # Сохраняем base64 изображение в файл
    photo_data = data['photo'].split(',')[1]
    image_bytes = base64.b64decode(photo_data)
    
    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{data['site_id']}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_bytes)
    
    photo = PhotoWithLocation(
        id=0,
        site_id=int(data['site_id']),
        photo_path=filepath,
        latitude=float(data.get('latitude', 0)),
        longitude=float(data.get('longitude', 0)),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        description=data.get('description', ''),
        document_section=data.get('section', '')
    )
    add_photo(photo)
    return jsonify({'success': True})

@app.route('/photo/delete/<int:photo_id>')
def delete_photo_route(photo_id):
    delete_photo(photo_id)
    return redirect(request.referrer or url_for('index'))

# ============ ДОКУМЕНТЫ ПО РАЗДЕЛАМ ============
@app.route('/documents/<int:site_id>/<section>')
def documents_section(site_id, section):
    site = get_site_by_id(site_id)
    docs = get_documents_by_site(site_id, section)
    section_names = {
        'incoming': 'Входящие документы',
        'outgoing': 'Исходящие документы', 
        'acts': 'Акты',
        'journals': 'Журналы',
        'executive': 'Исполнительная документация'
    }
    return render_template('documents.html', site=site, docs=docs, section=section, section_name=section_names.get(section, section))

@app.route('/document/add', methods=['POST'])
def add_document_route():
    doc = Document(
        id=0,
        site_id=int(request.form['site_id']),
        section=request.form['section'],
        title=request.form['title'],
        document_number=request.form.get('document_number', ''),
        date=request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
        description=request.form.get('description', ''),
        file_path='',  # здесь можно добавить загрузку файлов
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    add_document(doc)
    return redirect(url_for('documents_section', site_id=doc.site_id, section=doc.section))

@app.route('/document/delete/<int:doc_id>')
def delete_document_route(doc_id):
    doc = get_documents_by_site(0)  # временно, нужно исправить
    delete_document(doc_id)
    return redirect(request.referrer or url_for('index'))

# ============ НОРМАТИВЫ ============
@app.route('/normatives')
def normatives():
    doc_type = request.args.get('type', '')
    search = request.args.get('search', '')
    return render_template('normatives.html', normatives=get_all_normatives(doc_type, search),
                          search=search, selected_type=doc_type)

@app.route('/normative/<int:doc_id>')
def normative_view(doc_id):
    return render_template('normative_view.html', doc=get_normative_by_id(doc_id))

@app.route('/normative/favorite/<int:doc_id>/<int:is_favorite>')
def favorite_toggle(doc_id, is_favorite):
    toggle_favorite(doc_id, bool(is_favorite))
    return redirect(request.referrer or url_for('normatives'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)