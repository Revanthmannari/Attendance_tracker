# 🎓 Advanced Attendance Management System

A modern, feature-rich attendance management system built with Python Flask, featuring secret code-based attendance, student self-registration, analytics, and comprehensive reporting.

## ✨ Features

### 🔐 Authentication & User Management
- **Student Self-Signup**: Students can create their own accounts
- **Faculty Manual Addition**: Faculty can manually add students
- **Profile Management**: Students can update their passwords
- **Secure Login**: Role-based access control

### 📊 Attendance System
- **Secret Code of the Day**: 6-character alphanumeric codes valid for 2 minutes
- **Real-time Validation**: Instant feedback on attendance submission
- **Duplicate Prevention**: One attendance record per student per day
- **Case-insensitive**: Codes work in any case (upper/lower)

### 📈 Analytics & Reporting
- **Real-time Statistics**: Total students, attendance records, present count, attendance rate
- **Daily Attendance Charts**: Visual representation of last 7 days
- **Top Students Ranking**: Best attendance performers
- **CSV Export**: Download attendance reports for external analysis

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Clean Interface**: Modern, intuitive user experience
- **Visual Feedback**: Success/error messages and loading states
- **Professional Styling**: Beautiful gradients and card-based layout

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   cd AttendanceApp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to: `http://localhost:5000`

## 👥 User Guide

### For Faculty

#### 1. **Login**
- Username: `faculty`
- Password: `password`

#### 2. **Generate Attendance Codes**
- Click "Generate New Code" button
- Share the 6-character code with students
- Codes expire after 2 minutes for security

#### 3. **Manage Students**
- **Add Students**: Use "Add New Student" to manually create accounts
- **View Reports**: See all attendance records in the dashboard
- **Analytics**: Access detailed statistics and charts
- **Export Data**: Download CSV reports for external analysis

#### 4. **View Analytics**
- **Overview Stats**: Total students, attendance records, rates
- **Daily Trends**: Last 7 days attendance visualization
- **Top Performers**: Students with best attendance records

### For Students

#### 1. **Create Account**
- Click "Sign up here" on the login page
- Choose a username and password
- Confirm your password

#### 2. **Mark Attendance**
- Login with your credentials
- Enter the code provided by faculty
- Submit to mark your attendance
- View your attendance history and statistics

#### 3. **Manage Profile**
- Update your password
- View account information
- Track your attendance performance

## 📁 Project Structure

```
AttendanceApp/
├── app.py                 # Main Flask application
├── schema.sql            # Database schema
├── database.db           # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   └── style.css        # CSS styles
└── templates/
    ├── layout.html      # Base template
    ├── login.html       # Login page
    ├── signup.html      # Student signup
    ├── faculty_dashboard.html    # Faculty dashboard
    ├── student_dashboard.html    # Student dashboard
    ├── student_profile.html      # Student profile management
    ├── add_student.html          # Add student form
    └── analytics.html            # Analytics dashboard
```

## 🔧 Configuration

### Database
- **SQLite**: Lightweight, file-based database
- **Auto-creation**: Database and tables created automatically on first run
- **Schema**: Users and attendance tables with proper relationships

### Security Features
- **Session Management**: Secure user sessions
- **Role-based Access**: Faculty and student permissions
- **Input Validation**: Form validation and sanitization
- **Code Expiration**: Time-limited attendance codes

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users (id)
);
```

## 🎯 Key Features Explained

### Secret Code System
- **Generation**: Random 6-character alphanumeric codes
- **Validation**: Server-side verification with timestamp checking
- **Security**: 2-minute expiration prevents code reuse
- **User-friendly**: Case-insensitive input

### Analytics Dashboard
- **Real-time Data**: Live statistics from database
- **Visual Charts**: Progress bars for daily attendance
- **Performance Tracking**: Student ranking by attendance
- **Export Capability**: CSV download for external analysis

### Student Management
- **Dual Registration**: Both self-signup and faculty addition
- **Profile Control**: Students can manage their accounts
- **Attendance History**: Complete record of attendance
- **Statistics**: Personal attendance performance metrics

## 🔄 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - Student registration
- `GET /logout` - User logout

### Faculty Features
- `GET /faculty/dashboard` - Faculty dashboard
- `GET /faculty/add_student` - Add student page
- `POST /faculty/add_student` - Create student account
- `GET /faculty/analytics` - Analytics dashboard
- `GET /faculty/export_report` - Export CSV report
- `GET /api/generate_code` - Generate attendance code

### Student Features
- `GET /student/dashboard` - Student dashboard
- `GET /student/profile` - Profile management
- `POST /student/profile` - Update profile
- `POST /api/mark_attendance` - Submit attendance code

## 🛠️ Development

### Adding New Features
1. Add routes in `app.py`
2. Create templates in `templates/` directory
3. Update CSS in `static/style.css`
4. Test thoroughly

### Database Modifications
1. Update `schema.sql` with new table definitions
2. Modify database initialization in `app.py`
3. Handle data migration if needed

## 🚀 Deployment

### Production Considerations
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up proper environment variables
- Configure a production database (PostgreSQL, MySQL)
- Enable HTTPS
- Set up proper logging

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the documentation
2. Review the code comments
3. Create an issue in the repository

---

**Built with ❤️ using Python Flask**