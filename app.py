from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_migrate import Migrate
import pdfkit
import tempfile

db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:159950707@localhost:5432/vibro_diagnostics'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Модели данных
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(50))
    power = db.Column(db.Float)
    frequency = db.Column(db.Float)
    installation_date = db.Column(db.Date)
    last_repair_date = db.Column(db.Date)
    # Добавляем связь с протоколами
    protocols = db.relationship('Protocol', backref='equipment', lazy=True)

class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protocol_number = db.Column(db.String(20), unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    object_id = db.Column(db.Integer, db.ForeignKey('object.id'))
    inspector_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    conclusion = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    measurements = db.relationship('Measurement', backref='protocol', lazy=True)
    # Добавляем связи с другими моделями
    object = db.relationship('Object', backref='protocols', lazy=True)
    inspector = db.relationship('Employee', foreign_keys=[inspector_id], backref='inspected_protocols', lazy=True)
    reviewer = db.relationship('Employee', foreign_keys=[reviewer_id], backref='reviewed_protocols', lazy=True)
    device_id = db.Column(db.Integer, db.ForeignKey('measurement_device.id'))

    def generate_protocol_number(self):
        year = datetime.now().year
        count = Protocol.query.filter(
            db.extract('year', Protocol.date) == year
        ).count()
        return f"ВД-{year}-{count+1:04d}"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    certification_number = db.Column(db.String(50))

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocol.id'))
    point_number = db.Column(db.Integer)  # Номер точки (1-12)
    vertical_value = db.Column(db.Float)  # Значение для вертикального направления
    horizontal_value = db.Column(db.Float)  # Значение для горизонтального направления
    axial_value = db.Column(db.Float)  # Значение для осевого направления
    defect_class = db.Column(db.String(100))  # Общая классификация дефекта для точки

# Добавим новые модели
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))

class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    address = db.Column(db.String(500))
    # Добавляем связь с организацией
    organization = db.relationship('Organization', backref='objects', lazy=True)

# Добавляем новую модель после существующих
class MeasurementDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Наименование прибора
    model = db.Column(db.String(100))  # Модель прибора
    serial_number = db.Column(db.String(50))  # Серийный номер
    verification_number = db.Column(db.String(50))  # Номер свидетельства о поверке
    verification_date = db.Column(db.Date)  # Дата поверки
    valid_until = db.Column(db.Date)  # Действительно до
    
    # Добавим связь с протоколами
    protocols = db.relationship('Protocol', backref='device', lazy=True)

# В начале файла добавьте конфигурацию
config = None
WKHTMLTOPDF_PATH = os.environ.get('WKHTMLTOPDF_PATH')

if WKHTMLTOPDF_PATH:
    try:
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    except IOError:
        print("Warning: wkhtmltopdf not found at the specified path. PDF generation will be disabled.")
else:
    # Попробуем найти в стандартном месте
    default_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    if os.path.exists(default_path):
        try:
            config = pdfkit.configuration(wkhtmltopdf=default_path)
        except IOError:
            print("Warning: Could not configure wkhtmltopdf, even though it was found. PDF generation will be disabled.")
    else:
        print("Warning: wkhtmltopdf not found. Please install it and/or set the WKHTMLTOPDF_PATH environment variable.")

@app.route('/')
def index():
    return render_template('index.html',
                         protocols=Protocol.query.order_by(Protocol.date.desc()).limit(10).all())

@app.route('/equipment', methods=['GET', 'POST'])
def equipment_list():
    if request.method == 'POST':
        equipment = Equipment(
            name=request.form['name'],
            model=request.form['model'],
            serial_number=request.form['serial_number'],
            power=float(request.form['power']),
            frequency=float(request.form['frequency']),
            installation_date=datetime.strptime(request.form['installation_date'], '%Y-%m-%d')
        )
        db.session.add(equipment)
        db.session.commit()
        flash('Оборудование успешно добавлено', 'success')
        return redirect(url_for('equipment_list'))
        
    return render_template('equipment_list.html', 
                         equipment=Equipment.query.all())

