# 📱 Telecom Churn Prediction System

An Intelligent Decision Support System to predict customer attrition using Ant Colony Optimization (ACO) clustering and a generative AI assistant.

---

## 🌐 Live System Demo
You can test the fully functional live application immediately without any installation:
👉 **[Click Here to Open the Live Demo](https://streamlit.app)**

*Note: In the live demo, go to the **Data Management** page and click **"تشغيل محرك ACO"** to instantly generate the 99,999 subscriber records directly in the browser session memory.*

---

## 🛠️ How to Setup and Run Locally (Alternative)

### 1. Installation
Open your terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Database Setup (Optional)
To run locally with the full database sample:
1. Create a database named `telecom_churn_db_v2` in your PostgreSQL.
2. Restore the database backup file by running:
```bash
psql -U postgres -d telecom_churn_db_v2 -f database/backup.sql
```

### 3. Configure Environment Variables
Create a `.env` file in the root folder and add your credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telecom_churn_db_v2
DB_USER=postgres
DB_PASSWORD=your_postgres_password
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run Locally
```bash
streamlit run streamlit_app/app.py
```

---

## 📁 Project Structure
* `aco_engine/`: The core Ant Colony Optimization and Risk Scoring algorithms.
* `database/`: Database configuration and backup sql script.
* `streamlit_app/`: The UI dashboard screens and interactive charts.
* `utils/`: Machine learning offer composers and API connectors.
