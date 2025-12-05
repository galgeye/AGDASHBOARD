# School Behaviour & Safeguarding Dashboard

## Overview
This project contains the technical specification and prototype for a School Behaviour & Safeguarding Dashboard. The goal is to transform raw data into high-level strategic tracking (KPIs) regarding Equity, Effectiveness, and Compliance for School Leadership Teams (SLT).

## Contents
- **`technical_specification.md`**: Detailed backend design, including:
    - Relational Database Schema (Students, BehaviourLog, Attendance, Interventions)
    - SQL/Python Logic for Key Performance Indicators (Equity, Fidelity, Hotspots)
    - Dashboard Architecture (JSON structure for Governor's Report)
- **`index.html`**: A client-side prototype of the dashboard (SLT Edition v5.0) that accepts Excel file uploads.

## Deployment
### GitHub Repository
To deploy this project to GitHub:
1. Initialize a git repository.
2. Commit the files.
3. Push to a remote repository.

### CI/CD Pipeline
A sample GitHub Actions workflow is provided in `.github/workflows/ci_cd.yml` to demonstrate how the backend logic (once implemented) would be tested and deployed.
