# Technical Specification: School Behaviour & Safeguarding Dashboard

## 1. Data Schema Design

The following relational database schema supports the required metrics for Equity, Effectiveness, and Compliance.

### Entity Relationship Diagram (ERD) Overview
- **Students** (1) ---- (M) **BehaviourLog**
- **Students** (1) ---- (M) **Attendance**
- **BehaviourLog** (1) ---- (M) **Interventions**

### Table Definitions (SQL DDL)

```sql
-- Table: Students
-- Stores demographic and vulnerability data for disproportionality analysis.
CREATE TABLE Students (
    Student_ID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    YearGroup INT,
    Gender VARCHAR(20),
    Ethnicity VARCHAR(50),          -- For Race/Ethnicity disproportionality
    SEN_Status VARCHAR(20),         -- 'EHC Plan', 'SEN Support', 'None'
    FSM_Flag BOOLEAN,               -- Free School Meals (Vulnerability)
    PupilPremium_Flag BOOLEAN,      -- Pupil Premium (Vulnerability)
    IsActive BOOLEAN DEFAULT TRUE
);

-- Table: BehaviourLog
-- The core fact table for incidents.
CREATE TABLE BehaviourLog (
    Incident_ID INT PRIMARY KEY,
    Student_ID INT,
    IncidentDate DATETIME,
    BehaviorType VARCHAR(100),      -- e.g., 'Disruptive', 'Aggression', 'Truancy'
    Location VARCHAR(100),          -- e.g., 'Classroom 3B', 'Playground'
    SeverityCode VARCHAR(10),       -- 'SW' (2nd Warning), 'OC' (On Call), 'HD' (Head Detention)
    Points INT,                     -- For calculating High-Risk Case Load (60+ points)
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
);

-- Table: Attendance
-- Tracks daily/session attendance for Truancy and Lateness metrics.
CREATE TABLE Attendance (
    Record_ID INT PRIMARY KEY,
    Student_ID INT,
    Date DATE,
    SessionType VARCHAR(2),         -- 'AM' or 'PM'
    Status VARCHAR(50),             -- 'Present', 'Late', 'Auth_Absence', 'Unauth_Absence'
    MinutesLate INT DEFAULT 0,
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
);

-- Table: Interventions
-- Tracks actions taken in response to incidents for Fidelity Rate.
CREATE TABLE Interventions (
    Intervention_ID INT PRIMARY KEY,
    Incident_ID INT,
    ActionType VARCHAR(100),        -- e.g., 'Parent Call', 'Detention', 'Restorative Meeting'
    RequiredDate DATE,
    CompletionDate DATE,            -- NULL if not completed
    Status VARCHAR(20),             -- 'Pending', 'Completed', 'Overdue'
    FOREIGN KEY (Incident_ID) REFERENCES BehaviourLog(Incident_ID)
);
```

---

## 2. Logic Implementation

### Task A: Equity & Disproportionality (Risk Ratio)

**Requirement**: Calculate if a specific student group is more likely to be suspended than the baseline (or non-group).
**Metric**: Risk Ratio = (Risk of Group X) / (Risk of Comparison Group)
*Risk = (Number of Students in Group with Incident) / (Total Students in Group)*

#### Python Implementation (Pandas)

