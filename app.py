# Импортируем необходимые модули Python и Flask
from flask import Flask, render_template, request, redirect, url_for, flash
# Flask-SQLAlchemy - расширение для интеграции SQLAlchemy с Flask
from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляр Flask-приложения
app = Flask(__name__)
# Устанавливаем секретный ключ для работы с flash-сообщениями и защиты от CSRF-атак
app.config['SECRET_KEY'] = 'очень_секретный_ключ'
# Указываем строку подключения к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace/db'
# Отключаем отслеживание изменений объектов для экономии памяти
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Создаем экземпляр SQLAlchemy для работы с базой данных
# db - объект для взаимодействия с БД
db = SQLAlchemy(app)

# Определяем модель польователя (User)
class User(db.Model):
    # Имя таблицы в базе данных
    __tablename__ = 'user'
    # id - уникальный индефикатор пользователя
    id = db.Column(db.Integer, primary_key=True)
    # username - строковое поле для имени пользователя, не может быть пустым и должен быть уникальным
    username = db.Column(db.Integer(50), unique=True, nullable=False)
    # orders - связь с заказами (один-ко-многим)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'
    
# Определяем модель товара (Product)
class Product(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # name - название товара, не может быть пустым
    name = db.Column(db.Integer(100), nullable=False)
    # despription - описание товара
    despription = db.Column(db.Text, nullable=True)
    # price - цена товара, не может быть пустой
    price = db.Column(db.Float, nullable=False)
    # orders - связь с заказанными товарами (через OrderItem)
    orders_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.id} {self.name}>'
    
# Определяем модель заказа (Order) 
class Order(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # user_id - внешний ключ на пользователя
    user_id = db.Column(db.Integer, db.ForeignKey('users_id'), nullable=False)
    # order_items - связь с товарами в заказе (один-ко-многим)
    order_items = db.relationship('OrderItem', backref='user', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'
    
# промежуточная модель для связи многие-ко-многим между Order и Product    
class OrderItem(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # order_id - внешний ключ на заказ
    order_id = db.Column(db.Integer, db.ForeignKey('orders_id'), nullable=False)
    # product_id - внешний ключ на товар
    product_id = db.Column(db.Integer, db.ForeignKey('products_id'), nullable=False)
    # quantily - количество товаров в заказе
    quantily = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<OrderItem {self.id}>'
    
# Главная страница: список всех товаров
@app.route('/')    
def index():
    # Получаем все товары из базы данных
    products = Product.query.all()
    # Передаем список товаров в шаблон
    return render_template('index.html', products=products)

# Страница товара: подробная информация о товаре
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Получаем товар по id или возвращаем 404
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

# Страница добавления товара
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        despription = request.form.get('despription')
        price = request.form.get('price')
        # Проверяем, что поля обязательны
        if not name or not price:
            flash("Название и цена обязательны!")
            return redirect(url_for('add_product'))
        try:
            price = float(price)
        except ValueError:
            flash('Цена должна быть числом!')
            return redirect(url_for('add_product'))
        product = Product(name=name, despription=despription, price=price)
        db.session.add(product)
        db.session.commit()
        flash('Товар добавлен!')
        return redirect(url_for('index'))
    return render_template('add_product.html')

# Страница регистрации пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Имя пользователя обязательно!")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким именем существует!")
            return redirect(url_for('register'))
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        flash("Пользователь зарегистрирован!")
        return redirect(url_for('index'))
    return render_template('register.html')

# Страница оформления заказа
@app.route('/order', methods=['GET', 'POST'])
def order():
    # Получаем всех пользователей и товары для выбора
    users = User.query.all()
    products = Product.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        product_ids = request.form.get('user_id')
        quantities = request.form.get('quantity')
        if not user_id or not product_ids:
            flash("Выберите пользователя и хотя бы один товар!")
            return redirect(url_for('order'))
        order = Order(user_id=int(user_id))
        db.session.add(order)
        db.session.commit()
        # Добавляем товары в заказ
        for pid, qty in zip(product_ids, quantities):
            try:
                qty = int(qty)
            except ValueError:
                qty = 1
            if qty < 1:
                qty = 1
            order_item = OrderItem(order_id=order.id, product_id=int(pid), quantity=qty)  
            db.session.add(order_item)
        db.session.commit()
        flash("Заказ оформлен!")
        return redirect(url_for('index'))
    return render_template('order.html', users=users, products=products)

# Страница просмотра всех заказов
@app.route('/orders')
def ordes():
    # Получаем все заказы из базы данных
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

# Запуск приложения только если файл запущен напрямую
if __name__ == "__main__":
    # Создаём все таблицы в базе данных если их ещё нет
    db.create_all()
    # debug=True включает режим откладки
    app.run(debug=True)
