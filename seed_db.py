# seed_db.py
from database import SessionLocal, init_db
from models import User, Doctor, DoctorSchedule, Appointment, Review, UserRole, AppointmentStatus
from datetime import datetime, time

def seed_data():
    db = SessionLocal()

    # Clear existing data
    db.query(Review).delete()
    db.query(Appointment).delete()
    db.query(DoctorSchedule).delete()
    db.query(User).delete()
    db.query(Doctor).delete()

    # Create users
    user1 = User(telegram_id=12345, first_name="Alice", role=UserRole.PATIENT)
    user2 = User(telegram_id=67890, first_name="Bob", role=UserRole.PATIENT)
    db.add_all([user1, user2])
    db.commit()

    # Create doctors
    doctor1 = Doctor(name="Dr. Smith", specialty="Cardiology", bio="Expert in heart health.")
    doctor2 = Doctor(name="Dr. Jones", specialty="Pediatrics", bio="Cares for children's health.")
    doctor3 = Doctor(name="Dr. Brown", specialty="Dermatology", bio="Specializes in skin conditions.")
    db.add_all([doctor1, doctor2, doctor3])
    db.commit()

    # Create schedules
    schedule1 = DoctorSchedule(doctor_id=doctor1.id, day_of_week=0, start_time=datetime.strptime("09:00", "%H:%M").time(), end_time=datetime.strptime("17:00", "%H:%M").time())
    schedule2 = DoctorSchedule(doctor_id=doctor2.id, day_of_week=1, start_time=datetime.strptime("10:00", "%H:%M").time(), end_time=datetime.strptime("18:00", "%H:%M").time())
    db.add_all([schedule1, schedule2])
    db.commit()

    # Create appointments
    appointment1 = Appointment(user_id=user1.id, doctor_id=doctor1.id, appointment_time=datetime(2024, 5, 20, 10, 0), status=AppointmentStatus.SCHEDULED)
    db.add(appointment1)
    db.commit()

    # Create reviews
    review1 = Review(user_id=user1.id, doctor_id=doctor1.id, rating=5, comment="Excellent doctor!")
    db.add(review1)
    db.commit()

    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database seeded successfully!")
