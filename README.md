# CC-Learn 📚

**Turn your Claude Code sessions into daily learning summaries.**

CC-Learn automatically analyzes your Claude Code conversations, extracts key learning points, and sends them to Slack — helping junior developers maximize learning from AI-assisted coding.

## Why?

When you use Claude Code, you're essentially pair programming with a senior engineer. But it's easy to miss the lessons hidden in those conversations:

- Why did Claude suggest that approach?
- What pitfalls did it help you avoid?
- How could you have prompted better?

CC-Learn captures these insights automatically, so you can learn even when you're too busy coding to reflect.

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd cc-learn
uv sync  # or: pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Get your API keys:**
- [Gemini API Key](https://aistudio.google.com/app/apikey)
- [Slack Webhook URL](https://api.slack.com/messaging/webhooks)

### 3. Run it

```bash
uv run main.py
# or: python main.py
```

## Configuration

Edit `summarize_claude.py` to customize:

```python
# How far back to look for sessions (in hours)
HOURS_TO_LOOKBACK = 24

# Which Gemini model to use
MODEL = "gemini-2.5-flash"  # or "gemini-2.5-pro" for deeper analysis

# Where Claude Code stores session logs
CLAUDE_LOGS_DIR = os.path.expanduser("~/.claude/projects")
```

## Automate with Cron

### Linux/macOS

```bash
# Edit crontab
crontab -e

# Run every day at 6 PM
0 18 * * * cd /path/to/cc-learn && /path/to/python main.py >> /var/log/cc-learn.log 2>&1
```

### Windows (Task Scheduler)

1. Create `run_summary.bat`:
```batch
@echo off
cd C:\Users\user\cc-learn
uv run main.py
```

2. Open Task Scheduler → Create Basic Task → Set your schedule → Action: Start a program → Browse to `run_summary.bat`

## Example Output

```
### TECHNICAL CONCEPTS LEARNED
- Learned about the `glob` module for recursive file searching
- Understood JSONL format parsing with line-by-line JSON decoding
- **Why**: JSONL is preferred for log files because each line is independent

### PROBLEM-SOLVING & DEBUGGING INSIGHTS
- Encountered UnicodeDecodeError on Windows — fixed by specifying `encoding="utf-8"`
- Problem was decomposed: first get files → parse → summarize → send

### CLAUDE CODE PROMPTING EFFECTIVENESS
**What worked well:**
- Asking "why is this bug here?" with terminal output attached
- Providing the actual JSONL structure to help debug parsing

**Tips for next time:**
- When debugging, always share the actual data format
- Let Claude Code read error messages directly from terminal

### ACTION ITEMS
1. **Practice** — Write a script that parses another JSONL format
2. **Study** — Python's `json` module and encoding handling
3. **Remember** — Always specify encoding when opening files on Windows
```

## Requirements

- Python 3.12+
- Claude Code (session logs at `~/.claude/projects`)
- Gemini API key
- Slack webhook URL

## License

MIT — do whatever you want with it.

---

**Built to help junior developers learn faster from AI-assisted coding.** 🚀
