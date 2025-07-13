# models.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    appointments = relationship("Appointment", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    bio = Column(String)
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    reviews = relationship("Review", back_populates="doctor")

class DoctorSchedule(Base):
    __tablename__ = 'doctor_schedules'
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    day_of_week = Column(Integer) # 0 = Monday, 6 = Sunday
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Integer, default=0)
    doctor = relationship("Doctor", back_populates="schedules")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    appointment_time = Column(DateTime)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    rating = Column(Integer)
    comment = Column(String)
    user = relationship("User", back_populates="reviews")
    doctor = relationship("Doctor", back_populates="reviews")
