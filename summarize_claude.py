import os
import json
import glob
import requests
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION
CLAUDE_LOGS_DIR = os.path.expanduser("~/.claude/projects")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"
HOURS_TO_LOOKBACK = 24  # Process files from the last N hours
PROMPT = """
You are a Senior Software Engineer and expert mentor analyzing a junior developer's coding session with **Claude Code** — an agentic AI coding assistant that can read/write files, run terminal commands, search codebases, and autonomously complete multi-step tasks.

Your goal: Extract actionable learning points that help this junior developer grow faster.

---

## ANALYSIS INSTRUCTIONS:

Analyze the above session and provide insights in these categories. Be specific, cite examples from the transcript, and focus on what's immediately actionable.

### TECHNICAL CONCEPTS LEARNED
- New language features, patterns, or frameworks introduced
- **Why** certain approaches were chosen (architecture decisions, tradeoffs)
- Concepts the junior should study deeper (with brief explanation of what to focus on)

### PROBLEM-SOLVING & DEBUGGING INSIGHTS
- How the problem was decomposed into smaller steps
- Debugging strategies demonstrated (print statements, logging, isolating issues)
- How edge cases or error scenarios were identified
- Any "aha moments" where the approach shifted

### PITFALLS, MISTAKES & TRADEOFFS
- Errors made and how they were caught/fixed
- Common mistakes to avoid in similar situations
- Tradeoffs discussed (performance vs readability, speed vs correctness, etc.)
- Security, scalability, or maintainability concerns raised

### CODE QUALITY & BEST PRACTICES
- Naming conventions, code organization, or structure improvements
- DRY (Don't Repeat Yourself) opportunities identified
- Error handling patterns demonstrated
- Testing strategies or suggestions made

### CLAUDE CODE PROMPTING EFFECTIVENESS
This section is critical — analyze how effectively the junior used Claude Code:

**What worked well:**
- Prompts that gave clear context (the "why" behind the task)
- Good use of specificity (file names, function names, expected behavior)
- Effective multi-step task delegation
- Smart use of Claude Code's capabilities (file search, codebase understanding)

**What could be improved:**
- Vague prompts that required clarification (quote them)
- Missing context that would have helped (project structure, dependencies, constraints)
- Times when smaller, focused prompts would have worked better than large ones
- Opportunities to use commands like `/compact`, `/clear`, or `CLAUDE.md` for context

**Claude Code-specific tips for next time:**
- When to let Claude Code be autonomous vs when to guide step-by-step
- How to phrase requests to leverage its agentic capabilities
- How to review and verify Claude Code's file changes effectively
- When to ask for explanations vs when to ask for implementation

### ACTION ITEMS FOR THE JUNIOR
Provide 3-5 specific, prioritized things the junior should:
1. **Practice** — Hands-on exercises to reinforce learning
2. **Study** — Topics/docs to read with specific focus areas
3. **Remember** — Key takeaways to internalize

---

## OUTPUT FORMAT:
- Use bullet points for readability
- Be concise but specific — cite examples from the transcript when helpful
- Skip any category that has no relevant insights (don't force it)
- End with an encouraging note about growth observed in this session
---

## TRANSCRIPT TO ANALYZE:
{TRANSCRIPT}
"""

def get_session_files_since(hours=None):
    """Find all .jsonl files created in the last N hours"""
    if hours is None:
        hours = HOURS_TO_LOOKBACK
    
    files = glob.glob(f"{CLAUDE_LOGS_DIR}/**/*.jsonl", recursive=True)
    if not files:
        return []
    
    cutoff_time = datetime.now().timestamp() - (hours * 3600)
    recent_files = []
    
    for file_path in files:
        if os.path.getctime(file_path) >= cutoff_time:
            recent_files.append(file_path)
    
    return sorted(recent_files, key=os.path.getctime)  # Oldest first

def extract_message_content(data):
    """Extract text content from Claude Code message structure"""
    message = data.get('message', {})
    content = message.get('content')
    
    if content is None:
        return None
    
    # User messages: content is a string
    if isinstance(content, str):
        return content.strip() if content.strip() else None
    
    # Assistant messages: content is a list of content blocks
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                text = block.get('text', '')
                if text.strip():
                    texts.append(text.strip())
        return "\n".join(texts) if texts else None
    
    return None

def parse_conversation(file_path):
    """Parse a single conversation file"""
    conversation = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                # Check top-level 'type' first, fall back to message.role
                msg_type = data.get('type') or data.get('message', {}).get('role')
                text = extract_message_content(data)
                
                if msg_type == 'user' and text:
                    conversation.append(f"ME: {text}")
                elif msg_type == 'assistant' and text:
                    conversation.append(f"Mentor: {text}")
            except:
                continue
    return "\n".join(conversation)

def parse_multiple_conversations(file_paths):
    """Parse multiple conversation files and combine them"""
    all_conversations = []
    
    for file_path in file_paths:
        conversation = parse_conversation(file_path)
        if conversation:
            # Add separator between sessions
            file_name = os.path.basename(file_path)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            all_conversations.append(f"\n--- Session: {file_name} ({file_time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
            all_conversations.append(conversation)
    
    return "\n".join(all_conversations)

def generate_summary(conversation_text):
    if not conversation_text:
        return "No conversation data available"
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT.format(TRANSCRIPT=conversation_text),
        config=config,
    )

    return response.text

def send_to_slack(summary):
    """Send the summary to Slack"""
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("ERROR: SLACK_WEBHOOK_URL is not set")
        return False
    
    if not summary:
        print("ERROR: No summary to send")
        return False
    
    slack_message = {
        "text": summary,
    }
    
    try:
        response = requests.post(slack_webhook_url, json=slack_message)
        if response.status_code == 200:
            print(f"✓ Successfully sent to Slack")
            return True
        else:
            print(f"ERROR: Slack returned status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to send to Slack: {e}")
        return False