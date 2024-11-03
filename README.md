# 🚀 Chat Rooms - Real-Time Communication Platform

Connect with friends and family through our modern, secure, and feature-rich chat application. Built with Flask and html/css, Chat Rooms offers seamless real-time communication with a focus on user privacy and community management.

## ✨ Key Features

### 👥 User Management & Security
- **Robust Authentication System**
  - Secure account creation with email verification
  - Password strength requirements and recovery options
  - Password salting, hashing, csrf_token and security
  - Session management with automatic timeout
  - Account deletion with data cleanup

- **Comprehensive Profile System**
  - Customizable user profiles with bio and interests
  - Profile picture upload and management via Cloudinary

### 💬 Chat Room Features
- **Room Management**
  - Create public chat rooms
  - Customizable room settings (name, profile picture)
  - View participants

- **Interactive Messaging**
  - Real-time message delivery using Socket.io
  - Message deletion and moderation
  - Multiple user support


### 🛡️ Moderation Tools
- **Room Administration**

    - Room creators have full control
    - Ability to appoint multiple moderators
    - Ban management system
    - Message deletion


### 🔄 Real-Time Features
- **Socket.io Integration**
  - Instant message delivery
  - Room creation and deletion


## 🛠️ Technical Stack

### Backend
- **Flask Framework**
  - Flask mail for mail
  - Scalable routing system
  - Custom user model
  - Error handling and logging

- **Database**
  - PostgreSQL for robust data storage
  - SQLAlchemy ORM for efficient queries
  - Database migrations with Alembic
  - Connection pooling and optimization

### Frontend

- **Styling**
  - Tailwind CSS for modern UI
  - Custom theming support
  - Dark/light mode toggle
  - Mobile-first approach

### Infrastructure
- **Authentication & Authorization**
  - Flask-Login for session management
  - JWT token implementation
  - Role-based access control

- **File Storage**
  - Cloudinary integration for media
  - Secure file handling
  - Multiple format support

## 🚀 Getting Started

### Prerequisites
```bash
# Required software
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
```

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/chat-rooms.git
   cd chat-rooms
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   pip install -r requirements.txt
   
   ```

4. **Configure Environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configurations
   # - Database credentials
   # - Cloudinary API keys
   # - Mail server settings
   # - Socket.io configurations
   ```

5. **Initialize Database**
   ```bash
   flask db upgrade
   ```

6. **Start Development Servers**
   ```bash
   # Start backend (from root directory)
   flask run

   ```

7. **Access Application**
   -  http://localhost:5000
