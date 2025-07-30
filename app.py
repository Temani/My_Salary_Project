from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
import os
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Shift, TaxExemptCity, Child
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import locale
import calendar
from datetime import datetime, timedelta, date as dt_date
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

# Load environment variables from .env file
load_dotenv()

# אתחול Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# אתחול Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
# אתחול Flask-Bootstrap
bootstrap = Bootstrap5(app)

# אתחול Flask-Login
login_manager = LoginManager()
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

login_manager.init_app(app)
locale.setlocale(locale.LC_ALL, 'he_IL.UTF-8')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # קבלת נתוני המשתמש מהטופס
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('אנא מלא את כל השדות', 'danger')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('שם משתמש לא נמצא', 'danger')
            return redirect(url_for('login'))
        
        if user and check_password_hash(user.password, password):
            flash('התחברת בהצלחה!', 'success')
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('שם משתמש או סיסמה שגויים', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not email or not password or not username:
            flash('אנא מלא את כל השדות', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('הסיסמה חייבת להכיל לפחות 6 תווים', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('שם המשתמש או האימייל כבר קיימים במערכת', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        try:
            new_user = User(
                username=username,
                email=email,
                password=password_hash
            )
            db.session.add(new_user)
            db.session.commit()

            flash('נרשמת בהצלחה! ברוך הבא!', 'success')
            return redirect(url_for('login'))  # שים לב לשם ה-endpoint לפי ה-blueprint

        except Exception as e:
            print(f"שגיאה בעת רישום: {e}")
            flash('שגיאה ברישום, אנא נסה שוב מאוחר יותר.', 'danger')

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)
    flash('התנתקת בהצלחה!', 'success')
    return redirect(url_for('login'))


@app.route('/shifts', methods=['GET', 'POST'])
@login_required
def manage_shifts():
    user = current_user
    if request.method == 'POST':
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        note = request.form.get('note')

        if not date_str or not start_time_str or not end_time_str:
            flash('אנא מלא את כל השדות', 'danger')
            return redirect(url_for('manage_shifts'))

        try:
            shift_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()            
            
            new_shift = Shift(
                user_id=user.id,
                date=shift_date,
                start_time=start_time,
                end_time=end_time,
                note=note,
                
            )
            db.session.add(new_shift)
            db.session.commit()
            flash('משמרת נשמרה בהצלחה!', 'success')
        except Exception as e:
            flash(f'שגיאה בשמירת המשמרת: {e}', 'danger')
    
    shifts = Shift.query.filter_by(user_id=current_user.id).order_by(Shift.date.asc()).all()
    if not shifts:
        flash('אין משמרות זמינות', 'info')
    return render_template('shifts.html',user=user, shifts=shifts, get_shift_duration=get_shift_duration)



# חישוב משך המשמרת
def get_shift_duration(shift):
    if not shift.start_time or not shift.end_time or not shift.date:
        return "00:00"

    start_dt = datetime.combine(shift.date, shift.start_time)
    end_dt = datetime.combine(shift.date, shift.end_time)

    # אם שעת הסיום לפני ההתחלה (משמרת חוצה חצות) נוסיף יום לסיום
    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    duration = abs(end_dt - start_dt)  # כאן הערך המוחלט 💡
    total_minutes = duration.total_seconds() // 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    return f"{hours:02d}:{minutes:02d}"

def calculate_shift_pay(hours, hourly_rate):
    tiers = {
        "100%": 0,
        "125%": 0,
        "150%": 0,
        "200%": 0
    }
    pay = 0

    if hours <= 8:
        tiers["100%"] = hours
        pay += hours * hourly_rate
    elif hours <= 10:
        tiers["100%"] = 8
        tiers["125%"] = hours - 8
        pay += 8 * hourly_rate + (hours - 8) * hourly_rate * 1.25
    elif hours <= 12:
        tiers["100%"] = 8
        tiers["125%"] = 2
        tiers["150%"] = hours - 10
        pay += 8 * hourly_rate + 2 * hourly_rate * 1.25 + (hours - 10) * hourly_rate * 1.5
    else:
        tiers["100%"] = 8
        tiers["125%"] = 2
        tiers["150%"] = 2
        tiers["200%"] = hours - 12
        pay += (
            8 * hourly_rate +
            2 * hourly_rate * 1.25 +
            2 * hourly_rate * 1.5 +
            (hours - 12) * hourly_rate * 2
        )

    return round(pay, 2), tiers

@app.route('/delete_shift/<int:shift_id>', methods=['POST'])
@login_required
def delete_shift(shift_id):
    shift = Shift.query.get_or_404(shift_id)

    # בדיקה אם המשתמש הנוכחי הוא הבעלים של המשמרת
    if shift.user_id != current_user.id:
        flash('אין לך הרשאה למחוק משמרת זו', 'danger')
        return redirect(url_for('manage_shifts'))
    # מחיקת המשמרת
    db.session.delete(shift)
    db.session.commit()
    flash('המשמרת נמחקה בהצלחה!', 'success')
    return redirect(url_for('manage_shifts'))



@app.route("/personal_info", methods=["GET", "POST"])
@login_required
def personal_info():
    if request.method == "POST":
        current_user.birth_date = request.form["birth_date"]
        current_user.gender = request.form["gender"]
        current_user.marital_status = request.form["marital_status"]
        current_user.city = request.form["city"]
        current_user.hourly_wage = request.form.get("hourly_wage", type=float) or None
        current_user.has_degree = "has_degree" in request.form
        current_user.degree_year = request.form.get("degree_year") or None

        # מחיקת ילדים ישנים (אם יש)
        Child.query.filter_by(user_id=current_user.id).delete()

        for date in request.form.getlist("child_birthdates"):
            if date:
                child = Child(birth_date=date, parent=current_user)
                db.session.add(child)

        db.session.commit()
        flash("הפרטים עודכנו בהצלחה!", "success")
        return redirect(url_for("personal_info"))
    current_date = dt_date.today().isoformat()

    return render_template("personal_info.html", user=current_user, current_date = current_date
)

@app.route('/api/cities')
def get_cities():
    cities = TaxExemptCity.query.with_entities(TaxExemptCity.city_name).order_by(TaxExemptCity.city_name).all()
    city_list = [city[0] for city in cities]
    return jsonify(city_list)

@app.route('/shift_details/<int:shift_id>', methods=['GET', 'POST'])
@login_required
def shift_details(shift_id):
    shift = Shift.query.get_or_404(shift_id)
    # בדיקה אם המשתמש הנוכחי הוא הבעלים של המשמרת
    if shift.user_id != current_user.id:
        flash('אין לך הרשאה לצפות בפרטי משמרת זו', 'danger')
        return redirect(url_for('manage_shifts'))
    
    duration_str = get_shift_duration(shift)
    hours, minutes = map(int, duration_str.split(':'))
    total_hours = hours + minutes / 60
    total_salary, tiers = calculate_shift_pay(total_hours, current_user.hourly_wage)
    day_of_week = calendar.day_name[shift.date.weekday()]

    return render_template('shift_details.html', shift=shift,get_shift_duration=get_shift_duration,
                            duration_str=duration_str, total_salary=round(total_salary, 2), tiers=tiers, day_of_week=day_of_week)

if __name__ == '__main__': 
    app.run(debug=True)