from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# MariaDB Configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_USER = os.environ.get('DB_USER', 'botcreator')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'botcreator123')
DB_NAME = os.environ.get('DB_NAME', 'botcreator')

# MariaDB connection string
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_size': 10,
    'max_overflow': 20
}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    google_id = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    bots = db.relationship('Bot', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def bot_count(self):
        return len([bot for bot in self.bots if bot.is_active])
    
    @property
    def last_activity(self):
        if self.bots:
            return max(bot.updated_at for bot in self.bots if bot.is_active)
        return self.created_at

class Bot(db.Model):
    __tablename__ = 'bots'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(200), nullable=True)
    config = db.Column(db.Text, nullable=False)  # JSON string
    python_code = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    def __repr__(self):
        return f'<Bot {self.name}>'

class BotSession(db.Model):
    __tablename__ = 'bot_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='bot_sessions')
    
    def __repr__(self):
        return f'<BotSession {self.id} for user {self.user_id}>'

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data instead of JSON
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([email, password, name, confirm_password]):
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже зарегистрирован', 'error')
            return render_template('register.html')
        
        try:
            user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Регистрация успешна! Добро пожаловать!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте еще раз.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data instead of JSON
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Введите email и пароль', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Неверный email или пароль', 'error')
        return render_template('login.html')
    
    return render_template('login.html')

@app.route('/google-login')
def google_login():
    # Google OAuth flow would be implemented here
    # For now, we'll simulate it
    return redirect(url_for('google_callback'))

@app.route('/google-callback')
def google_callback():
    # In a real implementation, this would handle the OAuth callback
    # For demo purposes, we'll create a mock user
    mock_user = User.query.filter_by(email='demo@google.com').first()
    if not mock_user:
        mock_user = User(
            email='demo@google.com',
            name='Demo Google User',
            google_id='google_123'
        )
        db.session.add(mock_user)
        db.session.commit()
    
    login_user(mock_user)
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_bots = Bot.query.filter_by(user_id=current_user.id, is_active=True).order_by(Bot.created_at.desc()).all()
    return render_template('dashboard.html', bots=user_bots)

@app.route('/create-bot')
@login_required
def create_bot():
    return render_template('create_bot.html')

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_active=True).count()
    total_bots = Bot.query.filter_by(is_active=True).count()
    total_sessions = BotSession.query.count()
    admin_count = User.query.filter_by(is_active=True, is_admin=True).count()
    
    # Recent registrations
    recent_users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).limit(5).all()
    
    # Recent bots
    recent_bots = Bot.query.filter_by(is_active=True).order_by(Bot.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_bots=total_bots,
                         total_sessions=total_sessions,
                         admin_count=admin_count,
                         recent_users=recent_users,
                         recent_bots=recent_bots)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    user_bots = Bot.query.filter_by(user_id=user_id, is_active=True).order_by(Bot.created_at.desc()).all()
    return render_template('admin/user_detail.html', user=user, bots=user_bots)

@app.route('/admin/bots')
@login_required
@admin_required
def admin_bots():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    bots = Bot.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/bots.html', bots=bots)

@app.route('/admin/stats')
@login_required
@admin_required
def admin_stats():
    # Get statistics
    total_users = User.query.filter_by(is_active=True).count()
    total_bots = Bot.query.filter_by(is_active=True).count()
    total_sessions = BotSession.query.count()
    
    # Recent registrations
    recent_users = User.query.filter_by(is_active=True).order_by(User.created_at.desc()).limit(10).all()
    
    # Top users by bot count
    top_users = db.session.query(
        User.name,
        User.email,
        db.func.count(Bot.id).label('bot_count')
    ).outerjoin(Bot, (User.id == Bot.user_id) & (Bot.is_active == True)).group_by(User.id).order_by(db.func.count(Bot.id).desc()).limit(10).all()
    
    # Monthly registrations
    monthly_stats = db.session.query(
        db.func.date_format(User.created_at, '%Y-%m').label('month'),
        db.func.count(User.id).label('count')
    ).filter(User.created_at >= datetime.utcnow().replace(day=1) - timedelta(days=365)).group_by(db.func.date_format(User.created_at, '%Y-%m')).order_by('month').all()
    
    return render_template('admin/stats.html', 
                         total_users=total_users,
                         total_bots=total_bots,
                         total_sessions=total_sessions,
                         recent_users=recent_users,
                         top_users=top_users,
                         monthly_stats=monthly_stats)

