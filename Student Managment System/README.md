# Student Management System

This is a Student Management System developed as an academic project.  
The system manages student records and academic activities and can be adapted for other management systems such as employee, bank, or factory systems.

## Features
- Student registration using QR code
- Attendance management
- Assignment uploading
- Grade updating
- Class performance charts
- Student record management (add, view, update, delete)

## Technologies Used
- HTML, CSS, JavaScript
- Python (Flask)
- MySQL (via XAMPP)
- QR code generation
- Chart visualization (JavaScript charts)
- ngrok (for temporary public access during development)

## Database
- MySQL database hosted locally using XAMPP
- Flask connected to MySQL for CRUD operations

## How to Run the Project Locally

1. Install Python (3.x)
2. Install XAMPP and start:
   - Apache
   - MySQL
3. Create the database in phpMyAdmin and import your SQL file (if available)
4. Clone the repository:
   git clone https://github.com/USERNAME/REPO_NAME.git
5. Navigate to the project folder
6. Install dependencies:
   pip install -r requirements.txt
7. Run the Flask app:
   python app.py
8. Open browser:
   http://127.0.0.1:5000

## Demo
This project runs locally.  
During development and presentation, **ngrok** was used to expose the local server temporarily for demo purposes.

## Screenshots
Screenshots of the system (QR registration, attendance, assignments, grades, charts) are included in the repository for reference.

## Learning Outcomes
- Backend development with Flask
- MySQL database integration
- QR-based registration systems
- Data visualization using charts
- Understanding local hosting and tunneling tools

## Author
M. Haseeb
