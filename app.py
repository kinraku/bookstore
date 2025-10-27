import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from wtforms import Form, SelectField, StringField, IntegerField, FloatField, DateField, TextAreaField
from wtforms.validators import InputRequired, NumberRange

# ждем пока бд запустится
time.sleep(10)
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# повторяем модели
# тип пользователя
class UserType(db.Model):
    __tablename__ = 'user_type'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), nullable=False)
    users = db.relationship('Users', backref='user_type', lazy=True)

# пользователь
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'))
    username = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    addresses = db.relationship('Address', backref='user', lazy=True)
    carts = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

# адрес
class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    address_type = db.Column(db.String(50))
    street = db.Column(db.String(150))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    house = db.Column(db.String(50))
    country = db.Column(db.String(100))

# товар
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0)
    product_type = db.Column(db.String(50))
    book = db.relationship('Book', backref='product', uselist=False, lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

# книга
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(150))
    publish_date = db.Column(db.Date)
    description = db.Column(db.Text)
    genre = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=0)
    pages = db.Column(db.Integer)
    reserved_quantity = db.Column(db.Integer, default=0)
    authors = db.relationship('Author', secondary='book_author', backref='books', lazy=True)

# автор
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    country = db.Column(db.String(100))
    biography = db.Column(db.Text)

# соотношение книга-автор
book_author = db.Table('book_author', db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
                       )

# корзина
class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('CartItem', backref='cart', lazy=True)

# элемент корзины
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)

# заказ
class Order(db.Model):
    __tablename__ = 'order_table'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    payment_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50), default='обрабатывается')
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    delivery_address = db.relationship('Address', foreign_keys=[delivery_address_id])
    payment_address = db.relationship('Address', foreign_keys=[payment_address_id])
    items = db.relationship('OrderItem', backref='order', lazy=True)

