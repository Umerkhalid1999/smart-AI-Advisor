# **🎓 Smart AI Advisor - Academic Guidance Platform***
## Overview
Smart AI Advisor is a modern web application designed to bridge the gap between students and academic advisors. Leveraging the power of artificial intelligence alongside human expertise, it provides students with instant access to academic guidance, while offering advisors an efficient platform to manage student inquiries.
Built with Flask and OpenAI's GPT technology, this platform enables real-time communication and personalized support for academic questions, course selection, career guidance, and more.

## ✨ Key Features
1. Dual Advisor System

AI-Powered Assistant: Instant responses to common academic questions and guidance
Human Advisor Network: Connect with real academic advisors for complex issues and personalized support
Seamless Integration: Switch between AI and human support as needed

2. Advanced Communication

Real-time Chat: Instant messaging powered by Socket.IO technology
Notification System: Stay updated with unread message alerts
Conversation History: Access complete chat logs for reference

3. Smart User Experience

Role-Based Interface: Tailored experiences for students and advisors
Secure Authentication: Robust login and registration system
Responsive Design: Optimized for both desktop and mobile use

4. Administrative Features

Advisor Dashboard: Comprehensive overview of student inquiries
User Management: Easily manage student and advisor accounts
Analytics: Track usage patterns and common questions

## 🛠️ Technology Stack
1. Backend Framework

Flask: Lightweight and flexible Python web framework
Gunicorn/Eventlet: Production-grade WSGI server configuration
Flask-SocketIO: Real-time bidirectional event-based communication

2. Database & ORM

- SQLAlchemy: Powerful ORM for database operations
- SQLite: Local development database
- PostgreSQL: Production database option

3. AI & Natural Language Processing

- OpenAI GPT-3.5: Advanced natural language understanding and generation
- Custom AI System Prompts: Tailored for academic advising context

4. Security

- Werkzeug: Password hashing and security utilities
- Session Management: Secure user sessions
- Environment Variable Protection: Sensitive credential management

## 📋 Installation & Setup
1. Prerequisites

- Python 3.12 or higher
- pip package manager
- OpenAI API key

2. Local Development Setup

- Clone the repository

bashgit clone https://github.com/Umerkhalid1999/smart-AI-Advisor.git
cd smart-AI-Advisor

3. Create and activate a virtual environment

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies

bashpip install -r requirements.txt

Configure environment variables
Create a .env file with:

OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secure_random_string_here

Initialize the database

bashpython -c "from app import app, db; app.app_context().push(); db.create_all()"

Run the application

bashpython app.py
The application will be available at http://localhost:5000 

## 🚀 Deployment
This application is optimized for deployment on Railway:

Prepare your repository

Ensure all configuration files are in place: Procfile, railway.json, wsgi.py
Verify database initialization in app.py


Deploy on Railway

Fork or push to your GitHub repository
Connect your GitHub repository to Railway
Add required environment variables in Railway dashboard:

OPENAI_API_KEY: Your OpenAI API key
SECRET_KEY: A secure random string for session management


Deploy your application


Monitor and scale

Use Railway dashboard to monitor application health
Scale resources as needed based on user demand



📱 User Guide
For Students

Account Creation

Register with a valid email address
Select "student" as your role
Complete your profile


Getting Academic Help

Choose between AI advisor or human advisor
For AI: Simply type your question and receive instant guidance
For human advisors: Browse available advisors and initiate a conversation


Managing Conversations

Access all your conversation history
Resume conversations at any time
Switch between AI and human advisors based on your needs



For Advisors

Advisor Registration

Create an account with "advisor" role
Set up your expertise profile
Begin receiving student inquiries


Student Management

View all connected students from your dashboard
See unread message indicators
Prioritize urgent inquiries


Communication Tools

Real-time messaging with students
View conversation history for context
Provide personalized academic guidance



🛣️ Future Roadmap

Enhanced AI Capabilities: Integration with specialized academic knowledge bases
Scheduling System: Calendar integration for booking advisor appointments
Resource Library: Shareable documents and academic resources
Analytics Dashboard: Insights into common student questions and trends
Multi-language Support: Expanding accessibility to non-English speakers
Mobile Applications: Native iOS and Android apps

🔄 API Endpoints
EndpointMethodDescription/registerPOSTCreate a new user account/loginPOSTAuthenticate a user/chat_selectionGETChoose between AI and human advising/chatGETAccess the AI chat interface/human_chat/<advisor_id>GETChat with a specific advisor/advisor_dashboardGETAdvisor's view of all student chats/send_messagePOSTSend a message to AI advisor/send_human_messagePOSTSend a message to human advisor/profileGETView and edit user profile
📊 Project Structure
smart-AI-Advisor/
├── app.py                 # Main application file with routes and logic
├── wsgi.py                # WSGI entry point for production servers
├── Procfile               # Railway deployment configuration
├── railway.json           # Railway specific settings
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore patterns
├── .env                   # Environment variables (local only)
├── templates/             # HTML templates
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── chat_selection.html# Choose advisor type
│   ├── index.html         # AI chat interface
│   ├── human_chat.html    # Human advisor chat
│   ├── profile.html       # User profile page
│   ├── advisor_dashboard.html # Advisor view
│   └── advisor_chat.html  # Advisor's student chat view
└── static/                # Static assets
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    └── img/               # Image assets
🤝 Contributing
Contributions are welcome and greatly appreciated! If you're interested in improving Smart AI Advisor, please follow these steps:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
👥 Acknowledgements

OpenAI for providing the powerful GPT API
Flask and its extension developers
Railway for hosting services
The open-source community for various tools and libraries

📬 Contact
Umer Khalid - GitHub Profile
Project Link: https://github.com/Umerkhalid1999/smart-AI-Advisor
