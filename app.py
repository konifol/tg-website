from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_creator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bots = db.relationship('Bot', backref='user', lazy=True)

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(200), nullable=True)
    config = db.Column(db.Text, nullable=False)  # JSON string
    python_code = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
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
    user_bots = Bot.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bots=user_bots)

@app.route('/create-bot')
@login_required
def create_bot():
    return render_template('create_bot.html')

@app.route('/api/save-bot-session', methods=['POST'])
@login_required
def save_bot_session():
    data = request.get_json()
    session['bot_config'] = data
    return jsonify({'success': True})

@app.route('/api/get-bot-session')
@login_required
def get_bot_session():
    return jsonify(session.get('bot_config', {}))

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
    
    # Clear session
    session.pop('bot_config', None)
    
    return jsonify({'success': True, 'bot_id': bot.id})

@app.route('/api/generate-python-code', methods=['POST'])
@login_required
def generate_python_code():
    data = request.get_json()
    config = data['config']
    
    # Generate Python code based on bot configuration
    python_code = generate_bot_code(config)
    
    return jsonify({'python_code': python_code})

def generate_bot_code(config):
    """Generate Python code for the Telegram bot based on configuration"""
    
    code = '''import telebot
from telebot import types
import os

# Bot token - replace with your actual token
TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

# Bot configuration
BOT_NAME = "{}"
BOT_DESCRIPTION = "{}"

'''
    
    # Add handlers based on configuration
    if config.get('welcome_message'):
        code += '''
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle /start command"""
    welcome_text = """{}
    
Welcome to {}! I'm here to help you.
    """.format(BOT_DESCRIPTION, BOT_NAME)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Help"), types.KeyboardButton("About"))
    
    bot.reply_to(message, welcome_text, reply_markup=markup)
'''
    
    if config.get('help_command'):
        code += '''
@bot.message_handler(commands=['help'])
def send_help(message):
    """Handle /help command"""
    help_text = """Available commands:
/start - Start the bot
/help - Show this help message
/about - About the bot
    """
    bot.reply_to(message, help_text)
'''
    
    if config.get('about_command'):
        code += '''
@bot.message_handler(commands=['about'])
def send_about(message):
    """Handle /about command"""
    about_text = """{}
    
This bot was created using Bot Creator Platform.
    """.format(BOT_DESCRIPTION)
    bot.reply_to(message, about_text)
'''
    
    # Add custom responses
    if config.get('custom_responses'):
        for response in config['custom_responses']:
            trigger = response.get('trigger', '')
            reply = response.get('reply', '')
            if trigger and reply:
                code += '''
@bot.message_handler(func=lambda message: "{}" in message.text.lower())
def custom_response_{}(message):
    """Custom response to: {}"""
    bot.reply_to(message, "{}")
'''.format(trigger, trigger.replace(' ', '_'), trigger, reply)
    
    # Add echo functionality if enabled
    if config.get('echo_enabled'):
        code += '''
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Echo all messages"""
    bot.reply_to(message, message.text)
'''
    
    # Add main execution
    code += '''
if __name__ == "__main__":
    print(f"Starting {BOT_NAME}...")
    print("Bot is running. Press Ctrl+C to stop.")
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("Bot stopped.")
'''
    
    return code.format(
        config.get('name', 'My Bot'),
        config.get('description', 'A helpful Telegram bot'),
        config.get('welcome_message', 'Hello!'),
        config.get('name', 'My Bot')
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)