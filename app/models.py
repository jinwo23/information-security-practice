from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# зв’язкові таблиці

user_roles = Table(
"user_roles",
Base.metadata,
Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
"role_permissions",
Base.metadata,
Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# User

class User(Base):
tablename = "users"

id = Column(Integer, primary_key=True)
username = Column(String)
email = Column(String)
password_hash = Column(String)
is_active = Column(Boolean, default=True)
group_id = Column(Integer, ForeignKey("groups.id"))

roles = relationship("Role", secondary=user_roles)
group = relationship("Group")

# Role

class Role(Base):
tablename = "roles"

id = Column(Integer, primary_key=True)
name = Column(String)

# Permission

class Permission(Base):
tablename = "permissions"

id = Column(Integer, primary_key=True)
name = Column(String)

# Group

class Group(Base):
tablename = "groups"

id = Column(Integer, primary_key=True)
name = Column(String)

# Subject

class Subject(Base):
tablename = "subjects"

id = Column(Integer, primary_key=True)
name = Column(String)
credits = Column(Float)

# Grade

class Grade(Base):
tablename = "grades"

id = Column(Integer, primary_key=True)
student_id = Column(Integer, ForeignKey("users.id"))
subject_id = Column(Integer, ForeignKey("subjects.id"))
grade = Column(Integer)
date_assigned = Column(DateTime, default=datetime.utcnow)
