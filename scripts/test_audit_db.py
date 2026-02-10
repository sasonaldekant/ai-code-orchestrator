"""
Verification script for database-backed AuditLogger.
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audit_logger import AuditLogger

def main():
    print("=== AuditLogger SQLite Backend Test ===\n")
    
    # Path to test DB
    db_path = "outputs/audit_logs/test_audit.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    logger = AuditLogger(db_path=db_path)
    
    # Log some dummy actions
    print("Logging dummy actions...")
    logger.log_action("AnalystAgent", "requirements_gathering", {"feature": "Login"}, cost=0.005)
    logger.log_action("ArchitectAgent", "system_design", {"complexity": "medium"}, cost=0.012)
    logger.log_action("DeveloperAgent", "completion", {"files": ["main.py"]}, cost=0.045)
    logger.log_action("DeveloperAgent", "completion", {"files": ["utils.py"]}, cost=0.030)
    logger.log_action("QualityAgent", "reviewer_error", {"msg": "timeout"}, cost=0.001)
    
    # Retrieve logs
    print("\nRetrieving last 3 logs:")
    logs = logger.get_logs(limit=3)
    for log in logs:
        print(f" - [{log['timestamp']}] Agent: {log['agent']}, Action: {log['action']}, Cost: ${log['cost']:.4f}")
        
    # Generate Report
    print("\nGenerating Aggregate Report...")
    report = logger.generate_report()
    print("\n" + "="*40)
    print(report)
    print("="*40)
    
    if "Total Actions Logged: 5" in report and "$0.0930" in report:
        print("\nSUCCESS: AuditLogger verified.")
    else:
        print("\nWARNING: Report values mismatch.")

if __name__ == "__main__":
    main()
