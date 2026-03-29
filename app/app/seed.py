from app.database import SessionLocal
from app.models import User, Role, Permission, Group, Subject

def seed():
    db = SessionLocal()

    if db.query(Role).first():
        print("Already seeded")
        return

    admin = Role(name="admin")
    teacher = Role(name="teacher")
    student = Role(name="student")

    db.add_all([admin, teacher, student])
    db.commit()

    group = Group(name="КН-31")
    db.add(group)
    db.commit()

    subject = Subject(name="Security", credits=4.0)
    db.add(subject)
    db.commit()

    user = User(username="admin", email="admin@test.com", password_hash="123")
    db.add(user)
    db.commit()

    print("Seed done")

if __name__ == "__main__":
    seed()
