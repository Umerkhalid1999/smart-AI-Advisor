# 🎓 Smart AI Advisor - Academic Guidance Platform

## Overview

Smart AI Advisor is a modern web application designed to bridge the gap between students and academic advisors. Leveraging the power of artificial intelligence alongside human expertise, it provides students with instant access to academic guidance, while offering advisors an efficient platform to manage student inquiries.

Built with Flask and OpenAI's GPT technology, this platform enables real-time communication and personalized support for academic questions, course selection, career guidance, and more.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green?style=flat-square&logo=openai)](https://openai.com/)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-purple?style=flat-square&logo=railway)](https://railway.app/)

## ✨ Key Features

### Dual Advisor System
- **AI-Powered Assistant**: Instant responses to common academic questions and guidance
- **Human Advisor Network**: Connect with real academic advisors for complex issues and personalized support
- **Seamless Integration**: Switch between AI and human support as needed

### Advanced Communication
- **Real-time Chat**: Instant messaging powered by Socket.IO technology
- **Notification System**: Stay updated with unread message alerts
- **Conversation History**: Access complete chat logs for reference

### Smart User Experience
- **Role-Based Interface**: Tailored experiences for students and advisors
- **Secure Authentication**: Robust login and registration system
- **Responsive Design**: Optimized for both desktop and mobile use

### Administrative Features
- **Advisor Dashboard**: Comprehensive overview of student inquiries
- **User Management**: Easily manage student and advisor accounts
- **Analytics**: Track usage patterns and common questions

## 🛠️ Technology Stack

### Backend Framework
- **Flask**: Lightweight and flexible Python web framework
- **Gunicorn/Eventlet**: Production-grade WSGI server configuration
- **Flask-SocketIO**: Real-time bidirectional event-based communication

### Database & ORM
- **SQLAlchemy**: Powerful ORM for database operations
- **SQLite**: Local development database
- **PostgreSQL**: Production database option

### AI & Natural Language Processing
- **OpenAI GPT-3.5**: Advanced natural language understanding and generation
- **Custom AI System Prompts**: Tailored for academic advising context

### Security
- **Werkzeug**: Password hashing and security utilities
- **Session Management**: Secure user sessions
- **Environment Variable Protection**: Sensitive credential management

## 📋 Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip package manager
- OpenAI API key

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/Umerkhalid1999/smart-AI-Advisor.git
cd smart-AI-Advisor
