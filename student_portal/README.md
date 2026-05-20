# Student Portal System

A full-featured academic management system built with Django, SQLite, Bootstrap 5.

## Project Structure

```
student_portal/
├── student_portal/         # Django project settings & root URLs
├── accounts/               # User auth: Student, Instructor, Admin models & views
├── core/                   # Landing pages, dashboards, admin views
├── enrollment/             # Enrollment form, subject selection, section assignment
├── grades/                 # Grade CRUD for instructors, grade view for students
├── attendance/             # Attendance CRUD for instructors, attendance view for students
├── schedules/              # Class schedule views
├── announcements/          # Announcement CRUD
├── templates/              # All HTML templates (Bootstrap 5)
├── static/
│   ├── css/portal.css      # Custom styles (blue theme, sidebar, cards)
│   └── js/portal.js        # Sidebar toggle, AJAX dept→program dropdown
└── db.sqlite3              # Auto-created on migrate
```

## Quick Start

### 1. Install dependencies
```bash
pip install django
```

### 2. Run migrations
```bash
cd student_portal
python manage.py migrate
```

### 3. Seed initial data (departments, programs, admin account)
```bash
python manage.py shell < seed.py
# OR run the seed commands from README manually
```

### 4. Start development server
```bash
python manage.py runserver
```

### 5. Access the system
- **Home:** http://127.0.0.1:8000/
- **Admin Login:** http://127.0.0.1:8000/accounts/admin/login/
  - Email: `admin@portal.edu`  |  Password: `admin1234`
- **Student Login:** http://127.0.0.1:8000/accounts/student/login/
- **Instructor Login:** http://127.0.0.1:8000/accounts/instructor/login/
- **Django Admin Panel:** http://127.0.0.1:8000/django-admin/

## Default Admin Credentials
| Field    | Value              |
|----------|--------------------|
| Email    | admin@portal.edu   |
| Password | admin1234          |

## User Workflows

### Student Flow
1. Register → Student Login → Landing Page
2. Fill Enrollment Form (personal info, educational background, guardian info, select subjects)
3. Wait for Admin Approval
4. Once approved → access Student Dashboard (GWA, schedule, attendance, grades, announcements)

### Instructor Flow
1. Register → Instructor Login → Dashboard
2. Admin assigns subjects to instructor
3. Instructor manages grades (CRUD) and attendance (CRUD)
4. Instructor can post announcements

### Admin Flow
1. Admin Login → Dashboard
2. Student Admin Panel: view enrollments, approve/reject, auto-section assignment (A→B→C)
3. Instructor Admin Panel: assign subjects to instructors, manage instructor loads

## Key Features Implemented
- ✅ Role-based authentication (Student / Instructor / Admin)
- ✅ Auto-filter programs by department (AJAX)
- ✅ Auto-filter subjects by department + program + year level
- ✅ Auto-sectioning on enrollment approval (A → B → C, first-come-first-serve)
- ✅ Dashboard access restriction (approved enrollment required)
- ✅ GWA auto-computation from grade components
- ✅ Attendance percentage per subject
- ✅ CSRF protection on all forms
- ✅ Hashed passwords (Django default)
- ✅ Unique Student ID and Faculty ID enforcement
- ✅ Print-ready enrollment copy and grade reports
- ✅ Responsive sidebar navigation (mobile toggle)
- ✅ Toast notification system for success/error messages

## Models Summary
| Model                | App          | Key Fields                                      |
|---------------------|--------------|-------------------------------------------------|
| User                | accounts     | role, email (custom AbstractUser)               |
| Department          | accounts     | name, code                                      |
| Program             | accounts     | name, code, department (FK)                     |
| StudentProfile      | accounts     | student_id (unique), department, program, year  |
| InstructorProfile   | accounts     | faculty_id (unique), position, year_handles     |
| Subject             | enrollment   | code, name, units, dept, program, year, instructor |
| Section             | enrollment   | name (A/B/C), max_slots, current_count          |
| Enrollment          | enrollment   | student, status, section, subjects (M2M)        |
| EducationalBackground | enrollment | primary/secondary/tertiary school fields        |
| Grade               | grades       | prelim/midterm/pre_final/final, final_grade     |
| Attendance          | attendance   | date, status (present/absent/late/excused)      |
| Schedule            | schedules    | subject, instructor, section, day, time         |
| Announcement        | announcements| title, content, audience, department            |
