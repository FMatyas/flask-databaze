from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Název', validators=[DataRequired(), Length(max=100)])
    price = DecimalField('Cena', places=2, validators=[DataRequired(), NumberRange(min=0)])
    description = StringField('Popis', validators=[Length(max=200)])
    dph = SelectField('DPH', choices=[('0','0%'), ('15','15%')], coerce=int, default=15)
