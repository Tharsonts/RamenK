import os
import json
import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ramenk-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Upload configuration
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Simple admin users
ADMIN_USERS = {
    'admin': {
        'password_hash': generate_password_hash('ramenk123'),
        'email': 'admin@ramenk.com',
        'is_admin': True
    }
}

def check_admin_auth():
    return session.get('admin_logged_in') and session.get('username') == 'admin'

def load_menu_data(only_visible=False):
    """Carrega dados do menu_data.py"""
    try:
        import sys
        import importlib
        # Recarrega o módulo para pegar mudanças em tempo real
        if 'menu_data' in sys.modules:
            importlib.reload(sys.modules['menu_data'])
        from menu_data import MENU_SECTIONS
        if only_visible:
            return [section for section in MENU_SECTIONS if section.get("visible", True)]
        return MENU_SECTIONS
    except ImportError:
        return []

def save_menu_data(menu_sections):
    """Salva dados no menu_data.py"""
    import pprint
    
    # Usar pprint para manter sintaxe Python (True/False em vez de true/false)
    formatted_data = pprint.pformat(menu_sections, indent=4, width=120)
    menu_data_content = f"MENU_SECTIONS = {formatted_data}"
    
    with open('menu_data.py', 'w', encoding='utf-8') as f:
        f.write(menu_data_content)

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_section_folder(section_id):
    """Cria pasta para a seção se não existir"""
    section_folder = os.path.join(app.config['UPLOAD_FOLDER'], section_id)
    if not os.path.exists(section_folder):
        os.makedirs(section_folder)
        logging.info(f"Pasta criada para seção: {section_folder}")
    return section_folder

def save_uploaded_image(file, section_id):
    """Salva imagem na pasta da seção e retorna o caminho relativo"""
    if file and allowed_file(file.filename):
        # Criar pasta da seção
        section_folder = create_section_folder(section_id)
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Caminho completo do arquivo
        file_path = os.path.join(section_folder, unique_filename)
        
        # Salvar arquivo
        file.save(file_path)
        
        # Retornar caminho relativo para usar no HTML
        relative_path = os.path.join('img', section_id, unique_filename).replace('\\', '/')
        logging.info(f"Imagem salva: {relative_path}")
        return relative_path
    
    return None

# Main routes
@app.route('/')
def index():
    menu_sections = load_menu_data(only_visible=True)
    return render_template('redesign.html', menu_sections=menu_sections)

@app.route('/old')
def old_design():
    menu_sections = load_menu_data(only_visible=True)
    return render_template('modern-japanese.html', menu_sections=menu_sections)

