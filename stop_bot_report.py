#!/usr/bin/env python3
"""
CARL Stop Bot Report Generator

This script provides a quick "stop bot" functionality that generates
a communication report when CARL is stopped or when requested.

Usage:
    python stop_bot_report.py [log_file_path]
    
This can be integrated into the main CARL system as a shutdown hook.
"""

import os
import sys
import re
from datetime import datetime
from generate_communication_report import CARLCommunicationAnalyzer

def generate_stop_bot_report(log_file: str = "tests/test_results.txt") -> str:
    """
    Generate a stop bot report with communication summary and conversation quick-review.
    
    Args:
        log_file: Path to the log file to analyze
        
    Returns:
        Path to the generated report file
    """
    print("🛑 Generating Stop Bot Report...")
    
    # Create analyzer
    analyzer = CARLCommunicationAnalyzer(log_file)
    
    # Generate timestamped report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"CARL_StopBot_Report_{timestamp}.md"
    
    # Generate and save report
    analyzer.save_report(report_filename)
    
    # Generate conversation quick-review
    quick_review_filename = f"CONVERSATION_QUICK-REVIEW_{timestamp}.md"
    generate_conversation_quick_review(log_file, quick_review_filename)
    
    print(f"📋 Stop Bot Report generated: {report_filename}")
    print(f"💬 Conversation Quick-Review generated: {quick_review_filename}")
    return report_filename

def generate_conversation_quick_review(log_file: str, output_file: str) -> str:
    """
    Generate a conversation quick-review with CARL says and User lines in chronological order.
    
    Args:
        log_file: Path to the log file to analyze
        output_file: Path to save the quick-review report
        
    Returns:
        Path to the generated quick-review file
    """
    print("💬 Generating Conversation Quick-Review...")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: Log file '{log_file}' not found.")
        return ""
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return ""
    
    # Extract conversation entries
    conversation_entries = []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Extract CARL says entries
        if "🔊 CARL says:" in line:
            # Extract timestamp and message
            timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
            
            # Extract the actual message
            message_match = re.search(r'🔊 CARL says: (.+)', line)
            message = message_match.group(1) if message_match else ""
            
            conversation_entries.append({
                'line': line_num,
                'timestamp': timestamp,
                'type': 'CARL',
                'content': message
            })
        
        # Extract User entries
        elif line.startswith("User:"):
            user_input = line[5:].strip()  # Remove "User:" prefix
            timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
            
            conversation_entries.append({
                'line': line_num,
                'timestamp': timestamp,
                'type': 'User',
                'content': user_input
            })
    
    # Sort by timestamp
    conversation_entries.sort(key=lambda x: x['timestamp'])
    
    # Generate the quick-review report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# CONVERSATION QUICK-REVIEW\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Source:** {log_file}\n\n")
        f.write("## Chronological Conversation Flow\n\n")
        f.write("This report shows the conversation between User and CARL in chronological order.\n\n")
        f.write("---\n\n")
        
        for entry in conversation_entries:
            f.write(f"**Line {entry['line']}:** {entry['timestamp']}: {entry['type']}: {entry['content']}\n\n")
        
        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total User inputs:** {len([e for e in conversation_entries if e['type'] == 'User'])}\n")
        f.write(f"- **Total CARL responses:** {len([e for e in conversation_entries if e['type'] == 'CARL'])}\n")
        f.write(f"- **Total conversation entries:** {len(conversation_entries)}\n\n")
        
        if conversation_entries:
            f.write("## Session Duration\n\n")
            start_time = conversation_entries[0]['timestamp']
            end_time = conversation_entries[-1]['timestamp']
            f.write(f"- **Start:** {start_time}\n")
            f.write(f"- **End:** {end_time}\n\n")
        
        f.write("---\n\n")
        f.write("*This report was generated automatically by CARL's communication analysis system.*\n")
    
    print(f"✅ Conversation Quick-Review generated: {output_file}")
    return output_file

def main():
    """Main function for stop bot report generation."""
    log_file = sys.argv[1] if len(sys.argv) > 1 else "tests/test_results.txt"
    
    if not os.path.exists(log_file):
        print(f"❌ Error: Log file '{log_file}' not found.")
        sys.exit(1)
    
    report_file = generate_stop_bot_report(log_file)
    print(f"✅ Stop Bot Report ready: {report_file}")

if __name__ == "__main__":
    main()
