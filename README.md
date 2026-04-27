# 🎓 ScholarGrid

**ScholarGrid** is a premium college collaboration platform where students can share academic notes, communicate in real-time group chats, track their contributions on a leaderboard, and submit feedback — all within a beautifully designed, gamified interface.

---

## 🚀 Features

### 👩‍🎓 Student
- **Dashboard** — Personalized welcome, stats (uploads, downloads, points, rank), trending notes, and top contributors
- **Notes** — Upload, browse, search, filter, and download academic notes (PDF/DOCX/etc.) with subject tagging and star ratings
- **Chat** — Real-time group messaging via WebSockets; join groups using invite codes, share files in chat
- **Leaderboard** — Ranked list of top contributors with tier badges (Bronze → Silver → Gold → Elite)
- **Feedback** — Submit complaints or suggestions; track status of previous submissions
- **Profile** — Edit name/bio, upload avatar, view account stats, toggle dark/light mode, upgrade to Faculty

### 🛠️ Admin / Faculty (Management Panel)
- **Dashboard** — Platform-wide stats and activity overview
- **Users** — View, search, warn, ban, and manage all registered users
- **Groups** — Create and delete chat groups; auto-generated join codes
- **Notes Moderation** — Approve or reject uploaded notes before they go live
- **Complaints** — View and resolve student-submitted feedback/complaints
- **Analytics** — Charts for monthly uploads, user growth, top subjects, and platform health

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, React Router v6 |
| **Styling** | Tailwind CSS, Framer Motion (animations) |
| **Icons** | Lucide React |
| **Backend** | Node.js, Express.js |
| **Real-time** | WebSocket (`ws`) |
| **Auth** | JWT (JSON Web Tokens) + bcrypt |
| **Database** | MySQL |
| **File Uploads** | Multer (avatars, notes, chat files) |

---

## 📦 Project Structure

```
scholargridddd/
├── server/                  # Node.js backend
│   ├── app.js               # Express server entry point
│   ├── db.js                # MySQL connection pool
│   ├── mysql_schema.sql     # Database schema definition
│   └── routes/
│       ├── auth.js          # Login, signup, /me
│       ├── users.js         # User management
│       ├── notes.js         # Notes CRUD + file upload
│       ├── groups.js        # Group chat management
│       ├── messages.js      # Chat messages
│       ├── leaderboard.js   # Rankings
│       ├── complaints.js    # Feedback/complaints
│       └── analytics.js     # Admin analytics
│
└── src/                     # React frontend
    ├── context/
    │   ├── AuthContext.jsx  # Auth state (login, signup, logout, profile)
    │   └── ThemeContext.jsx # Dark/light mode
    ├── services/            # API client functions (one file per domain)
    ├── routes/
    │   ├── AppRouter.jsx    # All route definitions
    │   └── ProtectedRoute.jsx
    ├── pages/
    │   ├── auth/            # Login, Signup
    │   ├── student/         # Dashboard, Notes, Chat, Leaderboard, Feedback, Profile
    │   └── admin/           # AdminDashboard, Users, Groups, Notes, Complaints, Analytics
    └── components/
        └── layout/          # StudentLayout, AdminLayout (sidebars, navbars)
```

---

## ⚙️ Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) v18 or higher
- npm v9 or higher
- MySQL Server (v8.0+)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aryannten/ScolarGrid.git
cd ScolarGrid

# 2. Install frontend dependencies
npm install

# 3. Install backend dependencies
npm install --prefix server
```

### Database Setup

1. Start your local MySQL server.
2. Create the database and tables using the provided schema:
   ```bash
   mysql -u root -p < server/mysql_schema.sql
   ```
3. Create a `.env` file in the root directory (and `server/` directory) with your database credentials:
   ```env
   PORT=3001
   JWT_SECRET=scholargrid-dev-secret-key-2026
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=scholargrid_db
   ```

### Running Locally

```bash
npm run dev
```

This starts both servers concurrently:
- **Frontend (Vite):** http://localhost:5173
- **Backend API:** http://localhost:3001

> The backend must be running for the frontend to function. The `npm run dev` command starts both automatically.

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Login |
| POST | `/api/auth/signup` | Public | Register |
| GET | `/api/auth/me` | JWT | Get current user |
| GET | `/api/notes` | JWT | List notes |
| POST | `/api/notes` | JWT | Upload a note |
| GET | `/api/leaderboard` | JWT | Get rankings |
| GET | `/api/groups` | JWT | List groups |
| POST | `/api/groups` | Faculty+ | Create group |
| POST | `/api/groups/join` | JWT | Join group by code |
| GET | `/api/messages/:groupId` | JWT | Get chat messages |
| POST | `/api/messages` | JWT | Send message |
| GET | `/api/complaints` | JWT | List complaints |
| POST | `/api/complaints` | JWT | Submit complaint |
| GET | `/api/analytics` | Faculty+ | Platform analytics |
| GET | `/api/health` | Public | Health check |

---

## 💾 Database

ScholarGrid uses a **MySQL Database** for robust, production-ready data persistence.

- The complete relational schema with foreign key constraints is defined in `server/mysql_schema.sql`.
- Database connections are pooled and managed asynchronously via the `mysql2/promise` package.
- All relationships (such as Group Memberships, Notes Ratings, and Leaderboard Points) are managed seamlessly using native SQL joins.

---

## 🔒 Roles & Permissions

| Role | Access |
|---|---|
| `student` | Student dashboard, notes, chat, leaderboard, feedback, profile |
| `faculty` | Full management panel (users, groups, notes moderation, complaints, analytics) |
| `superadmin` | All faculty permissions + user banning/deletion |

---

## 🛡️ Security Notes

- Passwords are hashed with **bcrypt** (10 salt rounds)
- All protected routes require a **JWT Bearer token** in the `Authorization` header
- Tokens are stored in `localStorage` and cleared on logout
- Ensure you do not expose your `.env` database credentials in public repositories.

---

## 📄 License

This project was built as a college collaboration platform. All rights reserved.
