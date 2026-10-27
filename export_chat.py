import os
import json
import sys
import re

def get_next_number(directory):
    max_num = 0
    pattern = re.compile(r'^(\d{3})\s*-')
    for fname in os.listdir(directory):
        match = pattern.match(fname)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1

def export_markdown(uuid, chat_name, output_dir):
    # Try to find the highly-readable transcript JSONL file automatically created by the IDE
    transcript_path = os.path.join(
        os.path.expanduser(r"~\.gemini\antigravity-ide\brain"), 
        uuid, 
        r".system_generated\logs\transcript_full.jsonl"
    )
    
    if not os.path.exists(transcript_path):
        transcript_path = transcript_path.replace("transcript_full.jsonl", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            print(f"Error: Could not find a readable transcript for conversation {uuid}")
            print(f"Checked path: {transcript_path}")
            return False
            
    print(f"Reading readable transcript from {transcript_path}...")
    
    next_num = get_next_number(output_dir)
    safe_name = "".join([c for c in chat_name if c.isalnum() or c in " -_"]).strip()
    filename = f"{next_num:03d} - {safe_name}.md"
    output_file = os.path.join(output_dir, filename)
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"# {chat_name}\n\n")
        for line in lines:
            try:
                data = json.loads(line)
                source = data.get("source")
                content = data.get("content", "").strip()
                type_ = data.get("type")
                
                # We only want to export the actual back-and-forth chat text, skipping backend tool outputs
                if not content:
                    continue
                    
                if source == "USER_EXPLICIT" and type_ == "USER_INPUT":
                    out.write(f"### User\n\n{content}\n\n---\n\n")
                elif source == "MODEL" and type_ == "PLANNER_RESPONSE":
                    out.write(f"### Antigravity\n\n{content}\n\n---\n\n")
                    
            except Exception as e:
                pass
                
    print(f"Successfully exported Markdown chat to {output_file}")
    return True

def get_latest_conversation(conversations_dir):
    try:
        db_files = [os.path.join(conversations_dir, f) for f in os.listdir(conversations_dir) if f.endswith('.db')]
        if not db_files:
            return None
        return max(db_files, key=os.path.getmtime)
    except Exception as e:
        print(f"Error finding latest conversation: {e}")
        return None

if __name__ == "__main__":
    conversations_dir = os.path.expanduser(r"~\.gemini\antigravity-ide\conversations")
    db_path = None
    
    if len(sys.argv) > 2:
        db_path = sys.argv[2]
        chat_name = sys.argv[1]
    elif len(sys.argv) > 1:
        if sys.argv[1].endswith(".db"):
            db_path = sys.argv[1]
            chat_name = os.path.splitext(os.path.basename(db_path))[0]
        else:
            chat_name = sys.argv[1]
            db_path = get_latest_conversation(conversations_dir)
    else:
        db_path = get_latest_conversation(conversations_dir)
        chat_name = os.path.splitext(os.path.basename(db_path))[0] if db_path else "Unknown Chat"
        
    if not db_path or not os.path.exists(db_path):
        print(f"Error: Could not determine a valid database path. Check if conversations exist in {conversations_dir}")
        sys.exit(1)
        
    uuid = os.path.splitext(os.path.basename(db_path))[0]
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exported-conversations")
    os.makedirs(output_dir, exist_ok=True)
    
    export_markdown(uuid, chat_name, output_dir)

