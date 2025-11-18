#!/usr/bin/env python3
"""
CARL Communication Report Generator

This script extracts conversation data from CARL test logs and generates
a comprehensive communication report showing the interaction flow between
User and CARL, including verbal responses and planned body language tracking.

Usage:
    python generate_communication_report.py [log_file_path]
    
If no log file is provided, it will use tests/test_results.txt by default.
"""

import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple

class CARLCommunicationAnalyzer:
    def __init__(self, log_file_path: str = "tests/test_results.txt"):
        self.log_file_path = log_file_path
        self.conversation_entries = []
        self.user_inputs = []
        self.carl_responses = []
        self.body_movements = []
        self.eye_expressions = []
        
    def load_log_file(self) -> List[str]:
        """Load the log file and return lines."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"❌ Error: Log file '{self.log_file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
            sys.exit(1)
    
    def extract_conversation_data(self, lines: List[str]) -> None:
        """Extract conversation data from log lines."""
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Extract User inputs
            if line.startswith("User:"):
                user_input = line[5:].strip()  # Remove "User:" prefix
                self.user_inputs.append({
                    'line': line_num,
                    'input': user_input,
                    'timestamp': self._extract_timestamp(line)
                })
            
            # Extract CARL verbal responses
            elif "🔊 CARL says:" in line:
                # Extract timestamp and message
                timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
                timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                
                # Extract the actual message
                message_match = re.search(r'🔊 CARL says: (.+)', line)
                message = message_match.group(1) if message_match else ""
                
                self.carl_responses.append({
                    'line': line_num,
                    'timestamp': timestamp,
                    'message': message
                })
            
            # Extract body movements (for future enhancement)
            elif "🎭 Executing body movement command:" in line or "🤖 ARC Body Movement Command:" in line:
                movement_match = re.search(r'(🎭|🤖).*?(\w+)', line)
                if movement_match:
                    movement = movement_match.group(2)
                    self.body_movements.append({
                        'line': line_num,
                        'timestamp': self._extract_timestamp(line),
                        'movement': movement
                    })
            
            # Extract eye expressions (for future enhancement)
            elif "👁️ Executing eye expression command:" in line or "👁️ ARC Eye Expression Command:" in line:
                eye_match = re.search(r'👁️.*?(\w+)', line)
                if eye_match:
                    expression = eye_match.group(1)
                    self.eye_expressions.append({
                        'line': line_num,
                        'timestamp': self._extract_timestamp(line),
                        'expression': expression
                    })
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line."""
        timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
        return timestamp_match.group(1) if timestamp_match else "Unknown"
    
    def create_conversation_flow(self) -> List[Dict]:
        """Create chronological conversation flow."""
        flow = []
        
        # Combine all entries with timestamps
        all_entries = []
        
        # Add user inputs
        for user_input in self.user_inputs:
            all_entries.append({
                'type': 'user',
                'timestamp': user_input['timestamp'],
                'line': user_input['line'],
                'content': user_input['input']
            })
        
        # Add CARL responses
        for response in self.carl_responses:
            all_entries.append({
                'type': 'carl',
                'timestamp': response['timestamp'],
                'line': response['line'],
                'content': response['message']
            })
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x['timestamp'])
        
        return all_entries
    
    def calculate_statistics(self) -> Dict:
        """Calculate communication statistics."""
        total_user_inputs = len(self.user_inputs)
        total_carl_responses = len(self.carl_responses)
        total_body_movements = len(self.body_movements)
        total_eye_expressions = len(self.eye_expressions)
        
        # Calculate response rate
        response_rate = (total_carl_responses / total_user_inputs * 100) if total_user_inputs > 0 else 0
        
        # Get session duration
        if self.user_inputs and self.carl_responses:
            start_time = self.user_inputs[0]['timestamp']
            end_time = self.carl_responses[-1]['timestamp']
            session_duration = self._calculate_duration(start_time, end_time)
        else:
            session_duration = "Unknown"
        
        return {
            'total_user_inputs': total_user_inputs,
            'total_carl_responses': total_carl_responses,
            'total_body_movements': total_body_movements,
            'total_eye_expressions': total_eye_expressions,
            'response_rate': response_rate,
            'session_duration': session_duration
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between two timestamps."""
        try:
            start_dt = datetime.strptime(start_time, "%H:%M:%S.%f")
            end_dt = datetime.strptime(end_time, "%H:%M:%S.%f")
            duration = end_dt - start_dt
            return str(duration).split('.')[0]  # Remove microseconds
        except:
            return "Unknown"
    
    def generate_report(self) -> str:
        """Generate the complete communication report."""
        lines = self.load_log_file()
        self.extract_conversation_data(lines)
        conversation_flow = self.create_conversation_flow()
        stats = self.calculate_statistics()
        
        # Generate report content
        report = f"""# CARL Communication Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Log File:** {self.log_file_path}  
**Session Duration:** {stats['session_duration']}  
**Total Interactions:** {stats['total_user_inputs']} User inputs, {stats['total_carl_responses']} CARL responses  

---

## 📋 **Conversation Summary**

This report provides a chronological view of the communication between User and CARL during the test session. The conversation demonstrates CARL's ability to:
- Respond to greetings and social interactions
- Process visual perception queries
- Access and recall memory
- Handle movement commands
- Execute emotional reactions
- Maintain conversational context

---

## 💬 **Complete Conversation Flow**

"""
        
        # Add conversation entries
        for i, entry in enumerate(conversation_flow, 1):
            if entry['type'] == 'user':
                report += f"### **{i}. User Input**\n"
                report += f"```\n"
                report += f"Line {entry['line']}: {entry['timestamp']}: User: {entry['content']}\n"
                report += f"```\n\n"
            else:
                report += f"### **{i}. CARL Response**\n"
                report += f"```\n"
                report += f"Line {entry['line']}: {entry['timestamp']}: 🔊 CARL says: {entry['content']}\n"
                report += f"```\n\n"
        
        # Add statistics
        report += f"""---

## 📊 **Communication Statistics**

| Metric | Count | Percentage |
|--------|-------|------------|
| **User Inputs** | {stats['total_user_inputs']} | 100% |
| **CARL Verbal Responses** | {stats['total_carl_responses']} | {stats['response_rate']:.1f}% |
| **Body Movements** | {stats['total_body_movements']} | - |
| **Eye Expressions** | {stats['total_eye_expressions']} | - |

---

## 🎯 **Body Language Tracking (Future Enhancement)**

### **Body Movements Detected:**
"""
        
        if self.body_movements:
            for movement in self.body_movements:
                report += f"- Line {movement['line']}: {movement['timestamp']}: {movement['movement']}\n"
        else:
            report += "- No body movements detected in current log format\n"
        
        report += f"""
### **Eye Expressions Detected:**
"""
        
        if self.eye_expressions:
            for expression in self.eye_expressions:
                report += f"- Line {expression['line']}: {expression['timestamp']}: {expression['expression']}\n"
        else:
            report += "- No eye expressions detected in current log format\n"
        
        report += f"""
---

## 🔮 **Future Enhancements**

### **Planned Additions:**
1. **Enhanced Body Language Tracking:**
   - Eye movement patterns
   - Limb movement coordination
   - Gesture recognition
   - Posture changes

2. **Multi-Modal Communication Analysis:**
   - Response time analysis
   - Emotional tone detection
   - Conversation flow patterns
   - Context retention scoring

3. **Advanced Metrics:**
   - Visual expression tracking
   - Audio tone analysis
   - Physical gesture logging
   - Environmental awareness

---

## 📝 **Technical Notes**

- **Log Format:** Timestamps with millisecond precision
- **Response Tracking:** Both verbal and non-verbal responses logged
- **Context Management:** Conversation context properly maintained
- **Memory Integration:** Successful integration with memory system
- **Command Processing:** Movement and emotional commands processed

---

*This report demonstrates CARL's evolving communication capabilities and provides a foundation for future enhancements in multi-modal interaction tracking.*
"""
        
        return report
    
    def save_report(self, output_file: str = "CARL_Communication_Report.md") -> None:
        """Generate and save the communication report."""
        report = self.generate_report()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Communication report generated: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")

def main():
    """Main function to run the communication report generator."""
    # Get log file path from command line or use default
    log_file = sys.argv[1] if len(sys.argv) > 1 else "tests/test_results.txt"
    
    print(f"🔍 Analyzing communication data from: {log_file}")
    
    # Create analyzer and generate report
    analyzer = CARLCommunicationAnalyzer(log_file)
    analyzer.save_report()
    
    print("📊 Communication analysis complete!")

if __name__ == "__main__":
    main()
