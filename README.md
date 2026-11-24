# Student Record Management System (SRMS) – Web Portal

A Streamlit web app for managing students, courses, enrolments, marks, grades, GPA, and semester result sheets.

## Project structure

```
srms_web/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
├── srms_data.json          # Auto-created data store (seeded with sample data)
├── .streamlit/config.toml  # Theme and server settings
├── .gitignore
└── README.md
```

## Run in VS Code (macOS)

1. Unzip the file and open the `srms_web` folder in VS Code (File > Open Folder).
2. Open the terminal (Ctrl + `) and create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open http://localhost:8501 in your browser.

To stop the server, press Ctrl + C in the terminal.

## Troubleshooting

- **Blank page / "Port 8501 is not available"**: another Streamlit is still running. Stop it with Ctrl + C, or run `streamlit run app.py --server.port 8510`.
- **`pip: command not found`**: use `python3 -m pip install -r requirements.txt`.
- **Changes not showing**: save the file (Cmd + S) and press Cmd + R in the browser.

## Features

- Dashboard with KPI cards, attendance and marks charts, and course cards
- Student directory: add, search, export CSV, delete
- Course catalog: add THEORY/LAB courses with faculty, semester, credits, attendance; delete
- Enrolment and marks entry with automatic grade (A–F) and grade points
- Result sheet with CSV export and credit-weighted GPA calculator
# arms_web
# arms_web
