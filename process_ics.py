from pathlib import Path

def reorder_summary(summary: str) -> str:
    """
    Example rule: split on '&bull;' and reorder.
    Adjust this logic to fit your formatting needs.
    """
    parts = [part.strip() for part in summary.split('&bull\\;')]
    if len(parts) != 3:
        return summary
    return f"{parts[2]} • {parts[1]} • {parts[0]}"

UTC_VTIMEZONE = """BEGIN:VTIMEZONE
TZID:UTC
X-LIC-LOCATION:UTC
BEGIN:STANDARD
TZOFFSETFROM:+0000
TZOFFSETTO:+0000
TZNAME:UTC
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
"""

def process_ics_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    inserted_calname = False
    inserted_timezone = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("SUMMARY:"):
            full_summary = line.strip()
            # Handle multi-line SUMMARY continuation lines
            while (i + 1 < len(lines)) and lines[i + 1].startswith("\t"):
                i += 1
                full_summary += lines[i].strip()
            content = full_summary[len("SUMMARY:"):]
            reordered = reorder_summary(content)
            new_lines.append(f"SUMMARY:{reordered}\n")

        elif line.startswith("X-WR-CALNAME:"):
            new_lines.append("X-WR-CALNAME:Fall 2025\n")
            inserted_calname = True

        elif line.startswith("CALSCALE:"):
            # Insert after CALSCALE
            new_lines.append(line)
            if not inserted_calname:
                new_lines.append("X-WR-CALNAME:Fall 2025\n")
                inserted_calname = True
            if not inserted_timezone:
                new_lines.append("X-WR-TIMEZONE:UTC\n")
                new_lines.append(UTC_VTIMEZONE + "\n")
                inserted_timezone = True
            i += 1
            continue

        else:
            new_lines.append(line)

        i += 1

    Path(output_path).write_text("".join(new_lines), encoding="utf-8")

if __name__ == "__main__":
    process_ics_file("raw.ics", "processed.ics")
