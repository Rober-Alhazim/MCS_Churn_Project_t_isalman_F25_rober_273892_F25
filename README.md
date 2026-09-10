## ⚙️ How to Setup and Run the Project Locally

Dear Professor, to test the application with the full database sample (99,999 subscriber records), please follow these simple steps to restore the database schema on your local machine:

### 1. Database Creation (PostgreSQL)
1. Open your pgAdmin or PostgreSQL terminal.
2. Create a new database named exactly: `telecom_churn_db_v2`

### 2. Restore Database Sample
Run the following command in your terminal to restore the full 99,999 records from the provided backup file:
```bash
psql -U postgres -d telecom_churn_db_v2 -f database/backup.sql
```

### 3. Setup Configuration
Create a `.env` file in the project root directory and write your database login details and your Groq API Key:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telecom_churn_db_v2
DB_USER=postgres
DB_PASSWORD=your_postgres_password
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Dashboard
```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```
### 5. Demo Link
```bash
https://drive.google.com/file/d/1mUZdhvMF0F1dvd5VEVGOtK0TJokdEuA0/view?usp=sharing
```
