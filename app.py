from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
import os
from openai import OpenAI
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = os.urandom(24)  # For session management
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
socketio = SocketIO(app)  # Initialize SocketIO for real-time chat

Initialize OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# User model - extended with role, profile image, and biodata
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'advisor'
    
    # Profile information
    profile_image = db.Column(db.String(255), default='default-avatar.png')
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    bio = db.Column(db.Text)
    
    # Student-specific fields
    student_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    year_of_study = db.Column(db.String(20))
    
    # Advisor-specific fields
    title = db.Column(db.String(100))  # Dr., Prof., etc.
    specialization = db.Column(db.String(200))
    office_location = db.Column(db.String(100))
    office_hours = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


# Chat model for storing human-to-human messages
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')


# Login required decorator
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Advisor role required decorator
def advisor_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'advisor':
            flash('This area is restricted to advisors', 'danger')
            return redirect(url_for('chat'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Database Admin role required decorator
def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('This area is restricted to database administrators', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.role == 'advisor':
            return redirect(url_for('advisor_dashboard'))
        elif user and user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('chat_selection'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')  # Default to student if not specified

        # Validate that all required fields are provided
        if not username or not email or not password:
            flash('Please fill in all required fields', 'danger')
            return render_template('register.html')

        # Validate role
        if role not in ['student', 'advisor', 'admin']:
            role = 'student'  # Default to student for safety

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('register.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['user_image'] = user.profile_image
            flash('Login successful!', 'success')

            if user.role == 'advisor':
                return redirect(url_for('advisor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('chat_selection'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('user_image', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/chat_selection')
@login_required
def chat_selection():
    username = session.get('username')

    # Get available advisors for human chat
    advisors = User.query.filter_by(role='advisor').all()

    return render_template('chat_selection.html',
                           username=username,
                           advisors=advisors)


@app.route('/chat')
@login_required
def chat():
    username = session.get('username')
    return render_template('index.html', username=username)


@app.route('/human_chat/<int:advisor_id>')
@login_required
def human_chat(advisor_id):
    current_user_id = session.get('user_id')
    advisor = User.query.get_or_404(advisor_id)

    # Verify the user is an advisor
    if advisor.role != 'advisor':
        flash('Invalid advisor selected', 'danger')
        return redirect(url_for('chat_selection'))

    # Mark messages as read
    unread_messages = ChatMessage.query.filter_by(
        sender_id=advisor_id,
        receiver_id=current_user_id,
        read=False
    ).all()

    for message in unread_messages:
        message.read = True

    db.session.commit()

    # Get conversation history
    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user_id) & (ChatMessage.receiver_id == advisor_id)) |
        ((ChatMessage.sender_id == advisor_id) & (ChatMessage.receiver_id == current_user_id))
    ).order_by(ChatMessage.timestamp).all()

    return render_template('human_chat.html',
                           advisor=advisor,
                           messages=messages,
                           username=session.get('username'))


@app.route('/advisor_dashboard')
@advisor_required
def advisor_dashboard():
    advisor_id = session.get('user_id')

    # Get all students who have sent messages to this advisor
    students = db.session.query(User).join(
        ChatMessage, User.id == ChatMessage.sender_id
    ).filter(
        ChatMessage.receiver_id == advisor_id,
        User.role == 'student'
    ).distinct().all()

    # Also get students who this advisor has messaged
    more_students = db.session.query(User).join(
        ChatMessage, User.id == ChatMessage.receiver_id
    ).filter(
        ChatMessage.sender_id == advisor_id,
        User.role == 'student'
    ).distinct().all()

    # Combine and remove duplicates
    all_students = list({student.id: student for student in students + more_students}.values())

    # Get unread message counts
    unread_counts = {}
    for student in all_students:
        count = ChatMessage.query.filter_by(
            sender_id=student.id,
            receiver_id=advisor_id,
            read=False
        ).count()
        unread_counts[student.id] = count

    return render_template('advisor_dashboard.html',
                           students=all_students,
                           unread_counts=unread_counts,
                           username=session.get('username'))


@app.route('/advisor_chat/<int:student_id>')
@advisor_required
def advisor_chat(student_id):
    advisor_id = session.get('user_id')
    student = User.query.get_or_404(student_id)

    # Verify the user is a student
    if student.role != 'student':
        flash('Invalid student selected', 'danger')
        return redirect(url_for('advisor_dashboard'))

    # Mark messages as read
    unread_messages = ChatMessage.query.filter_by(
        sender_id=student_id,
        receiver_id=advisor_id,
        read=False
    ).all()

    for message in unread_messages:
        message.read = True

    db.session.commit()

    # Get conversation history
    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == advisor_id) & (ChatMessage.receiver_id == student_id)) |
        ((ChatMessage.sender_id == student_id) & (ChatMessage.receiver_id == advisor_id))
    ).order_by(ChatMessage.timestamp).all()

    return render_template('advisor_chat.html',
                           student=student,
                           messages=messages,
                           username=session.get('username'))


