# 🧮 Tax Calculator Lead Generation App

A Flask-based web application that collects user information and automatically sends a tax calculator spreadsheet via email while storing leads in Google Sheets.

## 📁 Project Structure

```
tax-calculator-app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in repo)
├── .gitignore            # Git ignore rules
├── credentials.json      # Google Service Account credentials (not in repo)
├── tax_calculator.xlsx   # Excel file sent to users
├── README.md            # Project documentation
├── static/
│   ├── css/
│   │   └── styles.css   # Application styles
│   ├── js/
│   │   └── script.js    # Frontend JavaScript
│   └── images/
│       └── favicon.png  # Site favicon
└── templates/
    └── index.html       # Main HTML template
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd tax-calculator-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
EMAIL_ADDRESS=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-specific-password
GOOGLE_SHEETS_ID=your-google-sheets-id
```

**Important**:

- Use Gmail App Password, not your regular password
- Get Google Sheets ID from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### 4. Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account and download the JSON credentials
5. Rename the file to `credentials.json` and place in project root
6. Share your Google Sheet with the service account email

### 5. Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings → Security → App passwords
3. Generate a new app password for "Mail"
4. Use this password in your `.env` file

### 6. Add Tax Calculator File

Place your Excel tax calculator file as `tax_calculator.xlsx` in the project root.

## 🚀 Running the Application

### Development Mode

```bash
python3 app.py
```

The application will be available at `http://localhost:5500`

### Production Deployment

For production deployment, consider using:

- **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
- **Docker**: Create a Dockerfile for containerization
- **Cloud Platforms**: Deploy to Heroku, Railway, or DigitalOcean