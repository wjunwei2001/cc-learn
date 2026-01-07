from summarize_claude import get_session_files_since, parse_multiple_conversations, generate_summary, send_to_slack, HOURS_TO_LOOKBACK

def main():
    print("Hello from cc-learn!")
    print(f"Looking for session files from the last {HOURS_TO_LOOKBACK} hours...")
    
    files = get_session_files_since()
    if not files:
        print("No claude session files found in the specified time range")
        return
    
    print(f"Found {len(files)} session file(s) to process")
    
    print("Parsing conversations...")
    conversation_text = parse_multiple_conversations(files)
    print(f"Parsed {len(conversation_text)} characters of conversation text")
    
    print("Generating summary with Gemini (this may take a while)...")
    summary = generate_summary(conversation_text)
    print(f"Summary generated ({len(summary)} characters)")
    
    print("Sending to Slack...")
    send_to_slack(summary)
    print("Done!")


if __name__ == "__main__":
    main()
