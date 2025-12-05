-- Task C: Top 5 Incident Hotspots
-- Requirement: Aggregation of "What" (Behavior Type) and "Where" (Location/Time).

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
