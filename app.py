from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from config import Config
from models import db, User, LeaveRequest
from utils import analyze_leave_reason, send_notification
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', '')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            if role and user.role != role:
                flash("Role mismatch. Please select the correct role.", "danger")
                return redirect(url_for('login'))
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('dashboard'))
            elif user.role == 'tutor':
                return redirect(url_for('tutor_dashboard'))
            elif user.role == 'academic coordinator':
                return redirect(url_for('coordinator_dashboard'))
            elif user.role == 'hod':
                return redirect(url_for('hod_dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        new_user = User(username=username, password=password, role=role, attendance_percentage=100.0)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))
@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard - view own leave requests."""
    if current_user.role != 'student':
        return redirect(url_for('login'))
    my_requests = LeaveRequest.query.filter_by(student_id=current_user.id).all()
    return render_template('dashboard.html', my_requests=my_requests)

@app.route('/apply_leave', methods=['POST'])
@login_required
def apply_leave():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))

    
    if current_user.attendance_percentage < 75.0:
        flash("Your attendance is below 75%. You cannot submit a leave request.", "danger")
        return redirect(url_for('dashboard'))

    reason = request.form['reason']
    date = request.form['date']
    sentiment = analyze_leave_reason(reason)
    leave_request = LeaveRequest(
        student_id=current_user.id,
        reason=reason,
        date=date,
        status='Submitted'
    )
    db.session.add(leave_request)
    db.session.commit()

    flash(f"Leave request submitted. Sentiment: {sentiment}", "success")
    return redirect(url_for('dashboard'))
@app.route('/tutor_dashboard', methods=['GET','POST'])
@login_required
def tutor_dashboard():
    """Tutor sees all requests with status 'Submitted'."""
    if current_user.role != 'tutor':
        return redirect(url_for('login'))

    if request.method == 'POST':
        leave_id = request.form.get('leave_id')
        action = request.form.get('action')
        leave_req = LeaveRequest.query.get(leave_id)
        if leave_req and leave_req.status == 'Submitted':
            if action == 'approve':
                leave_req.status = 'Tutor Approved'
            elif action == 'decline':
                leave_req.status = 'Tutor Declined'
            db.session.commit()
    leave_requests = LeaveRequest.query.filter_by(status='Submitted').all()
    return render_template('tutor_dashboard.html', leave_requests=leave_requests)
@app.route('/coordinator_dashboard', methods=['GET','POST'])
@login_required
def coordinator_dashboard():
    """Coordinator sees all requests that are 'Tutor Approved'."""
    if current_user.role != 'academic coordinator':
        return redirect(url_for('login'))

    if request.method == 'POST':
        leave_id = request.form.get('leave_id')
        action = request.form.get('action')
        leave_req = LeaveRequest.query.get(leave_id)
        if leave_req and leave_req.status == 'Tutor Approved':
            if action == 'approve':
                leave_req.status = 'Coordinator Approved'
                # Possibly notify next role (HOD)
            elif action == 'decline':
                leave_req.status = 'Coordinator Declined'
                # Notify student
            db.session.commit()

    # Show only 'Tutor Approved' requests
    leave_requests = LeaveRequest.query.filter_by(status='Tutor Approved').all()
    return render_template('coordinator_dashboard.html', leave_requests=leave_requests)

# -------------------- HOD ROUTES -------------------- #
@app.route('/hod_dashboard', methods=['GET','POST'])
@login_required
def hod_dashboard():
    """HOD sees all requests that are 'Coordinator Approved'."""
    if current_user.role != 'hod':
        return redirect(url_for('login'))

    if request.method == 'POST':
        leave_id = request.form.get('leave_id')
        action = request.form.get('action')
        leave_req = LeaveRequest.query.get(leave_id)
        if leave_req and leave_req.status == 'Coordinator Approved':
            if action == 'approve':
                leave_req.status = 'HOD Approved'
                # Notify student of final approval
            elif action == 'decline':
                leave_req.status = 'HOD Declined'
                # Notify student of decline
            db.session.commit()
    leave_requests = LeaveRequest.query.filter_by(status='Coordinator Approved').all()
    return render_template('hod_dashboard.html', leave_requests=leave_requests)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Check if a HOD account exists; if not, create one
        if not User.query.filter_by(role='hod').first():
            default_hod = User(
                username='hoduser', 
                password='123456', 
                role='hod', 
                attendance_percentage=100.0
            )
            db.session.add(default_hod)
            db.session.commit()
            print("Default HOD account created: hoduser / hodpass")
    app.run(debug=True)
