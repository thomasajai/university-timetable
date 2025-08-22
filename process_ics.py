from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# Your existing summary reordering
def reorder_summary(summary):
    parts = [part.strip() for part in summary.split('&bull\\;')]
    if len(parts) != 3:
        return summary
    return f"{parts[2]} • {parts[1]} • {parts[0]}"

# Convert UTC datetime string to Eastern local time string
def convert_to_eastern(utc_str):
    utc_dt = datetime.strptime(utc_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
    eastern_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
    return eastern_dt.strftime("%Y%m%dT%H%M%S")  # No 'Z'

# The timezone header to prepend
VTIMEZONE_BLOCK = """BEGIN:VCALENDAR
PRODID:-//Google Inc//Google Calendar 70.9054//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Fall 2025 Calendar
X-WR-TIMEZONE:America/New_York
BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE
"""

def process_ics_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [VTIMEZONE_BLOCK + "\n"]  # Start with timezone block
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

        elif line.startswith("DTSTART:") or line.startswith("DTEND:"):
            tag, utc_value = line.strip().split(":")
            eastern_value = convert_to_eastern(utc_value)
            new_lines.append(f"{tag};TZID=America/New_York:{eastern_value}\n")

        elif line.startswith("BEGIN:VCALENDAR"):
            # Skip original VCALENDAR header
            pass
        elif line.startswith("END:VCALENDAR"):
            new_lines.append("END:VCALENDAR\n")
        else:
            new_lines.append(line)

        i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

process_ics_file('raw.ics', 'processed.ics')
