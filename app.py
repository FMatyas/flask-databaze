from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///products.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-to-a-secure-random-value')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
# Flask-Migrate
migrate = Migrate(app, db)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    dph = db.Column(db.Integer, nullable=False, default=15)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('list.html', products=products)

from forms import ProductForm

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=float(form.price.data),
            description=form.description.data,
            dph=form.dph.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Produkt přidán', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, product=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash('Produkt aktualizován', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, product=product)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produkt smazán', 'info')
    return redirect(url_for('index'))

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)
