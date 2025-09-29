"""
Test configuration and fixtures for CRM application tests
"""
import pytest
import tempfile
import os
from app import create_app
from models import db, User, Customer, Product, Category, Store, Employee, Position, Department
from config import Config


class TestConfig(Config):
    """Test configuration with in-memory database"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    LOG_LEVEL = 'ERROR'


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create test app with test configuration
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing"""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_customer(db_session):
    """Create sample customer for testing"""
    customer = Customer(
        first_name='太郎',
        last_name='田中',
        email='tanaka@example.com',
        phone='090-1234-5678',
        company='テスト株式会社'
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_category(db_session):
    """Create sample category for testing"""
    category = Category(
        name='テストカテゴリ',
        description='テスト用のカテゴリです'
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create sample product for testing"""
    product = Product(
        name='テスト製品',
        sku='TEST-001',
        price=1000.00,
        category_id=sample_category.id,
        description='テスト用の製品です',
        cost=800.00,
        stock_quantity=100,
        min_stock_level=10
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def sample_store_data():
    """Create sample store data for testing"""
    from datetime import date
    return {
        'name': 'Test Store',
        'address': '123 Test Street, Test City',
        'phone': '123-456-7890',
        'email': 'test@store.com',
        'business_hours': {
            'mon': '09:00-18:00',
            'tue': '09:00-18:00',
            'wed': '09:00-18:00',
            'thu': '09:00-18:00',
            'fri': '09:00-18:00',
            'sat': '10:00-17:00',
            'sun': 'closed'
        },
        'closed_days': '日曜日',
        'status': 'active',
        'location_prefecture': '東京都',
        'location_city': '渋谷区',
        'establishment_date': date(2020, 1, 1)
    }


@pytest.fixture
def sample_store(db_session, sample_store_data):
    """Create sample store for testing"""
    store = Store(**sample_store_data)
    db_session.add(store)
    db_session.commit()
    return store


@pytest.fixture
def authenticated_client(client, sample_user):
    """Create authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_user.id)
        sess['_fresh'] = True
    return client


# Employee-related fixtures

@pytest.fixture
def sample_position(db_session):
    """Create sample position for testing"""
    position = Position(
        name='店長',
        level=1,
        description='店舗の責任者',
        is_management=True,
        salary_min=400,
        salary_max=800,
        is_active=True
    )
    db_session.add(position)
    db_session.commit()
    return position


@pytest.fixture
def sample_staff_position(db_session):
    """Create sample staff position for testing"""
    position = Position(
        name='スタッフ',
        level=5,
        description='一般スタッフ',
        is_management=False,
        salary_min=200,
        salary_max=400,
        is_active=True
    )
    db_session.add(position)
    db_session.commit()
    return position


@pytest.fixture
def sample_department(db_session):
    """Create sample department for testing"""
    department = Department(
        name='営業部',
        description='営業担当部署',
        is_active=True
    )
    db_session.add(department)
    db_session.commit()
    return department


@pytest.fixture
def sample_sub_department(db_session, sample_department):
    """Create sample sub-department for testing"""
    sub_dept = Department(
        name='第一営業課',
        parent_id=sample_department.id,
        description='第一営業課',
        is_active=True
    )
    db_session.add(sub_dept)
    db_session.commit()
    return sub_dept


@pytest.fixture
def sample_employee_data():
    """Create sample employee data for testing"""
    from datetime import date
    return {
        'employee_code': 'EMP001',
        'first_name': '太郎',
        'last_name': '田中',
        'email': 'tanaka@company.com',
        'phone': '090-1234-5678',
        'hire_date': date(2023, 4, 1),
        'employment_status': 'active',
        'salary_level': 3,
        'emergency_contact_name': '田中花子',
        'emergency_contact_phone': '090-8765-4321',
        'notes': 'テスト従業員'
    }


@pytest.fixture
def sample_employee(db_session, sample_store, sample_position, sample_department, sample_employee_data):
    """Create sample employee for testing"""
    employee_data = sample_employee_data.copy()
    employee_data.update({
        'store_id': sample_store.id,
        'position_id': sample_position.id,
        'department_id': sample_department.id
    })
    employee = Employee(**employee_data)
    db_session.add(employee)
    db_session.commit()
    return employee


@pytest.fixture
def sample_manager(db_session, sample_store, sample_position, sample_department):
    """Create sample manager for testing"""
    from datetime import date
    manager = Employee(
        employee_code='MGR001',
        first_name='一郎',
        last_name='佐藤',
        email='sato@company.com',
        phone='090-1111-2222',
        hire_date=date(2020, 1, 1),
        employment_status='active',
        salary_level=6,
        store_id=sample_store.id,
        position_id=sample_position.id,
        department_id=sample_department.id
    )
    db_session.add(manager)
    db_session.commit()
    return manager


@pytest.fixture
def sample_subordinate(db_session, sample_store, sample_staff_position, sample_department, sample_manager):
    """Create sample subordinate for testing"""
    from datetime import date
    subordinate = Employee(
        employee_code='EMP002',
        first_name='二郎',
        last_name='鈴木',
        email='suzuki@company.com',
        phone='090-3333-4444',
        hire_date=date(2023, 6, 1),
        employment_status='active',
        salary_level=2,
        store_id=sample_store.id,
        position_id=sample_staff_position.id,
        department_id=sample_department.id,
        manager_id=sample_manager.id
    )
    db_session.add(subordinate)
    db_session.commit()
    return subordinate


@pytest.fixture
def multiple_employees(db_session, sample_store, sample_position, sample_staff_position, sample_department):
    """Create multiple employees for testing"""
    from datetime import date
    employees = []

    # Manager
    manager = Employee(
        employee_code='MGR100',
        first_name='管理',
        last_name='者',
        email='manager@company.com',
        hire_date=date(2019, 1, 1),
        employment_status='active',
        salary_level=7,
        store_id=sample_store.id,
        position_id=sample_position.id,
        department_id=sample_department.id
    )
    db_session.add(manager)
    employees.append(manager)

    # Staff members
    for i in range(1, 4):
        employee = Employee(
            employee_code=f'STAFF{i:03d}',
            first_name=f'従業員{i}',
            last_name='テスト',
            email=f'staff{i}@company.com',
            hire_date=date(2023, i, 1),
            employment_status='active',
            salary_level=i,
            store_id=sample_store.id,
            position_id=sample_staff_position.id,
            department_id=sample_department.id,
            manager_id=manager.id
        )
        db_session.add(employee)
        employees.append(employee)

    db_session.commit()
    return employees