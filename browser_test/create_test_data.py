"""
Create test data for employee management system
"""
from app import create_app
from models import db, User, Store, Position, Department, Employee
from datetime import date, datetime


def create_test_data():
    """Create comprehensive test data"""
    app = create_app()

    with app.app_context():
        print("Creating test data...")

        # Clear existing data (be careful!)
        print("Clearing existing employee data...")
        Employee.query.delete()
        Position.query.delete()
        Department.query.delete()

        # Create test user if not exists
        test_user = User.query.filter_by(username='admin').first()
        if not test_user:
            print("Creating admin user...")
            test_user = User(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            db.session.add(test_user)

        # Create or get test store
        test_store = Store.query.filter_by(name='Test Store').first()
        if not test_store:
            print("Creating test store...")
            test_store = Store(
                name='Test Store',
                address='Tokyo, Japan',
                phone='03-1234-5678'
            )
            db.session.add(test_store)

        db.session.commit()

        # Create positions
        print("Creating positions...")
        positions = [
            Position(name='CEO', level=1, is_management=True, salary_min=10000, salary_max=20000),
            Position(name='Manager', level=3, is_management=True, salary_min=6000, salary_max=10000),
            Position(name='Senior Staff', level=5, is_management=False, salary_min=4000, salary_max=6000),
            Position(name='Staff', level=7, is_management=False, salary_min=3000, salary_max=4000),
            Position(name='Intern', level=9, is_management=False, salary_min=2000, salary_max=3000),
        ]

        for pos in positions:
            db.session.add(pos)

        db.session.commit()
        print(f"Created {len(positions)} positions")

        # Create departments
        print("Creating departments...")
        dept_sales = Department(name='Sales Department', description='Sales and marketing')
        dept_hr = Department(name='HR Department', description='Human resources')
        dept_it = Department(name='IT Department', description='Information technology')

        db.session.add_all([dept_sales, dept_hr, dept_it])
        db.session.commit()

        # Create sub-departments
        dept_sales_team1 = Department(
            name='Sales Team 1',
            description='First sales team',
            parent_id=dept_sales.id
        )
        dept_sales_team2 = Department(
            name='Sales Team 2',
            description='Second sales team',
            parent_id=dept_sales.id
        )

        db.session.add_all([dept_sales_team1, dept_sales_team2])
        db.session.commit()
        print(f"Created 5 departments")

        # Get positions
        pos_ceo = Position.query.filter_by(name='CEO').first()
        pos_manager = Position.query.filter_by(name='Manager').first()
        pos_senior = Position.query.filter_by(name='Senior Staff').first()
        pos_staff = Position.query.filter_by(name='Staff').first()
        pos_intern = Position.query.filter_by(name='Intern').first()

        # Create employees
        print("Creating employees...")

        # CEO
        emp_ceo = Employee(
            employee_code='EMP001',
            first_name='Taro',
            last_name='Yamada',
            email='yamada@example.com',
            phone='090-1111-1111',
            hire_date=date(2020, 1, 1),
            employment_status='active',
            salary_level=10,
            store_id=test_store.id,
            position_id=pos_ceo.id,
            department_id=dept_sales.id
        )
        emp_ceo.birth_date = date(1980, 5, 15)
        db.session.add(emp_ceo)
        db.session.commit()

        # Managers
        emp_mgr1 = Employee(
            employee_code='EMP002',
            first_name='Hanako',
            last_name='Sato',
            email='sato@example.com',
            phone='090-2222-2222',
            hire_date=date(2021, 4, 1),
            employment_status='active',
            salary_level=7,
            store_id=test_store.id,
            position_id=pos_manager.id,
            department_id=dept_sales_team1.id,
            manager_id=emp_ceo.id
        )
        emp_mgr1.birth_date = date(1985, 8, 20)

        emp_mgr2 = Employee(
            employee_code='EMP003',
            first_name='Ichiro',
            last_name='Tanaka',
            email='tanaka@example.com',
            phone='090-3333-3333',
            hire_date=date(2021, 6, 1),
            employment_status='active',
            salary_level=6,
            store_id=test_store.id,
            position_id=pos_manager.id,
            department_id=dept_hr.id,
            manager_id=emp_ceo.id
        )
        emp_mgr2.birth_date = date(1987, 12, 10)

        db.session.add_all([emp_mgr1, emp_mgr2])
        db.session.commit()

        # Senior staff
        emp_senior1 = Employee(
            employee_code='EMP004',
            first_name='Yuki',
            last_name='Suzuki',
            email='suzuki@example.com',
            phone='090-4444-4444',
            hire_date=date(2022, 1, 15),
            employment_status='active',
            salary_level=5,
            store_id=test_store.id,
            position_id=pos_senior.id,
            department_id=dept_sales_team1.id,
            manager_id=emp_mgr1.id
        )
        emp_senior1.birth_date = date(1990, 3, 25)

        db.session.add(emp_senior1)
        db.session.commit()

        # Staff
        for i in range(5, 10):
            emp = Employee(
                employee_code=f'EMP{i:03d}',
                first_name=f'Employee{i}',
                last_name='Test',
                email=f'emp{i}@example.com',
                phone=f'090-{i}{i}{i}{i}-{i}{i}{i}{i}',
                hire_date=date(2023, (i % 12) + 1, 1),
                employment_status='active' if i % 3 != 0 else 'on_leave',
                salary_level=(i % 5) + 1,
                store_id=test_store.id,
                position_id=pos_staff.id if i % 2 == 0 else pos_intern.id,
                department_id=dept_sales_team1.id if i % 2 == 0 else dept_it.id,
                manager_id=emp_mgr1.id if i % 2 == 0 else emp_mgr2.id
            )
            emp.birth_date = date(1995 + (i % 5), (i % 12) + 1, i)
            db.session.add(emp)

        db.session.commit()

        print("\nTest data created successfully!")
        print("\n" + "="*60)
        print("Login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("="*60)
        print("\nEmployees created:")
        print("  Total: 9 employees")
        print("  - 1 CEO (Taro Yamada)")
        print("  - 2 Managers (Hanako Sato, Ichiro Tanaka)")
        print("  - 1 Senior Staff (Yuki Suzuki)")
        print("  - 5 Staff/Interns")
        print("\nDepartments:")
        print("  - Sales Department")
        print("    - Sales Team 1")
        print("    - Sales Team 2")
        print("  - HR Department")
        print("  - IT Department")
        print("="*60)


if __name__ == '__main__':
    create_test_data()