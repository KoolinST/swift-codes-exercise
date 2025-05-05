<<<<<<< HEAD
# swift-codes-exercise
=======
## SWIFT Code Validation & CSV Importer
A robust and production-ready application built with **Flask** and **PostgreSQL**, designed to validate **SWIFT/BIC codes** according to ISO 9362 and seamlessly import data from CSV files into a relational database. It includes error handling, logging, Docker support, and CI/CD via GitHub Actions.

---

## ✨ Features

- ✅ **SWIFT Code Validation** — Verifies codes using ISO 9362 format rules.
- 📥 **CSV Importer** — Cleanly ingests structured data into the database.
- ⚠️ **Edge Case Handling** — Detects malformed CSV files, duplicates, and invalid data.
- 🛑 **Error Reporting** — Graceful exception handling with clear feedback.
- 📝 **Detailed Logging** — Logs all key operations and errors.
- 🧪 **Unit Testing** — Fully tested logic using `unittest` and `pytest`.
- 🐳 **Docker Support** — Full containerization via Docker and `docker-compose`.
- 🔁 **CI/CD Pipeline** — Automated tests on every push using GitHub Actions.

---

## 🧰 Prerequisites

Ensure you have the following installed:

- Python 3.9 or higher
- PostgreSQL
- Docker + Docker Compose

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/KoolinST/swift-codes-exercise.git
cd swift-codes-exercise
```
## Environment Configuration (Required for All Setups)
```bash
cp .env.example .env
```
Update any values in .env as needed (e.g., DB credentials, ports).\

Create a virtual environment (if using Python):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## 2️⃣ Run via Docker(Recommended)
Open Docker on your machine \
Start services defined in docker-compose.yml
```bash
docker-compose up --build
```
This command will build the Docker images (if not already built) and start the application services defined in the docker-compose.yml file.\
Now, the application available at http://localhost:8080 \
PostgreSQL exposed on: http://localhost:5432

## 3️⃣ Run Locally (Alternative)
## 🏗️ Manually Setup PostgreSQL
```bash
CREATE USER remitly WITH PASSWORD 'remitly';
CREATE DATABASE swift_data OWNER remitly;
CREATE DATABASE swift_data_test OWNER remitly;
```

```bash
python run.py
```

## API Endpoints
Retrieve details of a single SWIFT code (whether for a headquarters or branches):\
GET http://localhost:8080/v1/swift-codes/{swift-code} \
Return all SWIFT codes with details for a specific country (both headquarters and branches):\
GET http://localhost:8080/v1/swift-codes/country/{countryISO2code} \
Add new SWIFT code entries to the database for a specific country:\
POST http://localhost:8080/v1/swift-codes \
Delete a SWIFT code entry if the swiftCode matches the one in the database:\
DELETE http://localhost:8080/v1/swift-codes/{swift-code} \

Stop services defined in docker-compose.yml
```bash
docker-compose down
```
## ⚠️ Error Handling
Malformed SWIFT Codes — Invalid patterns or characters.
Missing Data — Empty required fields in CSV.
Duplicates — Already-existing records are skipped automatically.
Invalid CSV Structure — Triggers a validation error with a logged warning.
Tests
The application comes with unit tests to ensure correctness. It uses the unittest framework.

## ✅ Test Coverage:
SWIFT Code Validation\
CSV Importer logic\
Database integrity\
Error conditions (e.g., malformed files, duplicates)
## 🤝 Acknowledgements
**Flask** - Micro web framework\
**SQLAlchemy** - ORM for Python\
**PostgreSQL** - Relational DB\
**Pytest** - Testing framework\
**Docker** - Containerization\
**Docker Compose** - Multi-container orchestration\
**GitHub Actions** - CI/CD
