# Doctor Appointment Bot

This is a Telegram bot that allows users to book appointments with doctors.

## Features

- User onboarding and registration
- Specialty and doctor selection
- Appointment booking
- Appointment overview
- Review system
- User roles (patient and doctor)

## Project Structure

- `bot.py`: Main bot logic
- `models.py`: SQLAlchemy models
- `database.py`: Database session and initialization
- `config.py`: Configuration for bot token and database URI
- `seed_db.py`: Script to populate the database with sample data
- `__init__.py`: Package support

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**
    A `requirements.txt` file is not provided. You will need to install the following dependencies:
    - `python-telegram-bot`
    - `sqlalchemy`

3.  **Set up the environment variables:**
    Create a `.env` file in the root directory and add the following:
    ```
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    DATABASE_URI="sqlite:///./test.db"
    ```

4.  **Seed the database:**
    ```bash
    python seed_db.py
    ```

5.  **Run the bot:**
    ```bash
    python bot.py
    ```

## Usage

- Start the bot by sending the `/start` command.
- Follow the on-screen instructions to book an appointment.
- Use the `/menu` command to return to the main menu at any time.
- Use the `/cancel` command to exit the current flow.