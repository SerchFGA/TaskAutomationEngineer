# WindBorne Finance Automation Assignment

**Author:** Sergio Fernando Gonázalez Aguirre  
**Email:** sergino.8746@gmail.com

---

## Overview
This project is a full-stack financial data pipeline and dashboard designed to analyze key metrics for TE Connectivity (TEL), Sensata Technologies (ST), and DuPont (DD). It fetches data from the Alpha Vantage API, stores it in a database, and visualizes it via a Streamlit dashboard.

## Features
- **ETL Pipeline:** Automates data extraction, transformation, and loading into a relational database.
- **Financial Analysis:** Calculates Profitability, Liquidity, and Efficiency metrics.
- **Interactive Dashboard:** Visualizes trends with dynamic charts and high-contrast UI.
- **Production Ready:** Includes strategies for scaling, scheduling (n8n), and monitoring.

## Tech Stack
- **Language:** Python 3.10+
- **Frontend:** Streamlit, Plotly
- **Backend:** SQLAlchemy, Pandas
- **Database:** SQLite (Dev) / PostgreSQL (Production ready)

## Setup Instructions

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd WindBorne_Finance_Assignment
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    ALPHA_VANTAGE_API_KEY=your_api_key_here
    DATABASE_URL=sqlite:///finance.db
    ```

5.  **Run ETL Pipeline**
    Fetch data and populate the database:
    ```bash
    python etl.py
    ```

6.  **Launch Dashboard**
    Start the web application:
    ```bash
    streamlit run app.py
    ```
    Access at: `http://localhost:8501`

## Deployment (Getting a Public URL)
**Live Demo:** [https://taskautomationengineer.streamlit.app/](https://taskautomationengineer.streamlit.app/)

To satisfy the "Public dashboard URL" deliverable, this app is deployed using **Streamlit Community Cloud**.

### Database Strategy for Demo
The repository includes a pre-populated SQLite database (`finance.db`).
*   **Why?** To ensure the dashboard works immediately upon deployment without requiring a separate PostgreSQL server or running the ETL pipeline in the cloud.
*   **Production:** In a real-world scenario, this would connect to a hosted PostgreSQL instance (e.g., AWS RDS, Supabase) using the `DATABASE_URL` environment variable.

### How to Deploy Your Own
1.  **Push to GitHub**: Ensure this project is in a public GitHub repository.
2.  **Sign up/Login**: Go to [share.streamlit.io](https://share.streamlit.io/).
3.  **Deploy**:
    *   Click "New app".
    *   Select your GitHub repository.
    *   Set "Main file path" to `app.py`.
    *   Click "Deploy".

## Project Structure
- `app.py`: Main dashboard application.
- `etl.py`: Extract, Transform, Load script.
- `models.py`: Database schema definitions.
- `data/`: Local cache for API responses (gitignored).

## Production Strategy
Detailed answers regarding scheduling (n8n), rate limits, and scaling are available directly within the **Dashboard** under "Part 4: Production Strategy".
