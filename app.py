from flask import Flask, render_template, redirect, url_for, request, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# אתחול דאטה Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# אתחול Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# אתחול Flask-Bootstrap
bootstrap = Bootstrap5(app)


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # קבלת נתוני המשתמש מהטופס
        email = request.form['email']
        password = request.form['password']
        
        try:
            # התחברות למשתמש
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            if response.user:
                # אם ההתחברות הצליחה, נודיע למשתמש
                flash('התחברת בהצלחה!', 'success')
                return redirect(url_for('home'))
            else:
                flash('התחברות נכשלה, אנא נסה שוב.', 'danger')
        except Exception as e:
            print(f"Error during login: {e}")
            flash('אירעה שגיאה במהלך ההתחברות, אנא נסה שוב.', 'danger')
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # קבלת נתוני המשתמש מהטופס
        email = request.form.get('email')
        password = request.form.get('password')
        
        # בדיקת תקינות נתונים
        if not email or not password:
            flash('אנא מלא את כל השדות', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('הסיסמה חייבת להכיל לפחות 6 תווים', 'danger')
            return render_template('register.html')
        
        try: 
            # רישום משתמש חדש - הטריגר יצור אוטומטית רשומה ב-work_data
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            if response.user:
                # הטריגר כבר יצר רשומה ב-work_data אוטומטית!
                flash('נרשמת בהצלחה! בדוק את האימייל שלך לאישור החשבון.', 'success')
                return redirect(url_for('login'))
            else:
                flash('הרשמה נכשלה, אנא נסה שוב.', 'danger')
                
        except Exception as e:
            print(f"Error during registration: {e}")
            
            # הודעות שגיאה מותאמות
            error_message = str(e).lower()
            if 'already registered' in error_message or 'already exists' in error_message:
                flash('המשתמש כבר קיים במערכת', 'danger')
            elif 'invalid email' in error_message:
                flash('כתובת אימייל לא תקינה', 'danger')
            elif 'weak password' in error_message or 'password' in error_message:
                flash('הסיסמה חלשה מדי. השתמש בסיסמה חזקה יותר.', 'danger')
            else:
                flash('שגיאה ברישום, אנא נסה שוב מאוחר יותר.', 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    try:
        # התנתקות מהמשתמש
        supabase.auth.sign_out()
        flash('התנתקת בהצלחה!', 'success')
    except Exception as e:
        print(f"Error during logout: {e}")
        flash('אירעה שגיאה במהלך ההתנתקות, אנא נסה שוב.', 'danger')
    return redirect(url_for('home'))

@app.route('/data', methods=['GET', 'POST'])
def get_data():
    data = supabase.table('users').select('*').execute()
    return render_template('data.html', data=data.data)

if __name__ == '__main__': 
    app.run(debug=True)