# позиции заказа
class OrderItem(db.Model):
    __tablename__ = 'order_item'
    order_id = db.Column(db.Integer, db.ForeignKey('order_table.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Numeric(10, 2))

# возвращает путь к книге для шаблонов
def get_book_cover_path(book):
    if not book or not book.id:
        return None
    # проверяем файлы по шаблону book_{id}.*
    for ext in ['jpg', 'jpeg', 'png', 'gif']:
        filename = f"book_{book.id}.{ext}"
        full_path = os.path.join('static/uploads/books', filename)
        if os.path.exists(full_path):
            return f"uploads/books/{filename}"
    return None

# защита админки
class AdminModelView(ModelView):
    def is_accessible(self):
        user = get_current_user()
        return user and user.user_type_id == 1
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class BookForm(Form):
    title = StringField('Название', validators=[InputRequired()])
    isbn = StringField('ISBN', validators=[InputRequired()])
    publisher = StringField('Издатель')
    publish_date = DateField('Дата публикации')
    description = TextAreaField('Описание')
    genre = StringField('Жанр')
    quantity = IntegerField('Количество', validators=[NumberRange(min=0)])
    pages = IntegerField('Страницы', validators=[NumberRange(min=1)])
    reserved_quantity = IntegerField('Зарезервировано', validators=[NumberRange(min=0)])
    price = FloatField('Цена', validators=[NumberRange(min=0)])
    discount = FloatField('Скидка (%)', validators=[NumberRange(min=0, max=100)])
    authors = SelectField('Авторы', coerce=int, widget=Select2Widget())

class BookModelView(AdminModelView):

    form_columns = [
        'title', 'isbn', 'publisher', 'publish_date', 'description',
        'genre', 'quantity', 'pages', 'reserved_quantity', 'authors'
    ]

    def on_model_change(self, form, model, is_created):

        return super().on_model_change(form, model, is_created)
    column_list = ['id', 'title', 'isbn', 'genre', 'quantity']
    # показ. превью обложки
    def _cover_formatter(view, context, model, name):
        cover_path = get_book_cover_path(model)
        if cover_path:
            return f'<img src="/static/{cover_path}" style="max-height: 50px;">'
        return "Нет обложки"
    column_formatters = {
        'cover': _cover_formatter
    }
    # ковёр меняем на "обложка" в интерфейсе
    column_labels = {
        'cover': 'Обложка'
    }

# админ панель фласка
admin = Admin(app, name='Admin', template_mode='bootstrap3')
admin.add_view(AdminModelView(UserType, db.session))
admin.add_view(AdminModelView(Users, db.session, name='User'))
admin.add_view(AdminModelView(Address, db.session))
admin.add_view(AdminModelView(Product, db.session))
admin.add_view(BookModelView(Book, db.session, name='Book'))
admin.add_view(AdminModelView(Author, db.session))
admin.add_view(AdminModelView(Order, db.session))
admin.add_view(AdminModelView(OrderItem, db.session))

# ошибки и ошибка пэйдж
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Произошла ошибка: {str(e)}")
    return render_template('error.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Страница не найдена"), 404

@app.route('/static/<path:subpath>')
def static_files(subpath):
    return send_from_directory('static', subpath)

def get_current_user():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            return user
    return None

# контекстный процессор
@app.context_processor
def inject_user():
    return {
        'user': get_current_user(),
        'get_book_price_with_discount': get_book_price_with_discount,
        'get_book_cover_path': get_book_cover_path
    }

# возвращает цену книги с уч скидки
def get_book_price_with_discount(book):
    price = float(book.product.price)
    discount = float(book.product.discount or 0)
    if discount > 0:
        return price * (1 - discount / 100)
    return price

# маршруты
@app.route('/')
def index():
    books = Book.query.order_by(func.random()).limit(3).all()
    return render_template('index.html', books=books)

@app.route('/catalog')
def catalog():
    search_query = request.args.get('q', '').strip()
    if search_query:
        search_pattern = f'%{search_query}%'
        books_by_title_or_genre = Book.query.filter(
            Book.title.ilike(search_pattern) |
            Book.genre.ilike(search_pattern)
        ).all()
        author_books = Book.query.join(Book.authors).filter(
            Author.first_name.ilike(search_pattern) |
            Author.last_name.ilike(search_pattern) |
            Author.middle_name.ilike(search_pattern)
        ).all()
        books = list(set(books_by_title_or_genre + author_books))
    else:
        books = Book.query.all()
    return render_template('catalog.html', books=books, search_query=search_query)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/balance')
def balance():
    user = get_current_user()
    if not user:
        flash('Войдите в систему', 'error')
        return redirect(url_for('login'))
    return render_template('balance.html', user=user)

@app.route('/add_balance', methods=['POST'])
def add_balance():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    try:
        amount = float(request.form.get('amount', 0))
        if amount > 0:
            user.balance += amount
            db.session.commit()
            flash(f'Баланс пополнен на {amount} ₽', 'success')
    except ValueError:
        flash('Неверная сумма', 'error')
    return redirect(url_for('balance'))

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    final_price = get_book_price_with_discount(book)
    return render_template('book.html', book=book, final_price=final_price)

@app.route('/author/<int:author_id>')
def author_details(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author.html', author=author)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip()
        user = Users(
            user_type_id=2,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name
        )
        db.session.add(user)
        db.session.commit()
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type_id'] = user.user_type_id
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверные данные', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    user = get_current_user()
    if not user:
        flash('Войдите в систему', 'error')
        return redirect(url_for('login'))
    book = Book.query.get(book_id)
    if not book:
        flash('Книга не найдена', 'error')
        return redirect(url_for('catalog'))
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=book_id).first()
    if cart_item:
        if cart_item.quantity + 1 > book.quantity:
            flash(f'Нельзя добавить больше {book.quantity} шт. книги "{book.title}"', 'error')
            return redirect(request.referrer or url_for('catalog'))
        cart_item.quantity += 1
    else:
        if book.quantity < 1:
            flash('Эта книга временно отсутствует', 'error')
            return redirect(request.referrer or url_for('catalog'))
        cart_item = CartItem(cart_id=cart.id, product_id=book_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash('Книга добавлена в корзину', 'success')
    return redirect(request.referrer or url_for('catalog'))

@app.route('/cart')
def cart():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        return render_template('cart.html', items=[], total=0)
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    total = 0
    items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product and product.book:
            # Используем цену со скидкой
            final_price = get_book_price_with_discount(product.book)
            item_total = final_price * item.quantity
            total += item_total
            items.append({
                'book': product.book,
                'quantity': item.quantity,
                'total': item_total,
                'final_price': final_price,
                'original_price': float(product.price),
                'discount': float(product.discount or 0)
            })
    return render_template('cart.html', items=items, total=total)

@app.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return redirect(url_for('cart'))
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=book_id).first()
    if cart_item:
        new_quantity = int(request.form.get('quantity', 1))
        book = Book.query.get(book_id)
        if new_quantity > book.quantity:
            flash(f'Нельзя заказать больше {book.quantity} шт. книги "{book.title}"', 'error')
        elif new_quantity < 1:
            db.session.delete(cart_item)
            flash('Книга удалена из корзины', 'info')
        else:
            cart_item.quantity = new_quantity
            flash('Количество обновлено', 'success')
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart(book_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(user_id=user.id).first()
    if cart:
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=book_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Книга удалена из корзины', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    payment_address = Address.query.filter_by(user_id=user.id, address_type='payment').first()
    delivery_address = Address.query.filter_by(user_id=user.id, address_type='delivery').first()
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        flash('Ваша корзина пуста', 'error')
        return redirect(url_for('cart'))
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    if not cart_items:
        flash('Ваша корзина пуста', 'error')
        return redirect(url_for('cart'))
    for item in cart_items:
        if item.product.book.quantity < item.quantity:
            flash(
                f'Нельзя заказать {item.quantity} шт. книги "{item.product.book.title}". Доступно: {item.product.book.quantity} шт.',
                'error')
            return redirect(url_for('cart'))
    # расчет общей стоимости с учетом скидок на товары
    total = 0
    items_with_prices = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product and product.book:
            final_price = get_book_price_with_discount(product.book)
            item_total = final_price * item.quantity
            total += item_total
            items_with_prices.append({
                'product': product,
                'book': product.book,
                'quantity': item.quantity,
                'final_price': final_price,
                'item_total': item_total,
                'discount': float(product.discount or 0)
            })
    final_total = total
    # делаем чтобы нельзя было заказать без указания адреса
    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'balance')
        if not payment_address:
            flash('Заполните платежный адрес в профиле для оформления заказа', 'error')
            return redirect(url_for('profile'))
        if not delivery_address:
            flash('Заполните адрес доставки в профиле для оформления заказа', 'error')
            return redirect(url_for('profile'))
        if payment_method == 'balance' and float(user.balance) < final_total:
            flash('Недостаточно средств на балансе', 'error')
            return redirect(url_for('checkout'))
        order = Order(
            user_id=user.id,
            total_amount=final_total,
            payment_method=payment_method,
            delivery_address_id=delivery_address.id,
            payment_address_id=payment_address.id
        )
        db.session.add(order)
        db.session.flush()
        for item in cart_items:
            product = Product.query.get(item.product_id)
            final_price = get_book_price_with_discount(product.book)
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=final_price  # сохраняем цену с учетом скидки
            )
            db.session.add(order_item)
            item.product.book.quantity -= item.quantity
        # пока только баланс
        if payment_method == 'balance':
            user.balance -= final_total
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        flash(f'Заказ успешно оформлен! Номер заказа: #{order.id}', 'success')
        return redirect(url_for('profile'))
    return render_template('checkout.html', user=user, cart_items=items_with_prices, total=total,
                           final_total=final_total, payment_address=payment_address, delivery_address=delivery_address)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = Users.query.get(session['user_id'])
    orders = Order.query.filter_by(user_id=session['user_id']).all()
    payment_address = Address.query.filter_by(user_id=user.id, address_type='payment').first()
    delivery_address = Address.query.filter_by(user_id=user.id, address_type='delivery').first()
    if request.method == 'POST':
        if 'save_personal' in request.form:
            user.first_name = request.form.get('first_name', '')
            user.last_name = request.form.get('last_name', '')
            user.middle_name = request.form.get('middle_name', '')
            user.phone = request.form.get('phone', '')
            db.session.commit()
            flash('Личные данные сохранены', 'success')
        elif 'save_address' in request.form:
            payment_street = request.form.get('payment_street', '').strip()
            payment_city = request.form.get('payment_city', '').strip()
            payment_house = request.form.get('payment_house', '').strip()
            payment_postal_code = request.form.get('payment_postal_code', '').strip()
            payment_country = request.form.get('payment_country', '').strip()
            delivery_street = request.form.get('delivery_street', '').strip()
            delivery_city = request.form.get('delivery_city', '').strip()
            delivery_house = request.form.get('delivery_house', '').strip()
            delivery_postal_code = request.form.get('delivery_postal_code', '').strip()
            delivery_country = request.form.get('delivery_country', '').strip()
            if not payment_street or not payment_city or not payment_house or not payment_country:
                flash(
                    'Заполните поля полностью. Иначе мы не сможем доставить ваш заказ. При отсутствии улицы укажите населённый пункт',
                    'error')
                return redirect(url_for('profile'))
            if not delivery_street or not delivery_city or not delivery_house or not delivery_country:
                flash(
                    'Заполните поля полностью. Иначе мы не сможем доставить ваш заказ. При отсутствии улицы укажите населённый пункт',
                    'error')
                return redirect(url_for('profile'))
            payment_address = Address.query.filter_by(user_id=user.id, address_type='payment').first()
            if payment_address:
                payment_address.street = payment_street
                payment_address.city = payment_city
                payment_address.house = payment_house
                payment_address.postal_code = payment_postal_code
                payment_address.country = payment_country
            else:
                payment_address = Address(
                    user_id=user.id,
                    address_type='payment',
                    street=payment_street,
                    city=payment_city,
                    house=payment_house,
                    postal_code=payment_postal_code,
                    country=payment_country
                )
                db.session.add(payment_address)
            delivery_address = Address.query.filter_by(user_id=user.id, address_type='delivery').first()
            if delivery_address:
                delivery_address.street = delivery_street
                delivery_address.city = delivery_city
                delivery_address.house = delivery_house
                delivery_address.postal_code = delivery_postal_code
                delivery_address.country = delivery_country
            else:
                delivery_address = Address(
                    user_id=user.id,
                    address_type='delivery',
                    street=delivery_street,
                    city=delivery_city,
                    house=delivery_house,
                    postal_code=delivery_postal_code,
                    country=delivery_country
                )
                db.session.add(delivery_address)
            db.session.commit()
            flash('Адреса сохранены', 'success')
        elif 'save_login' in request.form:
            current_password = request.form.get('current_password', '')
            if check_password_hash(user.password_hash, current_password):
                new_username = request.form.get('username', '')
                if new_username != user.username:
                    if Users.query.filter_by(username=new_username).first():
                        flash('Это имя пользователя уже занято', 'error')
                    else:
                        user.username = new_username
                new_password = request.form.get('new_password', '')
                if new_password:
                    user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Данные для входа сохранены', 'success')
            else:
                flash('Неверный текущий пароль', 'error')
    return render_template('profile.html', user=user, orders=orders,
                           payment_address=payment_address, delivery_address=delivery_address)

# создаем админа и типы пользователей
def create_admin_user():
    with app.app_context():
        if not UserType.query.first():
            user_types = [
                UserType(type_name='Администратор'),
                UserType(type_name='Пользователь')
            ]
            db.session.add_all(user_types)
            db.session.commit()

        if not Users.query.filter_by(username='admin').first():
            admin = Users(
                user_type_id=1,
                username='admin',
                email='admin@bookstore.ru',
                password_hash=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='System'
            )
            db.session.add(admin)
            db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        create_admin_user()  
    app.run(debug=True, host='0.0.0.0', port=5000)