@app.route('/objects', methods=['GET', 'POST'])
def object_list():
    if request.method == 'POST':
        obj = Object(
            name=request.form['name'],
            organization_id=request.form['organization_id'],
            address=request.form['address']
        )
        db.session.add(obj)
        db.session.commit()
        flash('Объект успешно добавлен', 'success')
        return redirect(url_for('object_list'))
        
    return render_template('object_list.html',
                         objects=Object.query.all(),
                         organizations=Organization.query.all())

@app.route('/employees', methods=['GET', 'POST'])
def employee_list():
    if request.method == 'POST':
        employee = Employee(
            name=request.form['name'],
            position=request.form['position'],
            department=request.form['department'],
            certification_number=request.form['certification_number']
        )
        db.session.add(employee)
        db.session.commit()
        flash('Сотрудник успешно добавлен', 'success')
        return redirect(url_for('employee_list'))
        
    return render_template('employee_list.html',
                         employees=Employee.query.all())

@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        employee.name = request.form['name']
        employee.position = request.form['position']
        employee.department = request.form['department']
        employee.certification_number = request.form['certification_number']
        
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        db.session.delete(employee)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/protocols/print/<int:protocol_id>')
def print_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    measurements = prepare_measurements_data(protocol)
    return render_template('protocol_print.html', protocol=protocol, measurements=measurements)

@app.route('/protocols/new', methods=['GET', 'POST'])
def new_protocol():
    if request.method == 'POST':
        protocol = Protocol()
        protocol.equipment_id = request.form['equipment_id']
        protocol.object_id = request.form['object_id']
        protocol.inspector_id = request.form['inspector_id']
        protocol.reviewer_id = request.form['reviewer_id']
        protocol.device_id = request.form['device_id']
        protocol.conclusion = request.form['conclusion']
        protocol.recommendations = request.form['recommendations']
        
        # Генерация номера протокола
        protocol.protocol_number = protocol.generate_protocol_number()
        
        # Сохранение измерений
        for point in range(1, 13):
            measurement = Measurement(
                point_number=point,
                vertical_value=float(request.form.get(f'vertical_{point}', 0)) if request.form.get(f'vertical_{point}') else None,
                horizontal_value=float(request.form.get(f'horizontal_{point}', 0)) if request.form.get(f'horizontal_{point}') else None,
                axial_value=float(request.form.get(f'axial_{point}', 0)) if request.form.get(f'axial_{point}') else None,
                defect_class=request.form.get(f'defect_{point}', '')
            )
            protocol.measurements.append(measurement)
        
        db.session.add(protocol)
        db.session.commit()
        
        return redirect(url_for('view_protocol', protocol_id=protocol.id))
        
    return render_template('protocol_form.html',
                         equipments=Equipment.query.all(),
                         objects=Object.query.all(),
                         employees=Employee.query.all(),
                         devices=MeasurementDevice.query.all())

@app.route('/protocols/<int:protocol_id>')
def view_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    measurements = prepare_measurements_data(protocol)
    return render_template('protocol_view.html', protocol=protocol, measurements=measurements)

@app.route('/protocols')
def protocol_list():
    protocols = Protocol.query.order_by(Protocol.date.desc()).all()
    return render_template('protocol_list.html', protocols=protocols)

@app.route('/protocols/<int:protocol_id>', methods=['DELETE'])
def delete_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    try:
        db.session.delete(protocol)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/objects/<int:object_id>', methods=['DELETE'])