# ADMIN ROUTES
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
        
        section_id = request.form['section_id']
        
        new_section = {
            'id': section_id,
            'name': request.form['name'],
            'icon': request.form['icon'],
            'items': []
        }
        
        if request.form.get('subtitle'):
            new_section['subtitle'] = request.form['subtitle']
        
        # Criar pasta da seção automaticamente
        create_section_folder(section_id)
        
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
        # Formatar preço automaticamente
        price = request.form['price']
        if price and not price.startswith('R$'):
            # Se for apenas números, formatar como moeda
            if price.replace(',', '').replace('.', '').isdigit():
                # Converter "60" para "R$ 60,00"
                if ',' not in price:
                    price = price + ',00'
                price = 'R$ ' + price
            elif not price.startswith('R$'):
                price = 'R$ ' + price
        
        # Processar upload de imagem
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                image_path = save_uploaded_image(file, section_id)
                if image_path:
                    flash('Imagem enviada com sucesso!')
                else:
                    flash('Erro ao enviar imagem. Verifique o formato (PNG, JPG, JPEG, GIF, WEBP).', 'error')

        new_item = {
            'name': request.form['name'],
            'price': price,
            'description': request.form.get('description', ''),
            'image_path': image_path
        }
        
        # Processar subseção selecionada
        subsection_id = request.form.get('subsection_id')
        
        if subsection_id:
            # Adicionar à subsection existente
            if 'subsections' not in section:
                section['subsections'] = []
            
            # Procurar subsection pelo índice
            try:
                subsection_index = int(subsection_id)
                if 0 <= subsection_index < len(section['subsections']):
                    section['subsections'][subsection_index]['items'].append(new_item)
                else:
                    # Se índice inválido, adicionar diretamente à section
                    if 'items' not in section:
                        section['items'] = []
                    section['items'].append(new_item)
            except (ValueError, IndexError):
                # Se erro ao processar índice, adicionar diretamente à section
                if 'items' not in section:
                    section['items'] = []
                section['items'].append(new_item)
        else:
            # Adicionar diretamente à section
            if 'items' not in section:
                section['items'] = []
            section['items'].append(new_item)
        
        if section_index is not None:
            menu_sections[section_index] = section
        save_menu_data(menu_sections)
        
        flash('Item criado com sucesso!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    return render_template('admin/create_item.html', section=section, subsections=subsections, section_id=section_id)

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

@app.route('/admin/menu-navigation', methods=['GET', 'POST'])
def admin_menu_navigation():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data()
    
    if request.method == 'POST':
        # Processar atualizações de visibilidade e ordem das seções
        for section in menu_sections:
            section_id = section['id']
            
            # Atualizar visibilidade
            visible_key = f'visible_{section_id}'
            section['visible'] = visible_key in request.form
            
            # Atualizar posição
            position_key = f'position_{section_id}'
            if position_key in request.form:
                try:
                    section['position'] = int(request.form[position_key])
                except ValueError:
                    section['position'] = 0
        
        # Ordenar seções por posição
        menu_sections.sort(key=lambda x: x.get('position', 0))
        
        save_menu_data(menu_sections)
        flash('Configurações do menu lateral atualizadas com sucesso!')
        return redirect(url_for('admin_menu_navigation'))
    
    return render_template('admin/menu_navigation.html', menu_sections=menu_sections)

@app.route('/admin/preview')
def admin_preview():
    if not check_admin_auth():
        return redirect(url_for('admin_login'))
    
    menu_sections = load_menu_data(only_visible=True)
    return render_template('redesign.html', menu_sections=menu_sections)

@app.route('/admin/sections/<section_id>/items/<int:item_index>/edit', methods=['GET', 'POST'])
def admin_edit_item(section_id, item_index):
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
    
    if not section or item_index >= len(section.get('items', [])):
        flash('Item não encontrado!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    item = section['items'][item_index]
    
    if request.method == 'POST':
        # Formatar preço automaticamente
        price = request.form.get('price', '')
        if price and not price.startswith('R$'):
            # Se for apenas números, formatar como moeda
            if price.replace(',', '').replace('.', '').isdigit():
                # Converter "60" para "R$ 60,00"
                if ',' not in price:
                    price = price + ',00'
                price = 'R$ ' + price
            elif not price.startswith('R$'):
                price = 'R$ ' + price
        
        # Atualizar dados básicos do item
        item['name'] = request.form.get('name', '')
        item['description'] = request.form.get('description', '')
        item['price'] = price
        
        # Processar upload de nova imagem
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Salvar caminho da imagem atual para deletar depois
                old_image_path = item.get('image_path')
                
                # Salvar nova imagem
                new_image_path = save_uploaded_image(file, section_id)
                
                if new_image_path:
                    # Deletar imagem antiga se existir e for diferente da nova
                    if old_image_path and old_image_path != new_image_path:
                        try:
                            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_path.replace('img/', ''))
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                                logging.info(f"Imagem antiga deletada: {old_file_path}")
                        except Exception as e:
                            logging.error(f"Erro ao deletar imagem antiga: {e}")
                    
                    # Atualizar caminho da imagem no item
                    item['image_path'] = new_image_path
                    flash('Imagem atualizada com sucesso!')
                else:
                    flash('Erro ao enviar nova imagem. Verifique o formato (PNG, JPG, JPEG, GIF, WEBP).', 'error')
        
        # Verificar se o usuário quer remover a imagem (campo hidden)
        remove_image = request.form.get('remove_image') == 'true'
        if remove_image and item.get('image_path'):
            old_image_path = item.get('image_path')
            try:
                # Deletar arquivo físico
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_path.replace('img/', ''))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    logging.info(f"Imagem removida durante edição: {old_file_path}")
                
                # Remover referência no item
                del item['image_path']
                flash('Imagem removida com sucesso!')
            except Exception as e:
                logging.error(f"Erro ao remover imagem durante edição: {e}")
                flash('Erro ao remover imagem. Tente novamente.', 'error')
        
        # Salvar alterações
        menu_sections[section_index] = section
        save_menu_data(menu_sections)
        
        flash('Item atualizado com sucesso!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    return render_template('admin/edit_item.html', section=section, item=item, item_index=item_index)

@app.route('/admin/sections/<section_id>/items/<int:item_index>/delete', methods=['POST'])
def admin_delete_item(section_id, item_index):
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
    
    if not section or item_index >= len(section.get('items', [])):
        flash('Item não encontrado!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    # Remover o item
    item_name = section['items'][item_index].get('name', 'Item')
    del section['items'][item_index]
    
    # Salvar alterações
    menu_sections[section_index] = section
    save_menu_data(menu_sections)
    
    flash(f'Item "{item_name}" excluído com sucesso!')
    return redirect(url_for('admin_section_items', section_id=section_id))

@app.route('/admin/sections/<section_id>/items/<int:item_index>/delete-image', methods=['POST'])
def admin_delete_item_image(section_id, item_index):
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
    
    if not section or item_index >= len(section.get('items', [])):
        flash('Item não encontrado!')
        return redirect(url_for('admin_section_items', section_id=section_id))
    
    item = section['items'][item_index]
    old_image_path = item.get('image_path')
    
    if old_image_path:
        try:
            # Deletar arquivo físico
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_path.replace('img/', ''))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
                logging.info(f"Imagem deletada: {old_file_path}")
            
            # Remover referência no item
            del item['image_path']
            
            # Salvar alterações
            menu_sections[section_index] = section
            save_menu_data(menu_sections)
            
            flash('Imagem removida com sucesso!')
        except Exception as e:
            logging.error(f"Erro ao deletar imagem: {e}")
            flash('Erro ao remover imagem. Tente novamente.', 'error')
    else:
        flash('Este item não possui imagem para remover.', 'error')
    
    return redirect(url_for('admin_edit_item', section_id=section_id, item_index=item_index))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)