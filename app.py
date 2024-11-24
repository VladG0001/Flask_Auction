from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, LotForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] =
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    middle_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    photo = db.Column(db.String(150))

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image = db.Column(db.String(150))
    category = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='lots')

class SavedLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    user = db.relationship('User', backref='saved_lots')
    lot = db.relationship('Lot', backref='saved_by_users')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    query = request.args.get('query')
    if query:
        lots = Lot.query.filter(Lot.title.contains(query)).all()
    else:
        lots = Lot.query.all()
    return render_template('home.html', lots=lots)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                        middle_name=form.middle_name.data, email=form.email.data,
                        password=hashed_password, photo=form.photo.data.filename)

        if form.photo.data:
            photo_path = os.path.join('static/photos', form.photo.data.filename)
            form.photo.data.save(photo_path)
            new_user.photo = form.photo.data.filename

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/save_lot/<int:lot_id>', methods=['POST'])
@login_required
def save_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    saved_lot = SavedLot.query.filter_by(user_id=current_user.id, lot_id=lot.id).first()
    if not saved_lot:
        new_saved_lot = SavedLot(user_id=current_user.id, lot_id=lot.id)
        db.session.add(new_saved_lot)
        db.session.commit()
        flash(f'Лот "{lot.title}" збережено!')
    else:
        flash(f'Лот "{lot.title}" вже збережений.')

    return redirect(url_for('home'))

@app.route('/saved_lots')
@login_required
def saved_lots():
    saved_lots = SavedLot.query.filter_by(user_id=current_user.id).all()
    return render_template('saved_lots.html', saved_lots=saved_lots)

@app.route('/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    form = LotForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = form.image.data
            image_path = os.path.join('static/images', image_file.filename)
            image_file.save(image_path)
            new_lot = Lot(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                image=image_file.filename,
                user_id=current_user.id
            )
            db.session.add(new_lot)
            db.session.commit()
            return redirect(url_for('profile'))
    return render_template('create_lot.html', form=form)


@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = Lot.query.get(lot_id)
    if lot:
        db.session.delete(lot)
        db.session.commit()
        flash('Лот успішно видалено.', 'success')
    else:
        flash('Лот не знайдено.', 'danger')

    return redirect(url_for('your_lots_page'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/lot/<int:lot_id>')
def view_lot(lot_id):
    lot = Lot.query.get(lot_id)
    if not lot:
        return "Лот не знайдено", 404
    return render_template('view_lot.html', lot=lot)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