def delete_object(object_id):
    obj = Object.query.get_or_404(object_id)
    try:
        db.session.delete(obj)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/equipment/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    try:
        db.session.delete(equipment)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/equipment/<int:equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    try:
        equipment.name = request.form['name']
        equipment.model = request.form['model']
        equipment.serial_number = request.form['serial_number']
        equipment.power = float(request.form['power'])
        equipment.frequency = float(request.form['frequency'])
        equipment.installation_date = datetime.strptime(request.form['installation_date'], '%Y-%m-%d')
        
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/objects/<int:object_id>', methods=['PUT'])
def update_object(object_id):
    obj = Object.query.get_or_404(object_id)
    try:
        obj.name = request.form['name']
        obj.organization_id = request.form['organization_id']
        obj.address = request.form['address']
        
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/protocols/<int:protocol_id>/download')
def download_protocol(protocol_id):
    if not config:
        flash('Ошибка: Генерация PDF не настроена. Обратитесь к администратору.', 'danger')
        return redirect(url_for('view_protocol', protocol_id=protocol_id))

    protocol = Protocol.query.get_or_404(protocol_id)
    
    # Подготовка данных измерений
    measurements = prepare_measurements_data(protocol)
    
    # Создаем HTML для PDF
    html = render_template('protocol_print.html', protocol=protocol, measurements=measurements)
    
    # Конфигурация для pdfkit
    options = {
        'page-size': 'A4',
        'margin-top': '1.0cm',
        'margin-right': '1.0cm',
        'margin-bottom': '1.0cm',
        'margin-left': '1.0cm',
        'encoding': 'UTF-8',
        'enable-local-file-access': True,
        'footer-right': '[page] из [topage]'
    }
    
    # Создаем временный файл для PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        pdf_path = f.name
    
    try:
        pdfkit.from_string(html, pdf_path, options=options, configuration=config)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'Протокол_{protocol.protocol_number}.pdf'
        )
    finally:
        try:
            os.unlink(pdf_path)
        except:
            pass

@app.route('/devices', methods=['GET', 'POST'])
def device_list():
    if request.method == 'POST':
        device = MeasurementDevice(
            name=request.form['name'],
            model=request.form['model'],
            serial_number=request.form['serial_number'],
            verification_number=request.form['verification_number'],
            verification_date=datetime.strptime(request.form['verification_date'], '%Y-%m-%d'),
            valid_until=datetime.strptime(request.form['valid_until'], '%Y-%m-%d')
        )
        db.session.add(device)
        db.session.commit()
        flash('Прибор успешно добавлен', 'success')
        return redirect(url_for('device_list'))
        
    return render_template('device_list.html', 
                         devices=MeasurementDevice.query.all())

@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    device = MeasurementDevice.query.get_or_404(device_id)
    try:
        device.name = request.form['name']
        device.model = request.form['model']
        device.serial_number = request.form['serial_number']
        device.verification_number = request.form['verification_number']
        device.verification_date = datetime.strptime(request.form['verification_date'], '%Y-%m-%d')
        device.valid_until = datetime.strptime(request.form['valid_until'], '%Y-%m-%d')
        
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = MeasurementDevice.query.get_or_404(device_id)
    try:
        db.session.delete(device)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

def init_db():
    with app.app_context():
        # Создание всех таблиц
        db.create_all()
        
        try:
            # Проверка наличия тестовых данных
            if not Organization.query.first():
                # Добавление тестовой организации
                org = Organization(
                    name='ООО "Башнефть - Добыча"',
                    address='450077, Республика Башкортостан, г. Уфа',
                    phone='+7 347 261-61-61'
                )
                db.session.add(org)
                
                # Добавление тестового сотрудника
                emp = Employee(
                    name='Иванов Иван Иванович',
                    position='Инженер-диагност',
                    department='Лаборатория вибродиагностики',
                    certification_number='ЛНК-061А0073'
                )
                db.session.add(emp)
                
                db.session.commit()
                print("База данных успешно инициализирована с тестовыми данными")
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            db.session.rollback()

def prepare_measurements_data(protocol):
    measurements = {}
    for m in protocol.measurements:
        measurements[m.point_number] = {
            'vertical': {'value': m.vertical_value} if m.vertical_value is not None else None,
            'horizontal': {'value': m.horizontal_value} if m.horizontal_value is not None else None,
            'axial': {'value': m.axial_value} if m.axial_value is not None else None,
            'defect_class': m.defect_class
        }
    return measurements

if __name__ == '__main__':
    init_db()  # Инициализация базы данных при запуске
    app.run(debug=True) 