if user and check_password_hash(user.password, password):
            flash('התחברת בהצלחה!', 'success')
            login_user(user)
            return redirect(url_for('home'))