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

NY_VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:20070311T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:20071104T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
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
        line = lines[i].strip("\n")

        if line.startswith("SUMMARY:"):
            full_summary = line
            while (i + 1 < len(lines)) and lines[i + 1].startswith("\t"):
                i += 1
                full_summary += lines[i + 1].strip()
            content = full_summary[len("SUMMARY:"):]
            reordered = reorder_summary(content)
            new_lines.append(f"SUMMARY:{reordered}\n")

        elif line.startswith("X-WR-CALNAME:"):
            new_lines.append("X-WR-CALNAME:Fall 2025\n")
            inserted_calname = True

        elif line.startswith("CALSCALE:"):
            # Keep CALSCALE
            new_lines.append(line + "\n")
            # Insert calname if missing
            if not inserted_calname:
                new_lines.append("X-WR-CALNAME:Fall 2025\n")
                inserted_calname = True
            # Insert timezone block if missing
            if not inserted_timezone:
                new_lines.append("X-WR-TIMEZONE:America/New_York\n")
                new_lines.append(NY_VTIMEZONE + "\n")
                inserted_timezone = True

        elif line.startswith("DTSTART:") or line.startswith("DTEND:"):
            tag, value = line.split(":", 1)
            if value.endswith("Z"):  # drop Z and add TZID
                value = value[:-1]
            new_lines.append(f"{tag};TZID=America/New_York:{value}\n")

        elif line.startswith("DTSTART;TZID") or line.startswith("DTEND;TZID"):
            # Normalize to America/New_York if another TZID is present
            prop, value = line.split(":", 1)
            new_lines.append(f"{prop.split(';')[0]};TZID=America/New_York:{value}\n")

        else:
            new_lines.append(line + "\n")

        i += 1

    Path(output_path).write_text("".join(new_lines), encoding="utf-8")

if __name__ == "__main__":
    process_ics_file("raw.ics", "processed.ics")
