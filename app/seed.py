from app.database import SessionLocal
from app.models import User, Role, Permission, Group, Subject, Grade
from app.security import hash_password


def seed():
    db = SessionLocal()

    if db.query(User).first():
        print("Already seeded")
        db.close()
        return

    admin_role = Role(name="admin")
    teacher_role = Role(name="teacher")
    student_role = Role(name="student")

    db.add_all([admin_role, teacher_role, student_role])
    db.commit()

    read_grades = Permission(name="read_grades")
    edit_grades = Permission(name="edit_grades")
    read_schedule = Permission(name="read_schedule")

    db.add_all([read_grades, edit_grades, read_schedule])
    db.commit()

    group = Group(name="КН-31")
    db.add(group)
    db.commit()
    db.refresh(group)

    subject = Subject(name="Security", credits=4.0)
    db.add(subject)
    db.commit()
    db.refresh(subject)

    admin = User(
        username="admin",
        password_hash=hash_password("Admin123!"),
        full_name="Адміністратор системи",
        is_active=True,
    )
    admin.email = "admin@test.com"
    admin.roles.append(admin_role)

    teacher = User(
        username="teacher1",
        password_hash=hash_password("Teacher123!"),
        full_name="Тестовий викладач",
        is_active=True,
    )
    teacher.email = "teacher1@test.com"
    teacher.roles.append(teacher_role)

    student = User(
        username="student1",
        password_hash=hash_password("Student123!"),
        full_name="Тестовий студент",
        group_id=group.id,
        is_active=True,
    )
    student.email = "student1@test.com"
    student.roles.append(student_role)

    db.add_all([admin, teacher, student])
    db.commit()
    db.refresh(student)

    grade = Grade(
        student_id=student.id,
        subject_id=subject.id,
        grade=90,
    )
    db.add(grade)
    db.commit()

    db.close()
    print("Seed done")


if __name__ == "__main__":
    seed()