```python
import pandas as pd

def calculate_risk_ratio(df_students, df_incidents, group_col, target_group, incident_type='Suspension'):
    """
    Calculates the Risk Ratio for a specific demographic group regarding a specific incident type.
    
    Args:
        df_students (pd.DataFrame): Dataframe containing Student_ID and demographic columns (group_col).
        df_incidents (pd.DataFrame): Dataframe containing Incident_ID, Student_ID, BehaviorType.
        group_col (str): The demographic column to analyze (e.g., 'Ethnicity', 'SEN_Status').
        target_group (str): The specific value in group_col to test (e.g., 'Black Caribbean').
        incident_type (str): The behavior type to filter for.
        
    Returns:
        float: The Risk Ratio. >1.0 indicates over-representation.
    """
    
    # 1. Merge Data
    # We need all students to calculate the population sizes, even those without incidents.
    # Filter incidents for the specific type first
    target_incidents = df_incidents[df_incidents['BehaviorType'] == incident_type]
    
    # Get set of students who had this incident
    students_with_incident = set(target_incidents['Student_ID'].unique())
    
    # 2. Define Groups
    # Target Group Population
    target_pop = df_students[df_students[group_col] == target_group]
    target_pop_count = len(target_pop)
    
    # Comparison Group Population (everyone else)
    comp_pop = df_students[df_students[group_col] != target_group]
    comp_pop_count = len(comp_pop)
    
    if target_pop_count == 0 or comp_pop_count == 0:
        return None # Avoid division by zero
        
    # 3. Calculate Risks
    # Count students in target group who had the incident
    target_incident_count = target_pop[target_pop['Student_ID'].isin(students_with_incident)].shape[0]
    target_risk = target_incident_count / target_pop_count
    
    # Count students in comparison group who had the incident
    comp_incident_count = comp_pop[comp_pop['Student_ID'].isin(students_with_incident)].shape[0]
    comp_risk = comp_incident_count / comp_pop_count
    
    if comp_risk == 0:
        return float('inf') # Infinite risk ratio (comparison group has 0 incidents)
        
    # 4. Calculate Ratio
    risk_ratio = target_risk / comp_risk
    
    return risk_ratio
```

### Task B: Intervention Fidelity Rate

**Requirement**: % of mandatory actions recorded as Completed.

#### SQL Query

```sql
SELECT 
    ActionType,
    COUNT(*) AS Total_Required,
    SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS Total_Completed,
    (CAST(SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 AS Fidelity_Rate_Percent
FROM 
    Interventions
GROUP BY 
    ActionType;
```

### Task C: Top 5 Incident Hotspots

**Requirement**: Aggregation of "What" (Behavior Type) and "Where" (Location/Time).
*Note: Assuming we extract 'Hour' from IncidentDate for the time component.*

#### SQL Query

```sql
SELECT TOP 5
    Location,
    DATEPART(hour, IncidentDate) AS Time_Hour,
    BehaviorType,
    COUNT(*) AS Incident_Count
FROM 
    BehaviourLog
GROUP BY 
    Location, 
    DATEPART(hour, IncidentDate), 
    BehaviorType
ORDER BY 
    Incident_Count DESC;
```

---

## 3. Dashboard Architecture: Governor's Equity Report

**Requirement**: Structure data for "Suspension Rates vs. Primary Reasons".
This JSON structure is designed to be consumed by a frontend charting library (e.g., Chart.js, Recharts).

### JSON Data Payload

```json
{
  "governor_view": {
    "report_period": "Autumn Term 2024",
    "equity_report": {
      "summary": {
        "total_suspensions": 45,
        "disproportionality_flag": true,
        "highest_risk_group": "SEN Support"
      },
      "suspension_rates_by_group": [
        {
          "group_category": "Ethnicity",
          "data": [
            { "label": "White British", "suspension_rate": 2.5, "population_count": 400 },
            { "label": "Black Caribbean", "suspension_rate": 5.2, "population_count": 80 },
            { "label": "Asian", "suspension_rate": 1.8, "population_count": 120 }
          ]
        },
        {
          "group_category": "SEN Status",
          "data": [
            { "label": "No SEN", "suspension_rate": 1.2, "population_count": 500 },
            { "label": "SEN Support", "suspension_rate": 6.5, "population_count": 80 },
            { "label": "EHC Plan", "suspension_rate": 8.0, "population_count": 20 }
          ]
        }
      ],
      "suspensions_vs_reasons": {
        "description": "Breakdown of primary reasons for suspension, segmented by the highest risk group (SEN Status) vs Baseline.",
        "series": [
          {
            "reason": "Persistent Disruptive Behaviour",
            "sen_support_count": 12,
            "non_sen_count": 5
          },
          {
            "reason": "Physical Assault against Pupil",
            "sen_support_count": 3,
            "non_sen_count": 8
          },
          {
            "reason": "Verbal Abuse / Threatening Adult",
            "sen_support_count": 5,
            "non_sen_count": 2
          }
        ]
      }
    },
    "systemic_compliance": {
      "safeguarding_audit_score": 95,
      "policy_fidelity_rate": 88.5
    }
  }
}
```
