# bot.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import SessionLocal
from models import User, Doctor

# Conversation states
SELECTING_ACTION, ASKING_FOR_NAME, SELECTING_SPECIALTY, SELECTING_DOCTOR, SELECTING_TIME, BOOKING, LEAVING_REVIEW, RECEIVING_REVIEW = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the user's name if not known."""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.message.from_user.id).first()
    db.close()

    if user:
        await update.message.reply_text(f"Welcome back, {user.first_name}!")
        if user.role == UserRole.PATIENT:
            await main_menu(update, context)
            return SELECTING_ACTION
        elif user.role == UserRole.DOCTOR:
            await doctor_menu(update, context)
            return SELECTING_ACTION
    else:
        await update.message.reply_text("Welcome to the Doctor Bot! What is your first name?")
        return ASKING_FOR_NAME

async def doctor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main menu for doctors."""
    keyboard = [
        [InlineKeyboardButton("View Schedule", callback_data='view_schedule')],
        [InlineKeyboardButton("My Reviews", callback_data='my_reviews')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Doctor Menu:", reply_markup=reply_markup)

async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the doctor's schedule."""
    # This is a placeholder for the doctor's schedule view
    await update.callback_query.message.reply_text("Here is your schedule...")
    return SELECTING_ACTION

async def my_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the doctor's reviews."""
    db = SessionLocal()
    # Assuming the doctor's user is linked to a doctor entry
    doctor = db.query(Doctor).filter(Doctor.name == "Dr. Smith").first() # Simplified for example
    reviews = db.query(Review).filter(Review.doctor_id == doctor.id).all()
    db.close()

    if not reviews:
        await update.callback_query.message.reply_text("You have no reviews.")
        return SELECTING_ACTION

    message = "Your reviews:\n"
    for r in reviews:
        message += f"- {r.rating}/5: {r.comment}\n"

    await update.callback_query.message.reply_text(message)
    return SELECTING_ACTION

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main menu."""
    keyboard = [
        [InlineKeyboardButton("Book an Appointment", callback_data='book_appointment')],
        [InlineKeyboardButton("My Appointments", callback_data='my_appointments')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose an option:", reply_markup=reply_markup)

async def my_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the user's appointments."""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.callback_query.from_user.id).first()
    appointments = db.query(Appointment).filter(Appointment.user_id == user.id).all()
    db.close()

    if not appointments:
        await update.callback_query.message.reply_text("You have no appointments.")
        return SELECTING_ACTION

    message = "Your appointments:\n"
    keyboard = []
    for app in appointments:
        doctor = db.query(Doctor).filter(Doctor.id == app.doctor_id).first()
        message += f"- Dr. {doctor.name} on {app.appointment_time.strftime('%Y-%m-%d %H:%M')} ({app.status.value})\n"
        if app.status == AppointmentStatus.COMPLETED:
            keyboard.append([InlineKeyboardButton(f"Leave a review for Dr. {doctor.name}", callback_data=f"review_{app.id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
    return LEAVING_REVIEW

async def ask_for_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user for a review."""
    query = update.callback_query
    appointment_id = int(query.data.split('_')[1])
    context.user_data['appointment_id'] = appointment_id
    await query.message.reply_text("Please enter your review (rating 1-5 and a comment):")
    return RECEIVING_REVIEW

async def received_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the user's review."""
    db = SessionLocal()
    appointment_id = context.user_data['appointment_id']
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    # Simple parsing of review text, assuming "5 Great doctor"
    parts = update.message.text.split(" ", 1)
    rating = int(parts[0])
    comment = parts[1]

    review = Review(
        user_id=appointment.user_id,
        doctor_id=appointment.doctor_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    db.commit()
    db.close()

    await update.message.reply_text("Thank you for your review!")
    await main_menu(update.message, context)
    return ConversationHandler.END

async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the user's name and shows the main menu."""
    db = SessionLocal()
    user = User(telegram_id=update.message.from_user.id, first_name=update.message.text)
    db.add(user)
    db.commit()
    db.close()

    await update.message.reply_text(f"Thanks, {user.first_name}! I've saved your name.")
    await main_menu(update, context)
    return SELECTING_ACTION

async def select_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows a list of specialties."""
    db = SessionLocal()
    specialties = db.query(Doctor.specialty).distinct().all()
    db.close()

    keyboard = [[InlineKeyboardButton(s[0], callback_data=f"spec_{s[0]}")] for s in specialties]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Please choose a specialty:", reply_markup=reply_markup)
    return SELECTING_DOCTOR

from datetime import datetime, timedelta

async def select_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows a list of doctors for the selected specialty."""
    query = update.callback_query
    specialty = query.data.split('_')[1]
    context.user_data['specialty'] = specialty

    db = SessionLocal()
    doctors = db.query(Doctor).filter(Doctor.specialty == specialty).all()
    db.close()

    keyboard = [[InlineKeyboardButton(d.name, callback_data=f"doc_{d.id}")] for d in doctors]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Please choose a doctor:", reply_markup=reply_markup)
    return SELECTING_TIME

async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the selected doctor's schedule for the next 7 days."""
    query = update.callback_query
    doctor_id = int(query.data.split('_')[1])
    context.user_data['doctor_id'] = doctor_id

    db = SessionLocal()
    schedule = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id).all()
    db.close()

    keyboard = []
    today = datetime.today()
    for i in range(7):
        day = today + timedelta(days=i)
        for s in schedule:
            if s.day_of_week == day.weekday():
                keyboard.append([InlineKeyboardButton(day.strftime("%A, %B %d"), callback_data=f"day_{day.strftime('%Y-%m-%d')}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Please choose a day:", reply_markup=reply_markup)
    return BOOKING

async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Books the appointment."""
    query = update.callback_query
    day = query.data.split('_')[1]
    doctor_id = context.user_data['doctor_id']

    # This is a simplified booking logic. A real-world scenario would be more complex.
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
    appointment_time = datetime.strptime(day, "%Y-%m-%d")

    appointment = Appointment(
        user_id=user.id,
        doctor_id=doctor_id,
        appointment_time=appointment_time,
        status=AppointmentStatus.SCHEDULED
    )
    db.add(appointment)
    db.commit()
    db.close()

    await query.message.reply_text("Your appointment has been booked successfully!")
    await main_menu(query.message, context)
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    from config import TELEGRAM_BOT_TOKEN
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_name)],
            SELECTING_ACTION: [
                CallbackQueryHandler(select_specialty, pattern='^book_appointment$'),
                CallbackQueryHandler(my_appointments, pattern='^my_appointments$'),
                CallbackQueryHandler(view_schedule, pattern='^view_schedule$'),
                CallbackQueryHandler(my_reviews, pattern='^my_reviews$'),
            ],
            SELECTING_DOCTOR: [CallbackQueryHandler(select_doctor, pattern='^spec_')],
            SELECTING_TIME: [CallbackQueryHandler(show_schedule, pattern='^doc_')],
            BOOKING: [CallbackQueryHandler(book_appointment, pattern='^day_')],
            LEAVING_REVIEW: [CallbackQueryHandler(ask_for_review, pattern='^review_')],
            RECEIVING_REVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_review)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)


    application.run_polling()


if __name__ == "__main__":
    main()
