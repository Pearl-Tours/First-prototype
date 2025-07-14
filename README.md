# Pearl Tours Web Application

**Pearl Tours** is a web application designed to showcase and manage tour packages for exploring Uganda, the Pearl of Africa. It allows users to browse tours, view details, and administrators to manage tour listings.

---

## 🛠 Technologies Used

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript, Bootstrap, Tailwind
- **Database:** MySQL (SQLite for development/testing)
- **Containerization:** Docker, Docker Compose

---

## 📁 Project Structure

```
├── app/                    # Main application folder
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # Database models
│   ├── routes.py           # Application routes
│   └── ...                 # Other Python modules
├── static/                 # Public static assets
├── test.db                 # SQLite database file
├── .gitignore
├── Dockerfile              # Docker configuration
├── docker-compose.yaml     # Docker Compose config
├── requirements.txt        # Python dependencies
├── start.sh                # Startup script
├── Tests/                  # pytest tests
└── .github/workflows/      # GitHub Actions workflows
```

---

## 👨‍💻 Developers

- **Backend:** Rhyan Lubega
- **Frontend:** George Mutale
- **Database & Security:** Oscar Kyamuwendo
- **Business Role:** Bernadette Nakazibwe
- **Product Manager & Machine Learning:** Boaz Onyango

---

## 🌟 Special Features

- Secure payment using bank cards and PayPal
- Terminal system for secure admin creation
- Quick tour booking system
- Tokenized emails for password recovery & support
- Email system for tour updates and receiving receipts
- Newsletter integration
- Live AI-powered chatbot

---

## ⚙️ Setup and Running the Project

### Prerequisites

- Python 3.8+
- pip
- Docker (optional)
- Docker Compose (optional)

---

## 🚀 Running the App

### ✅ Using Uvicorn (Local)

1. **Start the app:**

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python -m uvicorn app.main:app --reload --host localhost
```

2. **Admin Sign-In:**

Use the following credentials:

- **Email:** `mutalegeorge367@gmail.com`
- **Password:** `Tourism01@#`

Alternatively, create a new admin via terminal:

```bash
python -m app.create_admin
```

3. **Customer Sign-In:**

Use the following credentials:

- **Email:** `george.mutale@stud.th-deg.de`
- **Password:** `Tourism01`

---

### 🐳 Using Docker

> Docker creates a separate database. You must manually create admin and customer accounts inside the container.

1. **Build and run the services:**

```bash
chmod +x start.sh
./start.sh
```

2. **Create an admin inside Docker:**

```bash
docker exec -it first-prototype-app-1 python -m app.create_admin
```

3. **Customer Sign-Up/Login:**  
   Use the app interface to register and log in.

4. **Stop the services:**

```bash
Ctrl + C
# Or stop the container manually
docker ps
docker stop <container_id>
```

---

## 🤝 Contributing

We welcome contributions!

### Steps to Contribute

1. Fork the repository
2. Create a new feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m "Description of changes"`
4. Push to your fork: `git push origin feature-name`
5. Open a pull request

Please follow standard coding practices and ensure your code passes tests.

---

## 📄 License

Specify the license for the project here. (e.g., MIT, Apache 2.0)
