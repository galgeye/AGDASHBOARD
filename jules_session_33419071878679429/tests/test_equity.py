import unittest
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from equity import calculate_risk_ratio

class TestEquityLogic(unittest.TestCase):
    def setUp(self):
        # Setup mock data
        self.students = pd.DataFrame({
            'Student_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Ethnicity': ['GroupA', 'GroupA', 'GroupA', 'GroupA', 'GroupB', 'GroupB', 'GroupB', 'GroupB', 'GroupB', 'GroupB']
        })
        # 4 students in GroupA, 6 in GroupB
        
        self.incidents = pd.DataFrame({
            'Incident_ID': [101, 102, 103],
            'Student_ID': [1, 2, 5], # 2 from GroupA, 1 from GroupB
            'BehaviorType': ['Suspension', 'Suspension', 'Suspension']
        })

    def test_risk_ratio_calculation(self):
        # GroupA Risk: 2 incidents / 4 students = 0.5
        # GroupB Risk: 1 incident / 6 students = 0.1666...
        # Ratio: 0.5 / 0.1666... = 3.0
        
        ratio = calculate_risk_ratio(self.students, self.incidents, 'Ethnicity', 'GroupA', 'Suspension')
        self.assertAlmostEqual(ratio, 3.0)

    def test_no_incidents(self):
        # Case where no one has incidents
        empty_incidents = pd.DataFrame(columns=['Incident_ID', 'Student_ID', 'BehaviorType'])
        ratio = calculate_risk_ratio(self.students, empty_incidents, 'Ethnicity', 'GroupA', 'Suspension')
        # Risk A = 0, Risk B = 0. Division by zero handled?
        # If comp_risk is 0, function returns inf. 
        # But here target_risk is also 0. 0/0 is undefined.
        # Let's see how the function handles it.
        # target_risk = 0. comp_risk = 0.
        # Returns inf based on current logic.
        self.assertEqual(ratio, float('inf')) 

if __name__ == '__main__':
    unittest.main()
