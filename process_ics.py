# process_ics.py

def reorder_summary(summary):
    parts = [part.strip() for part in summary.split('&bull\\;')]
    if len(parts) != 3:
        return summary
    return f"{parts[2]} • {parts[1]} • {parts[0]}"

def process_ics_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("SUMMARY:"):
            full_summary = line.strip()
            while (i + 1 < len(lines)) and lines[i + 1].startswith('\t'):
                i += 1
                full_summary += lines[i].strip()
            original_content = full_summary[len("SUMMARY:"):]
            reordered = reorder_summary(original_content)
            new_lines.append(f"SUMMARY:{reordered}\n")
        else:
            new_lines.append(line)
        i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

process_ics_file('raw.ics', 'processed.ics')
