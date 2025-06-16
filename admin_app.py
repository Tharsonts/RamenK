import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Simple admin app without complex database dependencies
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ramenk-admin-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Simple user storage (for demo purposes)
ADMIN_USERS = {
    'admin': {
        'password_hash': generate_password_hash('ramenk123'),
        'email': 'admin@ramenk.com',
        'is_admin': True
    }
}

def check_admin_auth():
    return session.get('admin_logged_in') and session.get('username') == 'admin'

def load_menu_data():
    """Carrega dados do menu_data.py"""
    try:
        from menu_data import MENU_SECTIONS
        return MENU_SECTIONS
    except ImportError:
        return []

def save_menu_data(menu_sections):
    """Salva dados no menu_data.py"""
    menu_data_content = f"MENU_SECTIONS = {json.dumps(menu_sections, indent=4, ensure_ascii=False)}"
    
    with open('menu_data.py', 'w', encoding='utf-8') as f:
        f.write(menu_data_content)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in ADMIN_USERS:
            user = ADMIN_USERS[username]
            if check_password_hash(user['password_hash'], password) and user['is_admin']:
                session['admin_logged_in'] = True
                session['username'] = username
                flash('Login realizado com sucesso!')
                return redirect(url_for('admin_dashboard'))
        
        flash('Credenciais inválidas ou acesso negado.')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    total_sections = len(menu_sections)
    total_items = sum(len(section.get('items', [])) for section in menu_sections)
    
    # Contar subsections
    total_subsections = 0
    for section in menu_sections:
        if 'subsections' in section:
            total_subsections += len(section['subsections'])
            for subsection in section['subsections']:
                total_items += len(subsection.get('items', []))
    
    stats = {
        'total_sections': total_sections,
        'total_items': total_items,
        'total_subsections': total_subsections
    }
    
    return render_template('admin/dashboard.html', menu_sections=menu_sections, stats=stats)

@app.route('/admin/sections')
def admin_sections():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    return render_template('admin/sections.html', sections=menu_sections)

@app.route('/admin/sections/create', methods=['GET', 'POST'])
def admin_create_section():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        menu_sections = load_menu_data()
        
        new_section = {
            'id': request.form['section_id'],
            'name': request.form['name'],
            'icon': request.form['icon'],
            'items': []
        }
        
        if request.form.get('subtitle'):
            new_section['subtitle'] = request.form['subtitle']
        
        menu_sections.append(new_section)
        save_menu_data(menu_sections)
        
        flash('Seção criada com sucesso!')
        return redirect(url_for('admin_sections'))
    
    return render_template('admin/create_section.html')

@app.route('/admin/sections/<section_id>/items')
def admin_section_items(section_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    section = None
    
    for s in menu_sections:
        if s['id'] == section_id:
            section = s
            break
    
    if not section:
        flash('Seção não encontrada!')
        return redirect(url_for('admin_sections'))
    
    return render_template('admin/section_items.html', section=section)

from werkzeug.utils import secure_filename

def save_item_image(file, section_id):
    if file and file.filename:
        filename = secure_filename(file.filename)
        folder_path = os.path.join("static", "img", section_id)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return f"img/{section_id}/{filename}"
    return None

@app.route('/admin/items/create/<section_id>', methods=['GET', 'POST'])
def admin_create_item(section_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    section = None
    section_index = None
    
    for i, s in enumerate(menu_sections):
        if s['id'] == section_id:
            section = s
            section_index = i
            break
    
    if not section:
        flash('Seção não encontrada!')
        return redirect(url_for('admin_sections'))
    
    # Garante que subsections sempre será uma lista
    subsections = section.get('subsections', [])

    if request.method == 'POST':
        new_item = {
            'name': request.form['name'],
            'price': request.form['price'],
            'description': request.form.get('description', '')
        }

        image_file = request.files.get('image')
        image_path = save_item_image(image_file, section_id)
        if image_path:
            new_item['image_path'] = image_path

        subsection_title = request.form.get('subsection_title')
        
        if subsection_title:
            if 'subsections' not in section:
                section['subsections'] = []
            
            subsection_found = False
            for subsection in section['subsections']:
                if subsection['title'] == subsection_title:
                    subsection['items'].append(new_item)
                    subsection_found = True
                    break
            
            if not subsection_found:
                new_subsection = {
                    'title': subsection_title,
                    'items': [new_item]
                }
                section['subsections'].append(new_subsection)
        else:
            if 'items' not in section:
                section['items'] = []
            section['items'].append(new_item)
        
        if section_index is not None:
            menu_sections[section_index] = section
        save_menu_data(menu_sections)
        
        flash('Item criado com sucesso!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    return render_template('admin/create_item.html', section=section, subsections=subsections)

@app.route('/admin/subsections/create/<section_id>', methods=['GET', 'POST'])
def admin_create_subsection(section_id):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    section = None
    section_index = None
    
    for i, s in enumerate(menu_sections):
        if s['id'] == section_id:
            section = s
            section_index = i
            break
    
    if not section:
        flash('Seção não encontrada!')
        return redirect(url_for('admin_sections'))
    
    if request.method == 'POST':
        if 'subsections' not in section:
            section['subsections'] = []
        
        new_subsection = {
            'title': request.form['title'],
            'description': request.form.get('description', ''),
            'items': []
        }
        
        section['subsections'].append(new_subsection)
        if section_index is not None:
            menu_sections[section_index] = section
        save_menu_data(menu_sections)
        
        flash('Subseção criada com sucesso!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    return render_template('admin/create_subsection.html', section=section)

@app.route('/admin/preview')
def admin_preview():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    return render_template('redesign.html', menu_sections=menu_sections)

@app.route('/admin/sections/<section_id>/items/<int:item_index>/edit', methods=['GET', 'POST'])
def admin_edit_item(section_id, item_index):
    if not check_admin_auth():
        return redirect(url_for('admin_login'))

    menu_sections = load_menu_data()
    section = next((s for s in menu_sections if s['id'] == section_id), None)

    if not section:
        flash('Seção não encontrada.', 'error')
        return redirect(url_for('admin_sections'))

    if 'items' not in section or item_index >= len(section['items']):
        flash('Item não encontrado.', 'error')
        return redirect(url_for('admin_section_items', section_id=section_id))

    item = section['items'][item_index]

    if request.method == 'POST':
        item['name'] = request.form['name']
        item['price'] = request.form['price']
        item['description'] = request.form.get('description', '')

        # Remoção de imagem (se marcada)
        if request.form.get('remove_image') == 'true' and item.get('image_path'):
            try:
                image_path = os.path.join('static', item['image_path'])
                if os.path.exists(image_path):
                    os.remove(image_path)
                item.pop('image_path', None)
                flash('Imagem removida com sucesso.', 'success')
            except Exception as e:
                flash(f'Erro ao remover imagem: {e}', 'error')

        # Upload de nova imagem
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            # Remover antiga se houver
            if item.get('image_path'):
                old_path = os.path.join('static', item['image_path'])
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Salvar nova imagem
            image_path = save_item_image(image_file, section_id)
            if image_path:
                item['image_path'] = image_path
                flash('Imagem atualizada com sucesso.', 'success')

        save_menu_data(menu_sections)
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('admin_section_items', section_id=section_id))

    return render_template('admin/edit_item.html', section=section, item=item, item_index=item_index)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
