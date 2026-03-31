from app import app, db, Organization, Employee, MeasurementDevice
from datetime import datetime, date

def init_db():
    with app.app_context():
        # Удаляем все таблицы и создаем заново
        db.drop_all()
        db.create_all()
        
        try:
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

            # Добавление тестового прибора
            device = MeasurementDevice(
                name='Виброанализатор КВАРЦ',
                model='АГАТ-М',
                serial_number='АМ2108',
                verification_number='С-ВЮМ/25-11-2023/214957821',
                verification_date=date(2023, 11, 25),
                valid_until=date(2024, 11, 24)
            )
            db.session.add(device)
            
            db.session.commit()
            print("База данных успешно инициализирована с тестовыми данными")
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db() 