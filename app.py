from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from celery import Celery
from celery.schedules import crontab
from flask_mail import Mail, Message
import os
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///examportal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
CORS(app)
app.config["JWT_SECRET_KEY"] = "my-secret-key"

jwt = JWTManager(app)

# ---------- Celery + Redis ----------
def setup_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/0",
    )
    celery_app.conf.update(flask_app.config)
    celery_app.conf.timezone = "Asia/Kolkata"
    celery_app.conf.enable_utc = False
    celery_app.conf.beat_schedule = {
        # Daily examination reminder at 9:00 AM
        "daily-examination-reminder": {
            "task": "app.push_exam_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
        # Monthly examination report on the 1st at 9:00 AM
        "monthly-examination-report": {
            "task": "app.push_monthly_report",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),
        },
    }

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


celery = setup_celery(app)

# ---------- Email (Flask-Mail) ----------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "lazyiitians17@gmail.com")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
)
mail = Mail(app)

# Optional Google Chat webhook (set GOOGLE_CHAT_WEBHOOK env var)
GOOGLE_CHAT_WEBHOOK = os.environ.get("GOOGLE_CHAT_WEBHOOK", "")


def send_google_chat(text):
    if not GOOGLE_CHAT_WEBHOOK:
        return False
    try:
        response = requests.post(
            GOOGLE_CHAT_WEBHOOK,
            json={"text": text},
            timeout=10,
        )
        return response.ok
    except Exception:
        return False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    bookings = db.relationship("Booking", back_populates="student")
    examiner_profile = db.relationship(
        "ExaminerProfile", back_populates="user", uselist=False
    )
    student_profile = db.relationship(
        "StudentProfile", back_populates="user", uselist=False
    )
    examination_slots = db.relationship(
        "ExaminationSlot",
        back_populates="examiner",
        foreign_keys="ExaminationSlot.examiner_id"
    )
    evaluations = db.relationship(
        "Evaluation",
        back_populates="examiner",
        foreign_keys="Evaluation.examiner_id"
    )

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active")

    examinations = db.relationship("Examination", back_populates="course")


class Examination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    exam_name = db.Column(db.String(100))
    exam_type = db.Column(db.String(50))
    slot_start_date = db.Column(db.String(30))
    slot_end_date = db.Column(db.String(30))
    booking_start_time = db.Column(db.String(30))
    booking_end_time = db.Column(db.String(30))
    exam_start_time = db.Column(db.String(30))
    exam_end_time = db.Column(db.String(30))
    examiner_slot_creation_open = db.Column(db.Boolean, default=False)
    student_booking_open = db.Column(db.Boolean, default=False)
    results_published = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(30), default="Draft")

    course = db.relationship("Course", back_populates="examinations")
    rubrics = db.relationship("ExaminationRubric", back_populates="examination")
    slots = db.relationship("ExaminationSlot", back_populates="examination")


class ExaminationRubric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(
        db.Integer, db.ForeignKey("examination.id"), nullable=False
    )
    criterion_name = db.Column(db.String(100), nullable=False)
    maximum_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float, default=0)
    description = db.Column(db.Text)

    examination = db.relationship("Examination", back_populates="rubrics")


class ExaminerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )
    address = db.Column(db.String(200))
    past_experience = db.Column(db.String(500))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Active")

    user = db.relationship("User", back_populates="examiner_profile")

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    past_experience = db.Column(db.String(500))

    user = db.relationship(
        "User",
        back_populates="student_profile"
    )


class ExaminationSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(
        db.Integer, db.ForeignKey("examination.id"), nullable=False
    )
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Available")
    meeting_link = db.Column(db.String(300))

    examination = db.relationship("Examination", back_populates="slots")
    examiner = db.relationship(
        "User", back_populates="examination_slots", foreign_keys=[examiner_id]
    )
    bookings = db.relationship("Booking", back_populates="slot")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    slot_id = db.Column(
        db.Integer, db.ForeignKey("examination_slot.id"), nullable=False
    )
    booking_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="Booked")

    student = db.relationship("User", back_populates="bookings")
    slot = db.relationship("ExaminationSlot", back_populates="bookings")
    evaluation = db.relationship("Evaluation", back_populates="booking", uselist=False)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("booking.id"), unique=True, nullable=False
    )
    examiner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_marks = db.Column(db.Float, default=0)
    marks = db.Column(db.Text)
    remarks = db.Column(db.Text)
    evaluation_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")

    booking = db.relationship("Booking", back_populates="evaluation")
    examiner = db.relationship(
        "User", back_populates="evaluations", foreign_keys=[examiner_id]
    )


# ---------- Celery scheduled jobs ----------

@celery.task(name="app.push_exam_reminders")
def push_exam_reminders():
    """Daily examination reminder – email / Google Chat for today's booked slots."""
    sent = 0
    today = date.today()

    bookings = Booking.query.filter_by(status="Booked").all()
    for booking in bookings:
        slot = ExaminationSlot.query.filter_by(id=booking.slot_id).first()
        if not slot or slot.date != today:
            continue

        student = User.query.filter_by(id=booking.student_id).first()
        exam = Examination.query.filter_by(id=slot.examination_id).first()
        if not student or not student.email or not exam:
            continue

        examiner = User.query.filter_by(id=slot.examiner_id).first()
        if not examiner and exam.examiner_id:
            examiner = User.query.filter_by(id=exam.examiner_id).first()

        instructions = (
            f"Exam type: {exam.exam_type or 'N/A'}. "
            f"Please join on time"
            + (f" using this meeting link: {slot.meeting_link}" if slot.meeting_link else ".")
        )

        body = (
            f"Hi {student.name},\n\n"
            f"This is a reminder for your upcoming examination.\n\n"
            f"Examination name: {exam.exam_name}\n"
            f"Date and time: {slot.date} {slot.start_time} - {slot.end_time}\n"
            f"Assigned examiner: {examiner.name if examiner else 'Not assigned'}\n"
            f"Examination instructions: {instructions}\n\n"
            f"Regards,\nExam Portal"
        )

        # Email reminder
        try:
            msg = Message(
                subject=f"Reminder: {exam.exam_name}",
                recipients=[student.email],
                body=body,
            )
            mail.send(msg)
            sent += 1
        except Exception as exc:
            print(f"Email reminder failed for {student.email}: {exc}")

        # Optional Google Chat webhook
        send_google_chat(
            f"*Exam Reminder*\n"
            f"Student: {student.name}\n"
            f"Examination: {exam.exam_name}\n"
            f"Date/Time: {slot.date} {slot.start_time} - {slot.end_time}\n"
            f"Examiner: {examiner.name if examiner else 'Not assigned'}\n"
            f"Instructions: {instructions}"
        )

    return f"Sent {sent} examination reminder(s)"


