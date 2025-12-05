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
        Returns None if population is zero.
        Returns float('inf') if comparison group risk is zero.
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