@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    message = data.get('message', '')
    username = session.get('username')

    # Process the student's message through OpenAI
    ai_response = get_ai_response(message)

    return jsonify({
        'student_message': message,
        'advisor_response': ai_response,
        'timestamp': datetime.now().strftime('%H:%M'),
        'username': username
    })


@app.route('/send_human_message', methods=['POST'])
@login_required
def send_human_message():
    data = request.json
    receiver_id = data.get('receiver_id')
    content = data.get('message')

    if not receiver_id or not content:
        return jsonify({'error': 'Missing required data'}), 400

    sender_id = session.get('user_id')

    # Create new message
    new_message = ChatMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        timestamp=datetime.utcnow(),
        read=False
    )

    db.session.add(new_message)
    db.session.commit()

    # Emit socket event
    socketio.emit('new_message', {
        'message_id': new_message.id,
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': new_message.timestamp.strftime('%H:%M'),
        'sender_name': session.get('username')
    }, room=f'user_{receiver_id}')

    return jsonify({
        'success': True,
        'message_id': new_message.id,
        'timestamp': new_message.timestamp.strftime('%H:%M')
    })


def get_ai_response(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful academic advisor responding to a student's question."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"


# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(f'user_{session["user_id"]}')
        print(f"User {session.get('username')} connected and joined room user_{session['user_id']}")


@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(f'user_{session["user_id"]}')
        print(f"User {session.get('username')} disconnected")


# Profile management routes
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/edit_profile')
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    return render_template('edit_profile.html', user=user)


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    
    # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '' and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            user.profile_image = filename
    
    # Update basic profile information
    user.full_name = request.form.get('full_name', user.full_name)
    user.phone = request.form.get('phone', user.phone)
    user.bio = request.form.get('bio', user.bio)
    
    # Convert date_of_birth string to date object
    dob_str = request.form.get('date_of_birth')
    if dob_str:
        try:
            user.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            pass  # Keep existing date if format is invalid
    
    # Update role-specific fields
    if user.role == 'student':
        user.student_id = request.form.get('student_id', user.student_id)
        user.department = request.form.get('department', user.department)
        user.year_of_study = request.form.get('year_of_study', user.year_of_study)
    elif user.role == 'advisor':
        user.title = request.form.get('title', user.title)
        user.specialization = request.form.get('specialization', user.specialization)
        user.office_location = request.form.get('office_location', user.office_location)
        user.office_hours = request.form.get('office_hours', user.office_hours)
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        # Update session with new profile image if it was changed
        session['user_image'] = user.profile_image
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('profile'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/view_profile/<int:user_id>')
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_profile.html', user=user)


# Admin Dashboard Route
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Main admin dashboard with overview statistics"""
    # Get statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_advisors = User.query.filter_by(role='advisor').count()
    total_admins = User.query.filter_by(role='admin').count()
    total_messages = ChatMessage.query.count()
    
    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_advisors=total_advisors,
                         total_admins=total_admins,
                         total_messages=total_messages,
                         recent_users=recent_users,
                         recent_messages=recent_messages)


# Admin User Management - View All Users
@app.route('/admin/users')
@admin_required
def admin_users():
    """View all users in table format"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    search_query = request.args.get('search', '')
    per_page = 15
    
    # Build query
    query = User.query
    
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    
    if search_query:
        query = query.filter(
            (User.username.contains(search_query)) |
            (User.email.contains(search_query)) |
            (User.full_name.contains(search_query))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin_users.html', 
                         users=users, 
                         role_filter=role_filter, 
                         search_query=search_query)


# Admin Student Management
@app.route('/admin/students')
@admin_required
def admin_students():
    """View all students in detailed table format"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    per_page = 20
    
    # Build query for students only
    query = User.query.filter_by(role='student')
    
    if search_query:
        query = query.filter(
            (User.username.contains(search_query)) |
            (User.email.contains(search_query)) |
            (User.full_name.contains(search_query)) |
            (User.student_id.contains(search_query)) |
            (User.department.contains(search_query))
        )
    
    students = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin_students.html', students=students, search_query=search_query)


# Admin Advisor Management
@app.route('/admin/advisors')
@admin_required
def admin_advisors():
    """View all advisors in detailed table format"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    per_page = 20
    
    # Build query for advisors only
    query = User.query.filter_by(role='advisor')
    
    if search_query:
        query = query.filter(
            (User.username.contains(search_query)) |
            (User.email.contains(search_query)) |
            (User.full_name.contains(search_query)) |
            (User.specialization.contains(search_query)) |
            (User.title.contains(search_query))
        )
    
    advisors = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin_advisors.html', advisors=advisors, search_query=search_query)


# Admin Message Logs
@app.route('/admin/messages')
@admin_required
def admin_messages():
    """View all messages between users"""
    page = request.args.get('page', 1, type=int)
    per_page = 30
    
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin_messages.html', messages=messages)


# Admin Delete User
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a specific user (admin function)"""
    # Prevent admin from deleting themselves
    if session.get('user_id') == user_id:
        flash('You cannot delete your own account', 'danger')
        return redirect(request.referrer)
    
    user = User.query.get_or_404(user_id)
    
    # Delete user's messages first (to maintain referential integrity)
    ChatMessage.query.filter(
        (ChatMessage.sender_id == user_id) | (ChatMessage.receiver_id == user_id)
    ).delete()
    
    # Store info for flash message
    username = user.username
    role = user.role
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'{role.title()} "{username}" has been deleted successfully', 'success')
    return redirect(request.referrer)


# Admin Export Data
@app.route('/admin/export/<data_type>')
@admin_required
def admin_export_data(data_type):
    """Export data to CSV for presentations"""
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    
    if data_type == 'students':
        writer = csv.writer(output)
        writer.writerow(['ID', 'Username', 'Email', 'Full Name', 'Student ID', 'Department', 'Year', 'Phone', 'Created At'])
        
        students = User.query.filter_by(role='student').all()
        for student in students:
            writer.writerow([
                student.id, student.username, student.email, student.full_name or '',
                student.student_id or '', student.department or '', student.year_of_study or '',
                student.phone or '', student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        filename = 'students_export.csv'
        
    elif data_type == 'advisors':
        writer = csv.writer(output)
        writer.writerow(['ID', 'Username', 'Email', 'Full Name', 'Title', 'Specialization', 'Office', 'Office Hours', 'Created At'])
        
        advisors = User.query.filter_by(role='advisor').all()
        for advisor in advisors:
            writer.writerow([
                advisor.id, advisor.username, advisor.email, advisor.full_name or '',
                advisor.title or '', advisor.specialization or '', advisor.office_location or '',
                advisor.office_hours or '', advisor.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        filename = 'advisors_export.csv'
        
    elif data_type == 'messages':
        writer = csv.writer(output)
        writer.writerow(['ID', 'Sender', 'Receiver', 'Content', 'Timestamp', 'Read'])
        
        messages = ChatMessage.query.all()
        for message in messages:
            writer.writerow([
                message.id, message.sender.username, message.receiver.username,
                message.content[:200] + '...' if len(message.content) > 200 else message.content,
                message.timestamp.strftime('%Y-%m-%d %H:%M:%S'), message.read
            ])
        
        filename = 'messages_export.csv'
    
    else:
        return "Invalid data type", 400
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


if __name__ == '__main__':
    # Don't create tables here as we've migrated the database separately
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