@celery.task(name="app.push_monthly_report")
def push_monthly_report():
    """Monthly HTML examination report emailed to Admin on the 1st of each month."""
    today = date.today()
    if today.month == 1:
        year, month = today.year - 1, 12
    else:
        year, month = today.year, today.month - 1

    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    # Examinations conducted in the previous month (by exam window / slot dates)
    exams = Examination.query.filter(
        Examination.status.in_(["Closed", "Completed", "Active", "Published"])
    ).all()
    exams_conducted = []
    for exam in exams:
        has_slot_in_month = ExaminationSlot.query.filter(
            ExaminationSlot.examination_id == exam.id,
            ExaminationSlot.date >= month_start,
            ExaminationSlot.date < month_end,
        ).first()
        if has_slot_in_month or exam.status in ("Closed", "Completed"):
            exams_conducted.append(exam)

    bookings = Booking.query.filter(
        Booking.booking_date >= datetime.combine(month_start, datetime.min.time()),
        Booking.booking_date < datetime.combine(month_end, datetime.min.time()),
    ).all()
    # Fall back to all bookings if none fall in the window (demo-friendly)
    if not bookings:
        bookings = Booking.query.all()

    evaluations = Evaluation.query.filter(
        Evaluation.status == "Submitted"
    ).all()
    month_evaluations = [
        e for e in evaluations
        if e.evaluation_date
        and month_start <= e.evaluation_date.date() < month_end
    ]
    if not month_evaluations:
        month_evaluations = evaluations

    evaluated_students = set()
    evaluated_booking_ids = set()
    for item in month_evaluations:
        evaluated_booking_ids.add(item.booking_id)
        booking = Booking.query.filter_by(id=item.booking_id).first()
        if booking:
            evaluated_students.add(booking.student_id)

    completed_bookings = [
        item for item in bookings if item.id in evaluated_booking_ids
    ]
    pending = [
        item
        for item in Booking.query.filter_by(status="Booked").all()
        if item.id not in evaluated_booking_ids
        and (
            not item.evaluation
            or item.evaluation.status == "Pending"
        )
    ]

    examiner_counts = {}
    for item in month_evaluations:
        examiner_counts[item.examiner_id] = examiner_counts.get(item.examiner_id, 0) + 1
    active = sorted(examiner_counts.items(), key=lambda pair: pair[1], reverse=True)[:5]

    if active:
        rows = ""
        for examiner_id, count in active:
            examiner = User.query.filter_by(id=examiner_id).first()
            name = examiner.name if examiner else "Unknown"
            rows += f"<li>{name} — {count} evaluation(s)</li>"
    else:
        rows = "<li>No evaluations yet</li>"

    report_month = month_start.strftime("%B %Y")
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #222;">
      <h2>Monthly Examination Report — {report_month}</h2>
      <p>Automated report generated by Exam Portal.</p>
      <ul>
        <li><strong>Examinations conducted:</strong> {len(exams_conducted)}</li>
        <li><strong>Students evaluated:</strong> {len(evaluated_students)}</li>
        <li><strong>Completed bookings:</strong> {len(completed_bookings)}</li>
        <li><strong>Pending evaluations:</strong> {len(pending)}</li>
      </ul>
      <h3>Most active examiners</h3>
      <ul>{rows}</ul>
    </body>
    </html>
    """

    admins = User.query.filter_by(role="Admin").all()
    sent = 0
    for admin in admins:
        if not admin.email:
            continue
        try:
            msg = Message(
                subject=f"Monthly Examination Report — {report_month}",
                recipients=[admin.email],
                html=html_body,
            )
            mail.send(msg)
            sent += 1
        except Exception as exc:
            print(f"Monthly report email failed for {admin.email}: {exc}")

    send_google_chat(
        f"*Monthly Examination Report — {report_month}*\n"
        f"Examinations conducted: {len(exams_conducted)}\n"
        f"Students evaluated: {len(evaluated_students)}\n"
        f"Completed bookings: {len(completed_bookings)}\n"
        f"Pending evaluations: {len(pending)}"
    )

    return f"Monthly report sent to {sent} admin(s)"


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Please fill all fields"})

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({"message": "Email already exists"})

    password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password=password,
        role="Student"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"message": "User not found"})

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Wrong password"})

    if user.is_blocked:
        return jsonify({"message": "Your account is blocked"})

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    if user.role == "Admin":
        dashboard = "/admin/dashboard"

    elif user.role == "Examiner":
        dashboard = "/examiner/dashboard"

    else:
        dashboard = "/student/dashboard"

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "role": user.role,
        "dashboard": dashboard
    })


@app.route("/admin/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    total_courses = Course.query.count()
    total_examinations = Examination.query.count()
    total_examiners = User.query.filter_by(role="Examiner").count()
    total_students = User.query.filter_by(role="Student").count()
    total_slots = ExaminationSlot.query.count()
    total_bookings = Booking.query.count()

    return jsonify(
        {
            "total_courses": total_courses,
            "total_examinations": total_examinations,
            "total_examiners": total_examiners,
            "total_students": total_students,
            "total_slots": total_slots,
            "total_bookings": total_bookings,
        }
    )
    
@app.route("/createcourse", methods=["POST"])
@jwt_required()
def create_course():
    user_role = get_jwt()
    
    if user_role.get("role") != "Admin":
            return jsonify({"message": "Access denied"})

    data = request.get_json()

    course_code = data.get("course_code")
    course_name = data.get("course_name")
    department = data.get("department")
    credit = data.get("credit")
    description = data.get("description")
    status = data.get("status")

    if not course_code or not course_name or not department or not credit or not description:
        return jsonify({"message": "Please fill all fields"})

    existing_course = Course.query.filter_by(course_code=course_code).first()

    if existing_course:
        return jsonify({"message": "Course code already exists"})

    course = Course(
        course_code=course_code,
        course_name=course_name,
        department=department,
        credit=credit,
        description=description,
        status=status
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({"message": "Course created successfully"})

@app.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():

    courses = Course.query.all()

    course_list = []

    for course in courses:
        course_list.append({
            "id": course.id,
            "course_code": course.course_code,
            "course_name": course.course_name,
            "department": course.department,
            "description": course.description,
            "credit": course.credit,
            "status": course.status
        })

    return jsonify(course_list)

@app.route("/editcourse/<int:id>", methods=["GET"])
@jwt_required()
def get_course(id):

    course = Course.query.get(id)

    if course is None:
        return jsonify({"message": "Course not found"})

    return jsonify({
        "id": course.id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "department": course.department,
        "credit": course.credit,
        "description": course.description,
        "status": course.status
    })
    
@app.route("/editcourse/<int:id>", methods=["POST"])
@jwt_required()
def update_course(id):

    course = Course.query.get(id)

    if course is None:
        return jsonify({"message": "Course not found"})

    data = request.get_json()

    course_code = data.get("course_code")
    course_name = data.get("course_name")
    department = data.get("department")
    credit = data.get("credit")
    description = data.get("description")
    status = data.get("status")

    if not course_code or not course_name or not department or not credit or not description:
        return jsonify({"message": "Please fill all fields"})

    existing_course = Course.query.filter(
        Course.course_code == course_code,
        Course.id != id
    ).first()

    if existing_course:
        return jsonify({"message": "Course code already exists"})

    course.course_code = course_code
    course.course_name = course_name
    course.department = department
    course.credit = credit
    course.description = description
    course.status = status

    db.session.commit()

    return jsonify({"message": "Course updated successfully"})

@app.route("/courses/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_course(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    course = Course.query.get(id)

    if course is None:
        return jsonify({"message": "Course not found"})

    db.session.delete(course)
    db.session.commit()

    return jsonify({"message": "Course deleted successfully"})


@app.route("/createexamination", methods=["POST"])
@jwt_required()
def create_examination():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    data = request.get_json()

    course_id = data.get("course_id")
    examiner_id = data.get("examinor_id")
    exam_name = data.get("exam_name")

    slot_start_date = data.get("slot_start_date")
    slot_end_date = data.get("slot_end_date")

    booking_start_time = data.get("booking_start_time")
    booking_end_time = data.get("booking_end_time")

    exam_start_time = data.get("exam_start_time")
    exam_end_time = data.get("exam_end_time")

    if not all([
        course_id, examiner_id, exam_name,
        slot_start_date, slot_end_date,
        booking_start_time, booking_end_time,
        exam_start_time, exam_end_time
    ]):
        return jsonify({"message": "Please fill all fields"})

    try:
        slot_start = date.fromisoformat(slot_start_date)
        slot_end = date.fromisoformat(slot_end_date)

        booking_start = datetime.fromisoformat(booking_start_time)
        booking_end = datetime.fromisoformat(booking_end_time)

        exam_start = date.fromisoformat(exam_start_time)
        exam_end = date.fromisoformat(exam_end_time)

    except ValueError:
        return jsonify({"message": "Invalid date or time format"})

    if slot_start < date.today():
        return jsonify({"message": "Slot start date cannot be before today"})

    if slot_end < slot_start:
        return jsonify({"message": "Slot end date must be after slot start date"})

    if booking_start.date() <= slot_end:
        return jsonify({"message": "Booking start date must be after slot end date"})

    if booking_end.date() <= slot_end:
        return jsonify({"message": "Booking end date must be after slot end date"})

    if booking_end < booking_start:
        return jsonify({"message": "Booking end time must be after booking start time"})

    if exam_start <= booking_end.date():
        return jsonify({"message": "Exam start date must be after booking end date"})

    if exam_end <= booking_end.date():
        return jsonify({"message": "Exam end date must be after booking end date"})

    if exam_end < exam_start:
        return jsonify({"message": "Exam end date must be after exam start date"})

    course = Course.query.get(course_id)

    examiner = User.query.filter_by(
        id=examiner_id,
        role="Examiner"
    ).first()

    if course is None:
        return jsonify({"message": "Course not found"})

    if examiner is None:
        return jsonify({"message": "Examiner not found"})

    examination = Examination(
        course_id=course_id,
        examiner_id=examiner_id,
        exam_name=exam_name,
        exam_type="General",
        slot_start_date=slot_start_date,
        slot_end_date=slot_end_date,
        booking_start_time=booking_start_time,
        booking_end_time=booking_end_time,
        exam_start_time=exam_start_time,
        exam_end_time=exam_end_time
    )

    db.session.add(examination)
    db.session.commit()

    return jsonify({
        "message": "Examination created successfully"
    })
@app.route('/admin/create-examiner', methods=['POST'])
@jwt_required()
def create_examiner():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Please fill all fields"})

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email already exists"})

    password = generate_password_hash(password)

    new_examiner = User(
        name=username,
        email=email,
        password=password,
        role="Examiner"
    )

    db.session.add(new_examiner)
    db.session.commit()

    return jsonify({"message": "Examiner registered successfully"})

@app.route("/provide_examinor_details", methods=["GET"])
@jwt_required()
def provide_examinor_details():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examiners = User.query.filter_by(role="Examiner").all()

    examiner_list = []

    for examiner in examiners:
        examiner_list.append({
            "id": examiner.id,
            "name": examiner.name,
            "email": examiner.email,
            "role": examiner.role,
            "is_blocked": examiner.is_blocked
        })

    return jsonify({
        "data": examiner_list
    })


@app.route("/block_examinor/<int:id>", methods=["POST"])
@jwt_required()
def block_examinor(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examiner = User.query.filter_by(
        id=id,
        role="Examiner"
    ).first()

    if examiner is None:
        return jsonify({"message": "Examiner not found"})

    examiner.is_blocked = True

    db.session.commit()

    return jsonify({
        "message": "Examiner blocked successfully"
    })


@app.route("/unblock_examinor/<int:id>", methods=["POST"])
@jwt_required()
def unblock_examinor(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examiner = User.query.filter_by(
        id=id,
        role="Examiner"
    ).first()

    if examiner is None:
        return jsonify({"message": "Examiner not found"})

    examiner.is_blocked = False

    db.session.commit()

    return jsonify({
        "message": "Examiner unblocked successfully"
    })
    

@app.route('/provide_examination_details', methods=['GET'])
@jwt_required()
def provide_examination_details():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    all_examinations = Examination.query.all()

    all_examinations_list = []

    for examination in all_examinations:
        all_examinations_list.append({
            "id": examination.id,
            "name": examination.exam_name,
            "slot_start_date": examination.slot_start_date,
            "slot_end_date": examination.slot_end_date,
            "booking_start_time": examination.booking_start_time,
            "booking_end_time": examination.booking_end_time,
            "exam_start_date": examination.exam_start_time,
            "exam_end_date": examination.exam_end_time,
            "course_id": examination.course_id,
            "examiner_id": examination.examiner_id,
            "status": examination.status,
            "slot_open": examination.examiner_slot_creation_open,
            "booking_open": examination.student_booking_open,
            "results_published": examination.results_published
        })

    return jsonify({"data": all_examinations_list})


@app.route("/admin/edit-examination/<int:id>", methods=["PUT"])
@jwt_required()
def edit_examination(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if not examination:
        return jsonify({"message": "Examination not found"})

    data = request.json

    examination.exam_name = data["exam_name"]
    examination.exam_type = data["exam_type"]
    examination.slot_start_date = data["slot_start_date"]
    examination.slot_end_date = data["slot_end_date"]
    examination.booking_start_time = data["booking_start_time"]
    examination.booking_end_time = data["booking_end_time"]
    examination.exam_start_time = data["exam_start_time"]
    examination.exam_end_time = data["exam_end_time"]

    db.session.commit()

    return jsonify({"message": "Examination updated"})

@app.route('/admin/evaluations', methods=['GET'])
@jwt_required()
def admin_evaluations():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    all_evaluations = Evaluation.query.filter_by(status="Submitted").all()

    evaluations_list = []

    for evaluation in all_evaluations:
        evaluations_list.append({
            "id": evaluation.id,
            "student_name": evaluation.booking.student.name,
            "student_email": evaluation.booking.student.email,
            "exam_name": evaluation.booking.slot.examination.exam_name,
            "exam_id": evaluation.booking.slot.examination.id,
            "total_marks": evaluation.total_marks,
            "remarks": evaluation.remarks,
            "evaluation_date": evaluation.evaluation_date.strftime("%Y-%m-%d") if evaluation.evaluation_date else "",
            "results_published": evaluation.booking.slot.examination.results_published
        })

    return jsonify({"data": evaluations_list})
@app.route('/admin/evaluation-details/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def admin_evaluation_details(evaluation_id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    import json
    import ast

    evaluation = Evaluation.query.get(evaluation_id)

    if not evaluation:
        return jsonify({"message": "Evaluation not found"})

    marks_data = []

    if evaluation.marks:
        try:
            marks_data = json.loads(evaluation.marks)
        except:
            marks_data = ast.literal_eval(evaluation.marks)

    rubric_data = []

    for item in marks_data:
        rubric = ExaminationRubric.query.get(item["rubric_id"])

        if rubric:
            rubric_data.append({
                "criterion_name": rubric.criterion_name,
                "maximum_marks": rubric.maximum_marks,
                "weightage": rubric.weightage,
                "marks_obtained": item["marks"]
            })

    return jsonify({
        "student_name": evaluation.booking.student.name,
        "student_email": evaluation.booking.student.email,
        "exam_name": evaluation.booking.slot.examination.exam_name,
        "total_marks": evaluation.total_marks,
        "remarks": evaluation.remarks,
        "rubrics": rubric_data
    })

@app.route("/admin/publish-result/<int:id>", methods=["POST"])
@jwt_required()
def publish_result(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if not examination:
        return jsonify({"message": "Examination not found"})

    bookings = Booking.query.join(ExaminationSlot).filter(
        ExaminationSlot.examination_id == id,
        Booking.status == "Booked"
    ).all()

    if not bookings:
        return jsonify({"message": "No students have booked this examination"})

    for booking in bookings:

        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id,
            status="Submitted"
        ).first()

        if not evaluation:
            return jsonify({
                "message": "All students' evaluations are not completed yet"
            })

    examination.results_published = True
    examination.status = "Completed"
    examination.examiner_slot_creation_open = False
    examination.student_booking_open = False

    db.session.commit()

    return jsonify({"message": "Result published successfully"})


@app.route("/admin/create-rubric", methods=["POST"])
@jwt_required()
def create_rubric():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    data = request.get_json()

    examination_id = data.get("examination_id")
    criterion_name = data.get("criterion_name")
    maximum_marks = data.get("maximum_marks")
    weightage = data.get("weightage", 0)
    description = data.get("description")

    if not examination_id or not criterion_name or maximum_marks is None:
        return jsonify({"message": "Please fill all required fields"})

    examination = Examination.query.get(examination_id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    try:
        maximum_marks = float(maximum_marks)
        weightage = float(weightage)
    except (ValueError, TypeError):
        return jsonify({"message": "Enter valid marks and weightage"})

    if maximum_marks <= 0 or weightage < 0:
        return jsonify({"message": "Enter valid marks and weightage"})

    rubric = ExaminationRubric(
        examination_id=examination_id,
        criterion_name=criterion_name,
        maximum_marks=maximum_marks,
        weightage=weightage,
        description=description
    )

    db.session.add(rubric)
    db.session.commit()

    return jsonify({"message": "Rubric created successfully"})

@app.route("/admin/rubrics/<int:examination_id>", methods=["GET"])
@jwt_required()
def get_rubrics(examination_id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(examination_id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    rubrics = ExaminationRubric.query.filter_by(
        examination_id=examination_id
    ).all()

    rubric_list = []

    for rubric in rubrics:
        rubric_list.append({
            "id": rubric.id,
            "examination_id": rubric.examination_id,
            "criterion_name": rubric.criterion_name,
            "maximum_marks": rubric.maximum_marks,
            "weightage": rubric.weightage,
            "description": rubric.description
        })

    return jsonify(rubric_list)

@app.route("/admin/edit-rubric/<int:id>", methods=["PUT"])
@jwt_required()
def edit_rubric(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    rubric = ExaminationRubric.query.get(id)

    if rubric is None:
        return jsonify({"message": "Rubric not found"})

    data = request.get_json()

    criterion_name = data.get("criterion_name")
    maximum_marks = data.get("maximum_marks")
    weightage = data.get("weightage", 0)
    description = data.get("description")

    if not criterion_name or maximum_marks is None:
        return jsonify({"message": "Please fill all required fields"})

    try:
        maximum_marks = float(maximum_marks)
        weightage = float(weightage)
    except (ValueError, TypeError):
        return jsonify({"message": "Enter valid marks and weightage"})

    if maximum_marks <= 0 or weightage < 0:
        return jsonify({"message": "Enter valid marks and weightage"})

    rubric.criterion_name = criterion_name
    rubric.maximum_marks = maximum_marks
    rubric.weightage = weightage
    rubric.description = description

    db.session.commit()

    return jsonify({"message": "Rubric updated successfully"})

@app.route("/admin/delete-rubric/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_rubric(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    rubric = ExaminationRubric.query.get(id)

    if rubric is None:
        return jsonify({"message": "Rubric not found"})

    db.session.delete(rubric)
    db.session.commit()

    return jsonify({"message": "Rubric deleted successfully"})


@app.route("/examiner/dashboard", methods=["GET"])
@jwt_required()
def examiner_dashboard():

    examiner_id = get_jwt_identity()

    examiner = User.query.get(examiner_id)

    if not examiner or examiner.role != "Examiner":
        return jsonify({"message": "Examiner not found"})

    examinations = Examination.query.filter_by(
        examiner_id=examiner_id
    ).all()

    total_examinations = len(examinations)

    slots = ExaminationSlot.query.filter_by(
        examiner_id=examiner_id
    ).all()

    total_slots = len(slots)

    total_students = 0
    pending_evaluations = 0

    for slot in slots:

        bookings = Booking.query.filter_by(
            slot_id=slot.id,
            status="Booked"
        ).all()

        total_students = total_students + len(bookings)

        for booking in bookings:

            evaluation = Evaluation.query.filter_by(
                booking_id=booking.id
            ).first()

            if not evaluation or evaluation.status == "Pending":
                pending_evaluations += 1

    exam_list = []

    for exam in examinations:
        exam_list.append({
            "id": exam.id,
            "exam_name": exam.exam_name,
            "exam_type": exam.exam_type,
            "status": exam.status
        })

    return jsonify({
        "name": examiner.name,
        "total_examinations": total_examinations,
        "total_slots": total_slots,
        "total_students": total_students,
        "pending_evaluations": pending_evaluations,
        "examinations": exam_list
    })
    
@app.route("/examiner/profile", methods=["GET", "POST", "PUT"])
@jwt_required()
def examiner_profile():

    examiner_id = int(get_jwt_identity())

    examiner = User.query.get(examiner_id)

    if not examiner or examiner.role != "Examiner":
        return jsonify({"message": "Examiner not found"})

    profile = ExaminerProfile.query.filter_by(
        user_id=examiner_id
    ).first()

    if request.method == "GET":

        if not profile:
            return jsonify({
                "profile_exists": False,
                "name": examiner.name,
                "email": examiner.email
            })

        return jsonify({
            "profile_exists": True,
            "name": examiner.name,
            "email": examiner.email,
            "department": profile.department,
            "phone": profile.phone,
            "address": profile.address,
            "past_experience": profile.past_experience,
            "status": profile.status
        })

    data = request.get_json()

    if request.method == "POST":

        if profile:
            return jsonify({"message": "Profile already exists"})

        profile = ExaminerProfile(
            user_id=examiner_id,
            department=data.get("department"),
            phone=data.get("phone"),
            address=data.get("address"),
            past_experience=data.get("past_experience")
        )

        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Profile created successfully"})

    if request.method == "PUT":

        if not profile:
            return jsonify({"message": "Profile not found"})

        profile.department = data.get("department")
        profile.phone = data.get("phone")
        profile.address = data.get("address")
        profile.past_experience = data.get("past_experience")

        db.session.commit()

        return jsonify({"message": "Profile updated successfully"})
      

@app.route("/open_slot/<int:id>", methods=["POST"])
@jwt_required()
def open_slot(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    if examination.results_published:
        return jsonify({"message": "Cannot open slots. Examination is finished"})

    examination.examiner_slot_creation_open = True

    db.session.commit()

    return jsonify({"message": "Slot creation opened successfully"})


@app.route("/close_slot/<int:id>", methods=["POST"])
@jwt_required()
def close_slot(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    examination.examiner_slot_creation_open = False

    db.session.commit()

    return jsonify({"message": "Slot creation closed successfully"})

@app.route("/view_slot/<int:id>", methods=["GET"])
@jwt_required()
def view_slot(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    slots = ExaminationSlot.query.filter_by(
        examination_id=id
    ).all()

    slot_list = []

    for slot in slots:
        evaluated = False
        booked_names = []
        for booking in slot.bookings:
            if booking.status == "Booked" and booking.student:
                booked_names.append(booking.student.name)
            if booking.evaluation and booking.evaluation.status == "Submitted":
                evaluated = True
        slot_examiner = User.query.get(slot.examiner_id)
        slot_list.append({
            "id": slot.id,
            "date": slot.date.isoformat(),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "maximum_capacity": slot.maximum_capacity,
            "available_seats": slot.available_seats,
            "booked_seats": slot.maximum_capacity - slot.available_seats,
            "status": slot.status,
            "meeting_link": slot.meeting_link,
            "examiner_id": slot.examiner_id,
            "examiner_name": slot_examiner.name if slot_examiner else "",
            "booked_by": ", ".join(booked_names) if booked_names else "-",
            "evaluated": evaluated,
            "exam_start_date": str(examination.exam_start_time or "")[:10],
            "exam_end_date": str(examination.exam_end_time or "")[:10],
        })

    return jsonify({
        "examination_name": examination.exam_name,
        "exam_start_time": examination.exam_start_time,
        "exam_end_time": examination.exam_end_time,
        "data": slot_list
    })

@app.route("/admin_exam_detail/<int:id>", methods=["GET"])
@jwt_required()
def admin_exam_detail(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    course = Course.query.get(examination.course_id)
    examiner = User.query.get(examination.examiner_id)

    rubric_list = []

    for rubric in examination.rubrics:
        rubric_list.append({
            "id": rubric.id,
            "criterion_name": rubric.criterion_name,
            "maximum_marks": rubric.maximum_marks,
            "weightage": rubric.weightage,
            "description": rubric.description
        })

    slot_list = []
    for slot in ExaminationSlot.query.filter_by(examination_id=id).all():
        booked_names = []
        evaluated = False
        for booking in slot.bookings:
            if booking.status == "Booked" and booking.student:
                booked_names.append(booking.student.name)
            if booking.evaluation and booking.evaluation.status == "Submitted":
                evaluated = True
        slot_examiner = User.query.get(slot.examiner_id)
        slot_list.append({
            "id": slot.id,
            "date": slot.date.isoformat(),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "maximum_capacity": slot.maximum_capacity,
            "available_seats": slot.available_seats,
            "status": slot.status,
            "meeting_link": slot.meeting_link,
            "examiner_id": slot.examiner_id,
            "examiner_name": slot_examiner.name if slot_examiner else "",
            "booked_by": ", ".join(booked_names) if booked_names else "-",
            "evaluated": evaluated,
        })

    return jsonify({
        "id": examination.id,
        "exam_name": examination.exam_name,
        "exam_type": examination.exam_type,
        "course_name": course.course_name if course else "",
        "course_code": course.course_code if course else "",
        "examiner_id": examination.examiner_id,
        "examiner_name": examiner.name if examiner else "",
        "examiner_email": examiner.email if examiner else "",
        "slot_start_date": examination.slot_start_date,
        "slot_end_date": examination.slot_end_date,
        "booking_start_time": examination.booking_start_time,
        "booking_end_time": examination.booking_end_time,
        "exam_start_time": examination.exam_start_time,
        "exam_end_time": examination.exam_end_time,
        "status": examination.status,
        "rubrics": rubric_list,
        "slots": slot_list,
    })


# Examiner slots allow only 1 seat (m2-aligned capacity rule)
MAX_SLOT_CAPACITY = 1


def _parse_hhmm(value):
    text = str(value or "")[:5]
    parts = text.split(":")
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return None


def _ranges_overlap(start_a, end_a, start_b, end_b):
    if None in (start_a, end_a, start_b, end_b):
        return False
    return start_a < end_b and start_b < end_a


def _active_bookings_count(slot_id):
    return Booking.query.filter(
        Booking.slot_id == slot_id,
        Booking.status != "Cancelled",
    ).count()


def _sync_slot_seats(slot):
    """Keep capacity at 1 and available_seats in sync with active bookings."""
    slot.maximum_capacity = MAX_SLOT_CAPACITY
    taken = _active_bookings_count(slot.id)
    slot.available_seats = max(0, MAX_SLOT_CAPACITY - taken)
    slot.status = "Full" if slot.available_seats == 0 else "Available"
    return slot


def _parse_ymd(value):
    text = str(value or "").strip()[:10]
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _booking_period_started(exam):
    """True if admin opened booking or booking start date has arrived (like m2)."""
    if exam is None:
        return False
    if exam.student_booking_open:
        return True
    start = _parse_ymd(exam.booking_start_time)
    return bool(start and date.today() >= start)


def _normalize_capacity(raw_capacity):
    """Force max 1 seat per examiner slot."""
    try:
        capacity = int(raw_capacity)
    except (TypeError, ValueError):
        return None
    if capacity != MAX_SLOT_CAPACITY:
        return None
    return MAX_SLOT_CAPACITY


def has_examiner_clash(exam, new_examiner_id):
    """Return conflict message if examiner is busy on overlapping slots, else None.

    Rule: an examiner with no slots is free and can be assigned by admin.
    """
    new_id = int(new_examiner_id)
    if exam.examiner_id and int(exam.examiner_id) == new_id:
        return None

    # No slots at all → free; admin can assign
    if ExaminationSlot.query.filter_by(examiner_id=new_id).count() == 0:
        return None

    exam_slots = ExaminationSlot.query.filter_by(examination_id=exam.id).all()
    for slot in exam_slots:
        start = _parse_hhmm(slot.start_time.strftime("%H:%M"))
        end = _parse_hhmm(slot.end_time.strftime("%H:%M"))

        others = ExaminationSlot.query.filter(
            ExaminationSlot.id != slot.id,
            ExaminationSlot.examination_id != exam.id,
            ExaminationSlot.date == slot.date,
            ExaminationSlot.examiner_id == new_id,
        ).all()

        for other in others:
            other_start = _parse_hhmm(other.start_time.strftime("%H:%M"))
            other_end = _parse_hhmm(other.end_time.strftime("%H:%M"))
            if _ranges_overlap(start, end, other_start, other_end):
                person = User.query.get(new_id)
                name = person.name if person else "This examiner"
                return (
                    f"{name} is not free on {slot.date.isoformat()} "
                    f"at {slot.start_time.strftime('%H:%M')}"
                )
    return None


@app.route("/admin/exam-free-examiners/<int:exam_id>", methods=["GET"])
@jwt_required()
def exam_free_examiners(exam_id):
    """List examiners with free/busy status for reassignment on this exam."""
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"message": "Access denied"}), 403

    exam = Examination.query.get(exam_id)
    if exam is None:
        return jsonify({"message": "Examination not found"}), 404

    examiners = User.query.filter_by(role="Examiner").all()
    examiner_list = []

    for examiner in examiners:
        slot_count = ExaminationSlot.query.filter_by(examiner_id=examiner.id).count()
        conflict = has_examiner_clash(exam, examiner.id)
        is_free = conflict is None and not examiner.is_blocked

        examiner_list.append({
            "id": examiner.id,
            "name": examiner.name,
            "email": examiner.email,
            "role": examiner.role,
            "is_blocked": examiner.is_blocked,
            "has_slots": slot_count > 0,
            "is_free": is_free,
            "free_reason": (
                "current"
                if exam.examiner_id and int(exam.examiner_id) == examiner.id
                else "no_slots"
                if slot_count == 0
                else "available"
                if is_free
                else "busy"
            ),
        })

    return jsonify({"data": examiner_list})


@app.route("/admin/reassign-exam-examiner/<int:exam_id>", methods=["POST"])
@jwt_required()
def reassign_exam_examiner(exam_id):
    """Admin changes the examiner assigned to an examination (like reference)."""
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json() or {}
    new_examiner_id = data.get("examiner_id") or data.get("examinor_id")
    if not new_examiner_id:
        return jsonify({"message": "Please select an examiner"}), 400

    exam = Examination.query.get(exam_id)
    if exam is None:
        return jsonify({"message": "Examination not found"}), 404

    examiner = User.query.filter_by(id=new_examiner_id, role="Examiner").first()
    if examiner is None:
        return jsonify({"message": "Examiner not found"}), 404
    if examiner.is_blocked:
        return jsonify({"message": "Cannot assign a blocked examiner"}), 400

    conflict = has_examiner_clash(exam, new_examiner_id)
    if conflict:
        return jsonify({"message": conflict}), 400

    old_id = exam.examiner_id
    exam.examiner_id = int(new_examiner_id)

    for slot in ExaminationSlot.query.filter_by(examination_id=exam_id).all():
        if slot.examiner_id == old_id:
            slot.examiner_id = int(new_examiner_id)
        for booking in slot.bookings:
            if booking.evaluation and booking.evaluation.examiner_id == old_id:
                if booking.evaluation.status != "Submitted":
                    booking.evaluation.examiner_id = int(new_examiner_id)

    db.session.commit()
    return jsonify({"message": "Examiner changed successfully"})


@app.route("/admin/reschedule-slot/<int:slot_id>", methods=["POST"])
@jwt_required()
def reschedule_slot(slot_id):
    """Admin reschedules a slot date/time (like reference move_slot)."""
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    data = request.get_json() or {}
    slot = ExaminationSlot.query.get(slot_id)
    if slot is None:
        return jsonify({"message": "Slot not found"})

    for booking in slot.bookings:
        if booking.status == "Booked" and booking.evaluation and booking.evaluation.status == "Submitted":
            return jsonify({
                "message": "Marks have already been given, so this slot cannot be rescheduled"
            })

    exam = Examination.query.get(slot.examination_id)
    if exam is None:
        return jsonify({"message": "Examination not found"})

    slot_date_raw = data.get("slot_date") or data.get("date")
    start_raw = data.get("slot_time") or data.get("start_time")
    end_raw = data.get("end_time")

    if not slot_date_raw or not start_raw:
        return jsonify({"message": "Please provide date and start time"})

    try:
        new_date = date.fromisoformat(str(slot_date_raw)[:10])
    except ValueError:
        return jsonify({"message": "Invalid date format"})

    # Keep reschedule inside exam window when dates are set
    try:
        if exam.exam_start_time:
            exam_start = date.fromisoformat(str(exam.exam_start_time)[:10])
            if new_date < exam_start:
                return jsonify({
                    "message": "Reschedule only on an exam date, from the exam start date to the exam end date"
                })
        if exam.exam_end_time:
            exam_end = date.fromisoformat(str(exam.exam_end_time)[:10])
            if new_date > exam_end:
                return jsonify({
                    "message": "Reschedule only on an exam date, from the exam start date to the exam end date"
                })
    except ValueError:
        pass

    try:
        start_parts = str(start_raw)[:5].split(":")
        new_start = datetime.strptime(
            f"{int(start_parts[0]):02d}:{int(start_parts[1]):02d}", "%H:%M"
        ).time()
        if end_raw:
            end_parts = str(end_raw)[:5].split(":")
            new_end = datetime.strptime(
                f"{int(end_parts[0]):02d}:{int(end_parts[1]):02d}", "%H:%M"
            ).time()
        else:
            new_end = slot.end_time
    except (ValueError, IndexError):
        return jsonify({"message": "Invalid time format"})

    if new_end <= new_start:
        return jsonify({"message": "Choose a free time on the exam date"})

    new_start_m = _parse_hhmm(new_start.strftime("%H:%M"))
    new_end_m = _parse_hhmm(new_end.strftime("%H:%M"))

    for other in ExaminationSlot.query.filter_by(examination_id=slot.examination_id).all():
        if other.id == slot.id:
            continue
        if other.date != new_date:
            continue
        other_start = _parse_hhmm(other.start_time.strftime("%H:%M"))
        other_end = _parse_hhmm(other.end_time.strftime("%H:%M"))
        if _ranges_overlap(new_start_m, new_end_m, other_start, other_end):
            return jsonify({
                "message": "That time is not free. Choose a free time on the exam date"
            })

    slot.date = new_date
    slot.start_time = new_start
    slot.end_time = new_end
    db.session.commit()

    return jsonify({"message": "Slot rescheduled successfully"})
    
@app.route("/open_booking/<int:id>", methods=["POST"])
@jwt_required()
def open_booking(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    if examination.results_published:
        return jsonify({"message": "Cannot open booking. Examination is finished"})

    examination.student_booking_open = True
    db.session.commit()

    return jsonify({"message": "Student booking opened successfully"})


@app.route("/close_booking/<int:id>", methods=["POST"])
@jwt_required()
def close_booking(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    examination = Examination.query.get(id)

    if examination is None:
        return jsonify({"message": "Examination not found"})

    examination.student_booking_open = False
    db.session.commit()

    return jsonify({"message": "Student booking closed successfully"})

@app.route("/admin/students", methods=["GET"])
@jwt_required()
def admin_students():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    search = request.args.get("search", "").lower()

    students = User.query.filter_by(role="Student").all()

    student_list = []

    for student in students:

        profile = StudentProfile.query.filter_by(user_id=student.id).first()

        if (search in student.name.lower() or
            search in student.email.lower() or
            search in str(student.id)):

            student_list.append({
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "is_blocked": student.is_blocked,
                "address": profile.address if profile else "",
                "phone": profile.phone if profile else "",
                "past_experience": profile.past_experience if profile else "",
            })

    return jsonify({"data": student_list})

@app.route("/admin/student/<int:id>/<action>", methods=["POST"])
@jwt_required()
def change_student_status(id, action):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"message": "Access denied"}), 403

    user = User.query.filter_by(id=id, role="Student").first()
    if user is None:
        return jsonify({"message": "Student not found"}), 404

    if action == "block":
        user.is_blocked = True
    elif action == "unblock":
        user.is_blocked = False
    else:
        return jsonify({"message": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"success": True, "message": f"Student {action}ed successfully"})


@app.route("/admin/block-student/<int:id>", methods=["POST"])
@jwt_required()
def block_student(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    student = User.query.filter_by(
        id=id,
        role="Student"
    ).first()

    if not student:
        return jsonify({"message": "Student not found"})

    student.is_blocked = True

    db.session.commit()

    return jsonify({
        "message": "Student blocked successfully"
    })


@app.route("/admin/unblock-student/<int:id>", methods=["POST"])
@jwt_required()
def unblock_student(id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    student = User.query.filter_by(
        id=id,
        role="Student"
    ).first()

    if not student:
        return jsonify({"message": "Student not found"})

    student.is_blocked = False

    db.session.commit()

    return jsonify({
        "message": "Student unblocked successfully"
    })
    
@app.route("/admin/bookings", methods=["GET"])
@jwt_required()
def admin_bookings():

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    bookings = Booking.query.all()

    booking_list = []

    for booking in bookings:

        slot = booking.slot
        student = booking.student

        examination = slot.examination
        examiner = slot.examiner

        booking_list.append({
            "id": booking.id,
            "student_name": student.name,
            "student_email": student.email,
            "examination_name": examination.exam_name,
            "examiner_name": examiner.name,
            "slot_date": slot.date.strftime("%d-%m-%Y"),
            "start_time": slot.start_time.strftime("%I:%M %p"),
            "end_time": slot.end_time.strftime("%I:%M %p"),
            "booking_date": booking.booking_date.strftime("%d-%m-%Y %I:%M %p"),
            "status": booking.status
        })

    return jsonify({
        "message": "Bookings fetched successfully",
        "data": booking_list
    })


@app.route("/admin/available-slots/<int:booking_id>", methods=["GET"])
@jwt_required()
def available_slots(booking_id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"message": "Booking not found"})

    old_slot = booking.slot

    slots = ExaminationSlot.query.filter_by(
        examination_id=old_slot.examination_id
    ).all()

    slot_list = []

    for slot in slots:

        if slot.id != old_slot.id and slot.available_seats > 0 and slot.status == "Available":

            slot_list.append({
                "id": slot.id,
                "date": slot.date.strftime("%d-%m-%Y"),
                "start_time": slot.start_time.strftime("%I:%M %p"),
                "end_time": slot.end_time.strftime("%I:%M %p"),
                "available_seats": slot.available_seats
            })

    return jsonify({"data": slot_list})

@app.route("/admin/reschedule-booking/<int:booking_id>", methods=["POST"])
@jwt_required()
def reschedule_booking(booking_id):

    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"})

    booking = Booking.query.get(booking_id)

    if booking is None:
        return jsonify({"message": "Booking not found"})

    data = request.get_json()

    new_slot_id = data.get("slot_id")

    new_slot = ExaminationSlot.query.get(new_slot_id)

    if new_slot is None:
        return jsonify({"message": "New slot not found"})

    old_slot = booking.slot

    if old_slot.examination_id != new_slot.examination_id:
        return jsonify({
            "message": "You can select a slot from the same examination only"
        })

    if old_slot.id == new_slot.id:
        return jsonify({"message": "This is already the booked slot"})

    if _active_bookings_count(new_slot.id) >= MAX_SLOT_CAPACITY or new_slot.status != "Available":
        return jsonify({"message": "No seats available in this slot"})

    booking.slot_id = new_slot.id
    _sync_slot_seats(old_slot)
    _sync_slot_seats(new_slot)

    db.session.commit()

    return jsonify({
        "message": "Booking rescheduled successfully"
    })


def _booking_examiner_busy(old_slot, examiner_id):
    """True if examiner has overlapping slots on another exam (no slots = free)."""
    examiner_id = int(examiner_id)
    if ExaminationSlot.query.filter_by(examiner_id=examiner_id).count() == 0:
        return False

    start = _parse_hhmm(old_slot.start_time.strftime("%H:%M"))
    end = _parse_hhmm(old_slot.end_time.strftime("%H:%M"))

    others = ExaminationSlot.query.filter(
        ExaminationSlot.examiner_id == examiner_id,
        ExaminationSlot.examination_id != old_slot.examination_id,
        ExaminationSlot.date == old_slot.date,
        ExaminationSlot.id != old_slot.id,
    ).all()

    for other in others:
        other_start = _parse_hhmm(other.start_time.strftime("%H:%M"))
        other_end = _parse_hhmm(other.end_time.strftime("%H:%M"))
        if _ranges_overlap(start, end, other_start, other_end):
            return True
    return False


@app.route("/admin/reassign-slots/<int:booking_id>", methods=["GET"])
@jwt_required()
def reassign_slots(booking_id):
    """List free examiners for booking reassignment (no slots = free)."""
    user_role = get_jwt()

    if user_role.get("role") != "Admin":
        return jsonify({"message": "Access denied"}), 403

    booking = Booking.query.get(booking_id)

    if booking is None:
        return jsonify({"message": "Booking not found"}), 404

    old_slot = booking.slot
    current_examiner_id = old_slot.examiner_id
    options = []

    examiners = User.query.filter_by(role="Examiner").all()
    for examiner in examiners:
        if examiner.id == current_examiner_id:
            continue
        if examiner.is_blocked:
            continue
        if _booking_examiner_busy(old_slot, examiner.id):
            continue

        # Prefer an existing free slot for this examiner on the same exam
        existing = ExaminationSlot.query.filter(
            ExaminationSlot.examination_id == old_slot.examination_id,
            ExaminationSlot.examiner_id == examiner.id,
            ExaminationSlot.id != old_slot.id,
            ExaminationSlot.available_seats > 0,
            ExaminationSlot.status == "Available",
        ).first()

        slot_count = ExaminationSlot.query.filter_by(examiner_id=examiner.id).count()
        options.append({
            "examiner_id": examiner.id,
            "examiner_name": examiner.name,
            "has_slots": slot_count > 0,
            "will_create_slot": existing is None,
            "slot_id": existing.id if existing else None,
            "date": (
                existing.date.strftime("%d-%m-%Y")
                if existing
                else old_slot.date.strftime("%d-%m-%Y")
            ),
            "start_time": (
                existing.start_time.strftime("%I:%M %p")
                if existing
                else old_slot.start_time.strftime("%I:%M %p")
            ),
            "end_time": (
                existing.end_time.strftime("%I:%M %p")
                if existing
                else old_slot.end_time.strftime("%I:%M %p")
            ),
            "available_seats": existing.available_seats if existing else 1,
        })

    return jsonify({"data": options})


@app.route("/admin/reassign-booking/<int:booking_id>", methods=["POST"])
@jwt_required()
def reassign_booking(booking_id):
    """Admin reassigns a booking to another examiner (creates slot if needed)."""
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"message": "Access denied"}), 403

    booking = Booking.query.get(booking_id)
    if booking is None:
        return jsonify({"message": "Booking not found"}), 404

    if booking.evaluation and booking.evaluation.status == "Submitted":
        return jsonify({
            "message": "Marks have already been given, so examiner cannot be reassigned"
        }), 400

    data = request.get_json() or {}
    old_slot = booking.slot

    new_slot = None
    examiner_id = data.get("examiner_id")
    new_slot_id = data.get("slot_id")

    if examiner_id:
        examiner = User.query.filter_by(id=examiner_id, role="Examiner").first()
        if examiner is None:
            return jsonify({"message": "Examiner not found"}), 404
        if examiner.is_blocked:
            return jsonify({"message": "Cannot reassign to a blocked examiner"}), 400
        if examiner.id == old_slot.examiner_id:
            return jsonify({"message": "This examiner is already assigned"}), 400
        if _booking_examiner_busy(old_slot, examiner.id):
            return jsonify({"message": f"{examiner.name} is not free at this time"}), 400

        new_slot = ExaminationSlot.query.filter(
            ExaminationSlot.examination_id == old_slot.examination_id,
            ExaminationSlot.examiner_id == examiner.id,
            ExaminationSlot.id != old_slot.id,
            ExaminationSlot.available_seats > 0,
            ExaminationSlot.status == "Available",
        ).first()

        # No slot for this free examiner → create one seat (capacity always 1)
        if new_slot is None:
            new_slot = ExaminationSlot(
                examination_id=old_slot.examination_id,
                examiner_id=examiner.id,
                date=old_slot.date,
                start_time=old_slot.start_time,
                end_time=old_slot.end_time,
                maximum_capacity=MAX_SLOT_CAPACITY,
                available_seats=MAX_SLOT_CAPACITY,
                status="Available",
                meeting_link=old_slot.meeting_link,
            )
            db.session.add(new_slot)
            db.session.flush()

    elif new_slot_id:
        new_slot = ExaminationSlot.query.get(new_slot_id)
        if new_slot is None:
            return jsonify({"message": "New slot not found"}), 404
    else:
        return jsonify({"message": "Please select an examiner"}), 400

    if old_slot.examination_id != new_slot.examination_id:
        return jsonify({
            "message": "You can select a slot from the same examination only"
        }), 400

    if old_slot.id == new_slot.id:
        return jsonify({"message": "This is already the booked slot"}), 400

    if _active_bookings_count(new_slot.id) >= MAX_SLOT_CAPACITY or new_slot.status != "Available":
        return jsonify({"message": "This slot is not available"}), 400

    new_examiner = User.query.get(new_slot.examiner_id)
    if new_examiner and new_examiner.is_blocked:
        return jsonify({"message": "Cannot reassign to a blocked examiner"}), 400

    booking.slot_id = new_slot.id

    if booking.evaluation:
        booking.evaluation.examiner_id = new_slot.examiner_id

    _sync_slot_seats(old_slot)
    _sync_slot_seats(new_slot)

    db.session.commit()

    return jsonify({
        "message": "Examiner reassigned successfully"
    })


@app.route("/examiner/assigned-examinations", methods=["GET"])
@jwt_required()
def assigned_examinations():

    examiner_id = int(get_jwt_identity())

    examiner = User.query.get(examiner_id)

    if not examiner or examiner.role != "Examiner":
        return jsonify({"message": "Examiner not found"})

    examinations = Examination.query.filter_by(
        examiner_id=examiner_id
    ).all()

    data = []

    for exam in examinations:
        data.append({
            "id": exam.id,
            "exam_name": exam.exam_name,
            "course_name": exam.course.course_name,
            "exam_type": exam.exam_type,
            "slot_start_date": exam.slot_start_date,
            "slot_end_date": exam.slot_end_date,
            "booking_start_time":exam.booking_start_time,
            "booking_end_time":exam.booking_end_time,
            "exam_start_time": exam.exam_start_time,
            "exam_end_time": exam.exam_end_time,
            "slot_creation_open": exam.examiner_slot_creation_open,
            "booking_open": exam.student_booking_open,
            "results_published": exam.results_published,
            "status": exam.status
        })

    return jsonify({"data": data})

@app.route("/examiner/create-slot", methods=["POST"])
@jwt_required()
def create_examiner_slot():

    examiner_id = int(get_jwt_identity())

    data = request.get_json() or {}

    examination_id = data.get("examination_id")
    date_raw = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    capacity_raw = data.get("maximum_capacity", MAX_SLOT_CAPACITY)
    meeting_link = (data.get("meeting_link") or "").strip() or None

    examination = Examination.query.get(examination_id)

    if not examination:
        return jsonify({"message": "Examination not found"})

    if examination.examiner_id != examiner_id:
        return jsonify({"message": "Not assigned to you"})

    if examination.results_published:
        return jsonify({"message": "Examination is finished. Cannot create slots"})

    slot_window_start = _parse_ymd(examination.slot_start_date)
    slot_window_end = _parse_ymd(examination.slot_end_date)
    today = date.today()
    in_window = bool(
        slot_window_start
        and slot_window_end
        and slot_window_start <= today <= slot_window_end
    )
    if not examination.examiner_slot_creation_open and not in_window:
        return jsonify({
            "message": "You can only create a slot between the slot start date and the slot end date"
        })

    try:
        slot_date = datetime.strptime(str(date_raw).strip()[:10], "%Y-%m-%d").date()
        start = datetime.strptime(str(start_time)[:5], "%H:%M").time()
        end = datetime.strptime(str(end_time)[:5], "%H:%M").time()
    except (ValueError, TypeError, AttributeError):
        return jsonify({"message": "Enter valid details"})

    exam_start = _parse_ymd(examination.exam_start_time)
    exam_end = _parse_ymd(examination.exam_end_time)
    if not exam_start or not exam_end:
        return jsonify({"message": "Examination dates are invalid"})

    if slot_date < exam_start or slot_date > exam_end:
        return jsonify({
            "message": "Slot date must be between the exam start date and the exam end date"
        })

    if start >= end:
        return jsonify({"message": "Invalid time"})

    capacity = _normalize_capacity(capacity_raw)
    if capacity is None:
        return jsonify({
            "message": "Maximum seats for one examiner slot must be 1"
        })

    new_slot = ExaminationSlot(
        examination_id=examination_id,
        examiner_id=examiner_id,
        date=slot_date,
        start_time=start,
        end_time=end,
        maximum_capacity=MAX_SLOT_CAPACITY,
        available_seats=MAX_SLOT_CAPACITY,
        status="Available",
        meeting_link=meeting_link,
    )

    db.session.add(new_slot)
    db.session.commit()

    return jsonify({"message": "Slot created successfully"})


@app.route("/examiner/my-slots", methods=["GET"])
@jwt_required()
def examiner_my_slots():
    examiner_id = int(get_jwt_identity())

    slots = ExaminationSlot.query.filter_by(examiner_id=examiner_id).all()

    data = []

    for slot in slots:
        data.append({
            "id": slot.id,
            "examination_id": slot.examination_id,
            "exam_name": slot.examination.exam_name,
            "date": slot.date.strftime("%Y-%m-%d"),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "maximum_capacity": slot.maximum_capacity,
            "available_seats": slot.available_seats,
            "status": slot.status
        })

    return jsonify({"data": data})

@app.route("/examiner/update-slot/<int:slot_id>", methods=["PUT"])
@jwt_required()
def update_examiner_slot(slot_id):
    examiner_id = int(get_jwt_identity())

    slot = ExaminationSlot.query.get(slot_id)

    if not slot:
        return jsonify({"message": "Slot not found"})

    if slot.examiner_id != examiner_id:
        return jsonify({"message": "You cannot update this slot"})

    examination = Examination.query.get(slot.examination_id)

    if _booking_period_started(examination):
        return jsonify({
            "message": "Slots can only be updated before student booking begins"
        })

    data = request.get_json() or {}

    try:
        slot_date = datetime.strptime(str(data.get("date"))[:10], "%Y-%m-%d").date()
        start = datetime.strptime(str(data.get("start_time"))[:5], "%H:%M").time()
        end = datetime.strptime(str(data.get("end_time"))[:5], "%H:%M").time()
    except (ValueError, TypeError):
        return jsonify({"message": "Please enter valid slot details"})

    exam_start = _parse_ymd(examination.exam_start_time)
    exam_end = _parse_ymd(examination.exam_end_time)
    if not exam_start or not exam_end:
        return jsonify({"message": "Examination dates are invalid"})

    if slot_date < exam_start or slot_date > exam_end:
        return jsonify({
            "message": "Slot date must be between the exam start date and the exam end date"
        })

    if start >= end:
        return jsonify({"message": "End time must be after start time"})

    capacity_raw = data.get("maximum_capacity", MAX_SLOT_CAPACITY)
    capacity = _normalize_capacity(capacity_raw)
    if capacity is None:
        return jsonify({
            "message": "Maximum seats for one examiner slot must be 1"
        })

    booked_students = _active_bookings_count(slot.id)
    if capacity < booked_students:
        return jsonify({"message": "Capacity cannot be less than booked students"})

    slot.date = slot_date
    slot.start_time = start
    slot.end_time = end
    if "meeting_link" in data:
        slot.meeting_link = (data.get("meeting_link") or "").strip() or None
    _sync_slot_seats(slot)

    db.session.commit()

    return jsonify({"message": "Slot updated successfully"})

@app.route("/examiner/delete-slot/<int:slot_id>", methods=["DELETE"])
@jwt_required()
def delete_examiner_slot(slot_id):
    examiner_id = int(get_jwt_identity())

    slot = ExaminationSlot.query.get(slot_id)

    if not slot:
        return jsonify({"message": "Slot not found"})

    if slot.examiner_id != examiner_id:
        return jsonify({"message": "You cannot delete this slot"})

    examination = Examination.query.get(slot.examination_id)

    if _booking_period_started(examination):
        return jsonify({
            "message": "Slots can only be removed before student booking begins"
        })

    active = _active_bookings_count(slot.id)
    if active > 0:
        return jsonify({"message": "Cannot remove a slot that has bookings"})

    # Remove cancelled/orphan booking rows like m2, then delete slot
    for booking in Booking.query.filter_by(slot_id=slot.id).all():
        if booking.evaluation:
            db.session.delete(booking.evaluation)
        db.session.delete(booking)

    db.session.delete(slot)
    db.session.commit()

    return jsonify({"message": "Slot deleted successfully"})


@app.route("/examiner/booked-students", methods=["GET"])
@jwt_required()
def examiner_view_booked_students():

    examiner_id = int(get_jwt_identity())

    slots = ExaminationSlot.query.filter_by(
        examiner_id=examiner_id
    ).all()

    data = []

    for slot in slots:

        bookings = Booking.query.filter_by(
            slot_id=slot.id,
            status="Booked"
        ).all()

        for booking in bookings:

            evaluation = Evaluation.query.filter_by(
                booking_id=booking.id
            ).first()

            data.append({
                "booking_id": booking.id,
                "student_name": booking.student.name,
                "student_email": booking.student.email,
                "exam_name": slot.examination.exam_name,
                "date": slot.date.strftime("%Y-%m-%d"),
                "start_time": slot.start_time.strftime("%I:%M %p"),
                "end_time": slot.end_time.strftime("%I:%M %p"),
                "booking_status": booking.status,
                "evaluation_status": evaluation.status if evaluation else "Pending"
            })

    return jsonify({"data": data})

@app.route("/examiner/evaluations", methods=["GET"])
@jwt_required()
def examiner_evaluations():

    examiner_id = int(get_jwt_identity())

    slots = ExaminationSlot.query.filter_by(
        examiner_id=examiner_id
    ).all()

    data = []

    for slot in slots:

        bookings = Booking.query.filter_by(
            slot_id=slot.id,
            status="Booked"
        ).all()

        for booking in bookings:

            evaluation = Evaluation.query.filter_by(
                booking_id=booking.id
            ).first()

            if not evaluation or evaluation.status == "Pending":

                data.append({
                    "booking_id": booking.id,
                    "student_name": booking.student.name,
                    "student_email": booking.student.email,
                    "exam_name": slot.examination.exam_name,
                    "date": slot.date.strftime("%Y-%m-%d")
                })

    return jsonify({"data": data})
@app.route("/examiner/evaluation-details/<int:booking_id>", methods=["GET"])
@jwt_required()
def examiner_evaluation_details(booking_id):

    examiner_id = int(get_jwt_identity())

    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"message": "Booking not found"})

    if booking.slot.examiner_id != examiner_id:
        return jsonify({"message": "You cannot evaluate this student"})

    rubrics = ExaminationRubric.query.filter_by(
        examination_id=booking.slot.examination_id
    ).all()

    data = []

    for rubric in rubrics:
        data.append({
            "id": rubric.id,
            "criterion_name": rubric.criterion_name,
            "maximum_marks": rubric.maximum_marks,
            "weightage": rubric.weightage,
            "description": rubric.description
        })

    return jsonify({
        "student_name": booking.student.name,
        "student_email": booking.student.email,
        "exam_name": booking.slot.examination.exam_name,
        "rubrics": data
    })

@app.route("/examiner/submit-evaluation/<int:booking_id>", methods=["POST"])
@jwt_required()
def submit_evaluation(booking_id):

    examiner_id = int(get_jwt_identity())

    booking = Booking.query.get(booking_id)

    if not booking:
        return jsonify({"message": "Booking not found"})

    if booking.slot.examiner_id != examiner_id:
        return jsonify({"message": "You cannot evaluate this student"})

    data = request.get_json()

    marks_data = data.get("marks", [])
    remarks = data.get("remarks")

    total_marks = 0

    for item in marks_data:
        total_marks += float(item.get("marks", 0))

    evaluation = Evaluation.query.filter_by(
        booking_id=booking_id
    ).first()

    if evaluation:
        evaluation.total_marks = total_marks
        evaluation.marks = str(marks_data)
        evaluation.remarks = remarks
        evaluation.evaluation_date = datetime.now()
        evaluation.status = "Submitted"
    else:
        evaluation = Evaluation(
            booking_id=booking_id,
            examiner_id=examiner_id,
            total_marks=total_marks,
            marks=str(marks_data),
            remarks=remarks,
            evaluation_date=datetime.now(),
            status="Submitted"
        )

        db.session.add(evaluation)

    db.session.commit()

    return jsonify({"message": "Evaluation submitted successfully"})    
 
@app.route("/examiner/submitted-evaluations", methods=["GET"])
@jwt_required()
def examiner_submitted_evaluations():

    examiner_id = int(get_jwt_identity())

    evaluations = Evaluation.query.filter_by(
        examiner_id=examiner_id,
        status="Submitted"
    ).all()

    data = []

    for evaluation in evaluations:
        booking = evaluation.booking
        slot = booking.slot

        data.append({
            "id": evaluation.id,
            "student_name": booking.student.name,
            "student_email": booking.student.email,
            "exam_name": slot.examination.exam_name,
            "date": evaluation.evaluation_date.strftime("%Y-%m-%d")
                    if evaluation.evaluation_date else "",
            "total_marks": evaluation.total_marks,
            "remarks": evaluation.remarks
        })

    return jsonify({"data": data})


@app.route("/examiner/submitted-evaluation-details/<int:evaluation_id>", methods=["GET"])
@jwt_required()
def examiner_submitted_evaluation_details(evaluation_id):

    import json
    import ast

    examiner_id = int(get_jwt_identity())

    evaluation = Evaluation.query.filter_by(
        id=evaluation_id,
        examiner_id=examiner_id,
        status="Submitted"
    ).first()

    if not evaluation:
        return jsonify({"message": "Evaluation not found"})

    marks_data = []

    if evaluation.marks:
        try:
            marks_data = json.loads(evaluation.marks)
        except:
            marks_data = ast.literal_eval(evaluation.marks)

    rubric_data = []

    for item in marks_data:
        rubric = ExaminationRubric.query.get(item["rubric_id"])

        if rubric:
            rubric_data.append({
                "criterion_name": rubric.criterion_name,
                "maximum_marks": rubric.maximum_marks,
                "weightage": rubric.weightage,
                "marks_obtained": item["marks"]
            })

    return jsonify({
        "student_name": evaluation.booking.student.name,
        "student_email": evaluation.booking.student.email,
        "exam_name": evaluation.booking.slot.examination.exam_name,
        "total_marks": evaluation.total_marks,
        "remarks": evaluation.remarks,
        "evaluation_date": evaluation.evaluation_date.strftime("%Y-%m-%d")
                           if evaluation.evaluation_date else "",
        "rubrics": rubric_data
    })


@app.route("/student/dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():

    student_id = int(get_jwt_identity())

    student = User.query.get(student_id)

    if not student:
        return jsonify({"message": "Student not found"})

    available_examinations = Examination.query.filter_by(
        student_booking_open=True
    ).count()

    available_slots = ExaminationSlot.query.join(
        Examination
    ).filter(
        Examination.student_booking_open == True,
        ExaminationSlot.status == "Available",
        ExaminationSlot.available_seats > 0,
        ExaminationSlot.date >= datetime.now().date()
    ).count()

    upcoming_examinations = db.session.query(
        Examination.id
    ).join(
        ExaminationSlot
    ).join(
        Booking
    ).filter(
        Booking.student_id == student_id,
        Booking.status == "Booked",
        ExaminationSlot.date >= datetime.now().date()
    ).distinct().count()

    booked_slots = Booking.query.filter_by(
        student_id=student_id,
        status="Booked"
    ).count()

    published_results = Evaluation.query.join(
        Booking
    ).join(
        ExaminationSlot
    ).join(
        Examination
    ).filter(
        Booking.student_id == student_id,
        Examination.results_published == True
    ).count()

    return jsonify({
        "name": student.name,
        "available_examinations": available_examinations,
        "available_slots": available_slots,
        "upcoming_examinations": upcoming_examinations,
        "booked_slots": booked_slots,
        "published_results": published_results
    })

    
@app.route("/user/submitForm", methods=["POST"])
@jwt_required()
def submit_student_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if profile:
        return jsonify({"message": "Profile already exists"})

    profile = StudentProfile(
        user_id=user_id,
        address=data.get("address"),
        phone=data.get("phone"),
        past_experience=data.get("past_experience")
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Profile created successfully"})

@app.route("/get_user_profile", methods=["POST"])
@jwt_required()
def get_user_profile():
    user_id = int(get_jwt_identity())

    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if profile:
        return jsonify({
            "data": {
                "id": profile.id,
                "address": profile.address,
                "phone": profile.phone,
                "past_experience": profile.past_experience
            }
        })

    return jsonify({"data": None})

@app.route("/edit_user_profile", methods=["POST"])
@jwt_required()
def edit_user_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"message": "Profile not found"})

    profile.address = data.get("address")
    profile.phone = data.get("phone")
    profile.past_experience = data.get("past_experience")

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"})


@app.route("/student/examinations", methods=["GET"])
@jwt_required()
def student_examinations():

    exams = Examination.query.all()

    data = []
    today = datetime.now().date()

    for exam in exams:

        start_date = exam.exam_start_time.strip() if exam.exam_start_time else ""
        end_date = exam.exam_end_time.strip() if exam.exam_end_time else ""

        try:
            start = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
            end = datetime.strptime(end_date[:10], "%Y-%m-%d").date()

            if end < today:
                exam_status = "Completed"
                booking_status = "Exam Complete"

            elif exam.student_booking_open:

                available_slot = ExaminationSlot.query.filter(
                    ExaminationSlot.examination_id == exam.id,
                    ExaminationSlot.status == "Available",
                    ExaminationSlot.available_seats > 0
                ).first()

                if available_slot:
                    booking_status = "Booking Started"
                else:
                    booking_status = "Booking Closed"

                if start > today:
                    exam_status = "Upcoming"
                else:
                    exam_status = "Active"

            else:
                booking_status = "Booking Closed"

                if start > today:
                    exam_status = "Upcoming"
                else:
                    exam_status = "Active"

        except (ValueError, TypeError):
            exam_status = "Upcoming"
            booking_status = "Booking Closed"

        data.append({
            "id": exam.id,
            "exam_name": exam.exam_name,
            "course_name": exam.course.course_name if exam.course else "",
            "exam_start_date": start_date,
            "exam_end_date": end_date,
            "booking_status": booking_status,
            "status": exam_status
        })

    courses = []

    for course in Course.query.all():
        courses.append({
            "id": course.id,
            "course_name": course.course_name
        })

    return jsonify({
        "data": data,
        "courses": courses
    })

@app.route("/student/examination-details/<int:exam_id>", methods=["GET"])
@jwt_required()
def student_examination_details(exam_id):

    exam = Examination.query.get(exam_id)

    if not exam:
        return jsonify({"message": "Examination not found"})

    return jsonify({
        "id": exam.id,
        "exam_name": exam.exam_name,
        "exam_type": exam.exam_type,
        "course_name": exam.course.course_name if exam.course else "",
        "exam_start_date": exam.exam_start_time.strip() if exam.exam_start_time else "",
        "exam_end_date": exam.exam_end_time.strip() if exam.exam_end_time else "",
        "booking_start_time": exam.booking_start_time,
        "booking_end_time": exam.booking_end_time,
        "booking_status": "Open" if exam.student_booking_open else "Closed",
        "status": exam.status
    })
    

@app.route("/student/examination-slots/<int:exam_id>", methods=["GET"])
@jwt_required()
def student_examination_slots(exam_id):

    exam = Examination.query.get(exam_id)

    if not exam:
        return jsonify({"message": "Examination not found"})

    slots = ExaminationSlot.query.filter_by(
        examination_id=exam_id
    ).order_by(ExaminationSlot.date, ExaminationSlot.start_time).all()

    data = []

    for slot in slots:
        data.append({
            "id": slot.id,
            "date": slot.date.strftime("%Y-%m-%d"),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "maximum_capacity": slot.maximum_capacity,
            "available_seats": slot.available_seats,
            "status": slot.status
        })

    return jsonify({
    "exam_name": exam.exam_name,
    "course_name": exam.course.course_name if exam.course else "",
    "booking_open": exam.student_booking_open,
    "data": data
})

@app.route("/student/book-slot", methods=["POST"])
@jwt_required()
def student_book_slot():

    student_id = int(get_jwt_identity())
    student = User.query.get(student_id)

    if not student or student.role != "Student":
        return jsonify({"message": "Student not found"})

    data = request.get_json()
    slot_id = data.get("slot_id")

    if not slot_id:
        return jsonify({"message": "Please select a slot"})

    slot = ExaminationSlot.query.get(slot_id)

    if not slot:
        return jsonify({"message": "Slot not found"})

    exam = Examination.query.get(slot.examination_id)

    if not exam:
        return jsonify({"message": "Examination not found"})

    if student.is_blocked:
        return jsonify({"message": "Your account is blocked"})

    booking_start = _parse_ymd(exam.booking_start_time)
    booking_end = _parse_ymd(exam.booking_end_time)
    today = date.today()
    in_booking_window = bool(
        booking_start and booking_end and booking_start <= today <= booking_end
    )
    if not exam.student_booking_open and not in_booking_window:
        return jsonify({"message": "Student booking is closed"})

    existing_booking = Booking.query.join(
        ExaminationSlot,
        Booking.slot_id == ExaminationSlot.id
    ).filter(
        Booking.student_id == student_id,
        ExaminationSlot.examination_id == exam.id,
        Booking.status == "Booked"
    ).first()

    if existing_booking:
        return jsonify({
            "message": "You have already booked this examination"
        })

    taken = _active_bookings_count(slot.id)
    if taken >= MAX_SLOT_CAPACITY or slot.status != "Available":
        return jsonify({"message": "No seats available"})

    booking = Booking(
        student_id=student_id,
        slot_id=slot.id,
        status="Booked"
    )

    db.session.add(booking)
    db.session.flush()
    _sync_slot_seats(slot)
    db.session.commit()

    return jsonify({
        "message": "Examination slot booked successfully"
    })
    
@app.route("/student/my-bookings", methods=["GET"])
@jwt_required()
def student_my_bookings():

    student_id = int(get_jwt_identity())

    bookings = Booking.query.filter_by(
        student_id=student_id
    ).order_by(Booking.booking_date.desc()).all()

    data = []

    for booking in bookings:

        slot = booking.slot
        exam = slot.examination

        booking_status = booking.status
        if exam.results_published and booking.status == "Booked":
            booking_status = "Completed"

        data.append({
            "booking_id": booking.id,
            "exam_name": exam.exam_name,
            "course_name": exam.course.course_name if exam.course else "",
            "exam_type": exam.exam_type,
            "slot_date": slot.date.strftime("%Y-%m-%d"),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
            "booking_status": booking_status,
            "slot_status": slot.status
        })

    return jsonify({
        "data": data
    })


@app.route("/student/exam-history", methods=["GET"])
@jwt_required()
def student_exam_history():

    student_id = int(get_jwt_identity())

    student = User.query.get(student_id)

    if not student or student.role != "Student":
        return jsonify({"message": "Student not found"})

    bookings = Booking.query.filter_by(
        student_id=student_id
    ).all()

    data = []

    for booking in bookings:
        slot = booking.slot
        exam = slot.examination

        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id
        ).first()

        result_available = False

        if exam.results_published and evaluation and evaluation.status == "Submitted":
            result_available = True

        data.append({
            "booking_id": booking.id,
            "exam_name": exam.exam_name,
            "course_name": exam.course.course_name,
            "date": slot.date.strftime("%Y-%m-%d"),
            "start_time": slot.start_time.strftime("%H:%M"),
            "booking_status": "Completed" if result_available else booking.status,
            "result_available": result_available
        })

    return jsonify({"data": data})


@app.route("/student/results", methods=["GET"])
@jwt_required()
def student_results():

    import json
    import ast

    student_id = int(get_jwt_identity())

    student = User.query.get(student_id)

    if not student or student.role != "Student":
        return jsonify({"message": "Student not found"})

    bookings = Booking.query.filter_by(
        student_id=student_id
    ).all()

    data = []

    for booking in bookings:
        exam = booking.slot.examination

        if not exam.results_published:
            continue

        evaluation = Evaluation.query.filter_by(
            booking_id=booking.id,
            status="Submitted"
        ).first()

        if not evaluation:
            continue

        marks_data = []

        if evaluation.marks:
            try:
                marks_data = json.loads(evaluation.marks)
            except:
                marks_data = ast.literal_eval(evaluation.marks)

        rubric_data = []

        for item in marks_data:
            rubric = ExaminationRubric.query.get(item["rubric_id"])

            if rubric:
                rubric_data.append({
                    "criterion_name": rubric.criterion_name,
                    "maximum_marks": rubric.maximum_marks,
                    "weightage": rubric.weightage,
                    "marks_obtained": item["marks"]
                })

        data.append({
            "evaluation_id": evaluation.id,
            "exam_name": exam.exam_name,
            "course_name": exam.course.course_name,
            "exam_date": booking.slot.date.strftime("%Y-%m-%d"),
            "total_marks": evaluation.total_marks,
            "remarks": evaluation.remarks,
            "evaluation_date": evaluation.evaluation_date.strftime("%Y-%m-%d")
                               if evaluation.evaluation_date else "",
            "rubrics": rubric_data
        })

    return jsonify({"data": data})






def create_database():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="Admin").first()

        if admin is None:
            admin = User(
                name="Admin", email="admin@emp.com", password=generate_password_hash("admin123"), role="Admin"
            )

            db.session.add(admin)
            db.session.commit()

            print("Admin created successfully.")

        else:
            print("Admin already exists.")

        # Enforce max 1 seat per examiner slot on existing data
        for slot in ExaminationSlot.query.all():
            _sync_slot_seats(slot)
        db.session.commit()

        print("Database setup completed.")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
