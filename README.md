# Job Application Tracker

A Flask-based web application to track your job search progress, including applications, interviews, documents, and follow-up reminders.

## Features

- **Application Tracking**: Track job applications with company, role, status, and notes
- **Interview Management**: Log interviews with dates, types, and outcomes
- **Document Attachments**: Link resumes and cover letters to specific applications
- **Follow-up Reminders**: Set reminders to follow up on applications
- **Dashboard**: Overview of your job search with status breakdown and upcoming tasks

## Tech Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL (SQLite for local development)
- **Frontend**: Jinja2 templates + Tailwind CSS
- **Auth**: Flask-Login

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy sample.env to .env):
   ```bash
   cp sample.env .env
   ```

5. Run the application:
   ```bash
   python -m flask --app app.main run --debug
   ```

6. Open http://localhost:5000 in your browser

## Railway Deployment

1. Create a new project on [Railway](https://railway.app)
2. Add a PostgreSQL database
3. Connect your GitHub repository
4. Set environment variables:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: (automatically set by Railway PostgreSQL)

The app will automatically deploy using the `Procfile` and `railway.toml` configuration.

## Application Statuses

- **Saved**: Bookmarked, not yet applied
- **Applied**: Application submitted
- **Phone Screen**: Initial phone interview scheduled
- **Interviewing**: In active interview process
- **Final Round**: Final interview stage
- **Offer**: Received an offer
- **Rejected**: Application rejected
- **Withdrawn**: You withdrew from the process

## Project Structure

```
job_tracker/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── database.py          # SQLAlchemy setup
│   ├── main.py              # App entry point
│   ├── models/              # Database models
│   ├── routers/             # Route handlers
│   └── templates/           # Jinja2 templates
├── alembic/                 # Database migrations
├── requirements.txt
├── Procfile                 # Railway/Heroku deployment
└── railway.toml             # Railway configuration
```

## License

MIT