@app.route('/api/admin/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin and user.id == current_user.id:
        return jsonify({'error': 'Нельзя деактивировать свой аккаунт администратора'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_active': user.is_active,
        'message': f'Пользователь {"активирован" if user.is_active else "деактивирован"}'
    })

@app.route('/api/admin/toggle-admin-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Нельзя изменить права администратора для своего аккаунта'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_admin': user.is_admin,
        'message': f'Права администратора {"предоставлены" if user.is_admin else "отозваны"}'
    })

@app.route('/api/admin/delete-user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin and user.id == current_user.id:
        return jsonify({'error': 'Нельзя удалить свой аккаунт администратора'}), 400
    
    # Soft delete - mark as inactive
    user.is_active = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Пользователь удален'})

@app.route('/api/save-bot-session', methods=['POST'])
@login_required
def save_bot_session():
    data = request.get_json()
    
    # Save to database instead of session
    existing_session = BotSession.query.filter_by(user_id=current_user.id).first()
    
    if existing_session:
        existing_session.session_data = json.dumps(data)
        existing_session.updated_at = datetime.utcnow()
    else:
        new_session = BotSession(
            user_id=current_user.id,
            session_data=json.dumps(data)
        )
        db.session.add(new_session)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/get-bot-session')
@login_required
def get_bot_session():
    session_record = BotSession.query.filter_by(user_id=current_user.id).first()
    if session_record:
        return jsonify(json.loads(session_record.session_data))
    return jsonify({})

@app.route('/api/save-bot', methods=['POST'])
@login_required
def save_bot():
    data = request.get_json()
    
    bot = Bot(
        name=data['name'],
        token=data.get('token', ''),
        config=json.dumps(data['config']),
        python_code=data['python_code'],
        user_id=current_user.id
    )
    
    db.session.add(bot)
    db.session.commit()
    
    # Clear session data
    session_record = BotSession.query.filter_by(user_id=current_user.id).first()
    if session_record:
        db.session.delete(session_record)
        db.session.commit()
    
    return jsonify({'success': True, 'bot_id': bot.id})

@app.route('/api/generate-python-code', methods=['POST'])
@login_required
def generate_python_code():
    data = request.get_json()
    config = data['config']
    
    # Generate Python code based on bot configuration
    python_code = generate_bot_code(config)
    
    return jsonify({'python_code': python_code})

@app.route('/api/delete-bot/<int:bot_id>', methods=['DELETE'])
@login_required
def delete_bot(bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Soft delete
    bot.is_active = False
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/download-bot/<int:bot_id>')
@login_required
def download_bot(bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    return jsonify({
        'name': bot.name,
        'python_code': bot.python_code,
        'config': json.loads(bot.config)
    })

def generate_bot_code(config):
    """Generate Python code for the Telegram bot based on configuration"""
    
    code = '''import telebot
from telebot import types
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token - replace with your actual token
TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

# Bot configuration
BOT_NAME = "{}"
BOT_DESCRIPTION = "{}"

# Error handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # This will be overridden by specific handlers
        pass
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        bot.reply_to(message, "Sorry, something went wrong. Please try again later.")

'''
    
    # Add handlers based on configuration
    if config.get('welcome_message'):
        code += '''
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle /start command"""
    try:
        welcome_text = """{}
        
Welcome to {}! I'm here to help you.
        """.format(BOT_DESCRIPTION, BOT_NAME)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Help"), types.KeyboardButton("About"))
        
        bot.reply_to(message, welcome_text, reply_markup=markup)
        logger.info(f"User {message.from_user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in welcome handler: {e}")
        bot.reply_to(message, "Welcome! I'm here to help you.")
'''
    
    if config.get('help_command'):
        code += '''
@bot.message_handler(commands=['help'])
def send_help(message):
    """Handle /help command"""
    try:
        help_text = """Available commands:
/start - Start the bot
/help - Show this help message
/about - About the bot
        """
        bot.reply_to(message, help_text)
        logger.info(f"User {message.from_user.id} requested help")
    except Exception as e:
        logger.error(f"Error in help handler: {e}")
        bot.reply_to(message, "Here's how to use me...")
'''
    
    if config.get('about_command'):
        code += '''
@bot.message_handler(commands=['about'])
def send_about(message):
    """Handle /about command"""
    try:
        about_text = """{}
        
This bot was created using Bot Creator Platform.
        """.format(BOT_DESCRIPTION)
        bot.reply_to(message, about_text)
        logger.info(f"User {message.from_user.id} requested about info")
    except Exception as e:
        logger.error(f"Error in about handler: {e}")
        bot.reply_to(message, "I'm a helpful bot created with Bot Creator Platform.")
'''
    
    # Add custom responses
    if config.get('custom_responses'):
        for i, response in enumerate(config['custom_responses']):
            trigger = response.get('trigger', '')
            reply = response.get('reply', '')
            if trigger and reply:
                code += '''
@bot.message_handler(func=lambda message: "{}" in message.text.lower())
def custom_response_{}(message):
    """Custom response to: {}"""
    try:
        bot.reply_to(message, "{}")
        logger.info(f"User {message.from_user.id} triggered custom response: {}")
    except Exception as e:
        logger.error(f"Error in custom response handler: {e}")
        bot.reply_to(message, "{}")
'''.format(trigger, i, trigger, reply, trigger, reply)
    
    # Add echo functionality if enabled
    if config.get('echo_enabled'):
        code += '''
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Echo all messages"""
    try:
        bot.reply_to(message, message.text)
        logger.info(f"User {message.from_user.id} sent: {message.text}")
    except Exception as e:
        logger.error(f"Error in echo handler: {e}")
        bot.reply_to(message, "Sorry, I couldn't process your message.")
'''
    
    # Add main execution
    code += '''
if __name__ == "__main__":
    logger.info(f"Starting {BOT_NAME}...")
    print(f"Starting {BOT_NAME}...")
    print("Bot is running. Press Ctrl+C to stop.")
    
    try:
        bot.polling(none_stop=True, timeout=60)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("Bot stopped.")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
        print(f"Bot stopped due to error: {e}")
'''
    
    return code.format(
        config.get('name', 'My Bot'),
        config.get('description', 'A helpful Telegram bot'),
        config.get('welcome_message', 'Hello!'),
        config.get('name', 'My Bot')
    )

@app.cli.command('init-db')
def init_db():
    """Initialize the database with all tables."""
    db.create_all()
    
    # Create default admin user if not exists
    admin_user = User.query.filter_by(email='admin').first()
    if not admin_user:
        admin_user = User(
            email='admin',
            name='Administrator',
            password_hash=generate_password_hash('password'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin / password")
    
    print("Database initialized successfully!")

@app.cli.command('create-admin')
def create_admin():
    """Create an admin user."""
    email = input("Enter admin email: ")
    name = input("Enter admin name: ")
    password = input("Enter admin password: ")
    
    if User.query.filter_by(email=email).first():
        print("User already exists!")
        return
    
    admin = User(
        email=email,
        name=name,
        password_hash=generate_password_hash(password),
        is_admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user {email} created successfully!")

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            
            # Create default admin user if not exists
            admin_user = User.query.filter_by(email='admin').first()
            if not admin_user:
                admin_user = User(
                    email='admin',
                    name='Administrator',
                    password_hash=generate_password_hash('password'),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin / password")
            
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            print("Please check your MariaDB connection and credentials.")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
