-- Task B: Intervention Fidelity Rate
-- Requirement: % of mandatory actions recorded as Completed.

SELECT 
    ActionType,
    COUNT(*) AS Total_Required,
    SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS Total_Completed,
    (CAST(SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) * 100 AS Fidelity_Rate_Percent
FROM 
    Interventions
GROUP BY 
    ActionType;
