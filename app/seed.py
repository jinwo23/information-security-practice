from app.database import SessionLocal
from app.models import User, Role, Permission, Group, Subject

def seed():
    db = SessionLocal()

    # якщо вже є дані — не дублюємо
    if db.query(Role).first():
        print("Already seeded")
        return

    # ролі
    admin = Role(name="admin")
    teacher = Role(name="teacher")
    student = Role(name="student")

    db.add_all([admin, teacher, student])
    db.commit()

    # permissions
    perms = [
        Permission(name="read_grades"),
        Permission(name="edit_grades"),
        Permission(name="read_schedule"),
    ]
    db.add_all(perms)
    db.commit()

    # група
    group = Group(name="КН-31")
    db.add(group)
    db.commit()

    # предмет
    subject = Subject(name="Security", credits=4.0)
    db.add(subject)
    db.commit()

    # користувач
    user = User(
        username="admin",
        email="admin@test.com",
        password_hash="123"
    )
    db.add(user)
    db.commit()

    print("Seed done")

if __name__ == "__main__":
    seed()
