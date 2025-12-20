**EduBuddy Telegram Bot**

EduBuddy is a multilingual Telegram bot designed to improve communication between students and teachers by providing quick access to academic information and automated support.

⸻

**Key Features**
	•	Multilingual support (Russian 🇷🇺 / Kazakh 🇰🇿)
	•	Role-based access (Student / Teacher)
	•	Secure login & password authentication
	•	View schedules, grades, and homework
	•	Teacher grade management
	•	FAQ system with AI fallback
	•	AI answers in user-selected language
	•	In-bot settings (change login & password)
	•	PostgreSQL database
	•	Daily automated backups (cron)

⸻

**Tech Stack**
	•	Python 3.12
	•	PostgreSQL
	•	python-telegram-bot
	•	psycopg2
	•	Bash & Cron

**Run Locally**

	pipenv shell
	pipenv install requirements.txt
	python -m bot.main
	python -m admin.main 
