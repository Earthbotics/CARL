#!/usr/bin/env python3
"""
CARL Communication Tools

This module provides tools for generating communication reports from CARL's logs.
It can be integrated into the main CARL system for on-demand report generation.

Usage:
    from carl_communication_tools import generate_communication_report, generate_stop_bot_report
    
    # Generate a communication report
    report_file = generate_communication_report("path/to/logfile.txt")
    
    # Generate a stop bot report
    stop_report = generate_stop_bot_report("path/to/logfile.txt")
"""

import os
import sys
from datetime import datetime
from typing import Optional
from generate_communication_report import CARLCommunicationAnalyzer

def generate_communication_report(log_file: str = "tests/test_results.txt", 
                                output_file: Optional[str] = None) -> str:
    """
    Generate a comprehensive communication report from CARL logs.
    
    Args:
        log_file: Path to the log file to analyze
        output_file: Optional custom output file path
        
    Returns:
        Path to the generated report file
    """
    if not os.path.exists(log_file):
        raise FileNotFoundError(f"Log file '{log_file}' not found.")
    
    # Create analyzer
    analyzer = CARLCommunicationAnalyzer(log_file)
    
    # Generate report filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"CARL_Communication_Report_{timestamp}.md"
    
    # Generate and save report
    analyzer.save_report(output_file)
    
    return output_file

def generate_stop_bot_report(log_file: str = "tests/test_results.txt") -> str:
    """
    Generate a stop bot report with communication summary.
    
    Args:
        log_file: Path to the log file to analyze
        
    Returns:
        Path to the generated report file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"CARL_StopBot_Report_{timestamp}.md"
    
    return generate_communication_report(log_file, output_file)

def get_conversation_summary(log_file: str = "tests/test_results.txt") -> dict:
    """
    Get a quick summary of the conversation without generating a full report.
    
    Args:
        log_file: Path to the log file to analyze
        
    Returns:
        Dictionary with conversation statistics
    """
    if not os.path.exists(log_file):
        raise FileNotFoundError(f"Log file '{log_file}' not found.")
    
    analyzer = CARLCommunicationAnalyzer(log_file)
    lines = analyzer.load_log_file()
    analyzer.extract_conversation_data(lines)
    
    return analyzer.calculate_statistics()

def main():
    """Command line interface for the communication tools."""
    if len(sys.argv) < 2:
        print("Usage: python carl_communication_tools.py <command> [log_file]")
        print("Commands:")
        print("  report     - Generate full communication report")
        print("  stop       - Generate stop bot report")
        print("  summary    - Show conversation summary")
        sys.exit(1)
    
    command = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else "tests/test_results.txt"
    
    try:
        if command == "report":
            report_file = generate_communication_report(log_file)
            print(f"✅ Communication report generated: {report_file}")
            
        elif command == "stop":
            report_file = generate_stop_bot_report(log_file)
            print(f"🛑 Stop bot report generated: {report_file}")
            
        elif command == "summary":
            stats = get_conversation_summary(log_file)
            print("📊 Conversation Summary:")
            print(f"  User Inputs: {stats['total_user_inputs']}")
            print(f"  CARL Responses: {stats['total_carl_responses']}")
            print(f"  Response Rate: {stats['response_rate']:.1f}%")
            print(f"  Session Duration: {stats['session_duration']}")
            print(f"  Body Movements: {stats['total_body_movements']}")
            print(f"  Eye Expressions: {stats['total_eye_expressions']}")
            
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
