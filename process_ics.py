from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

def reorder_summary(summary: str) -> str:
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

def utc_to_et(utc_str: str) -> str:
    """Convert UTC time string (YYYYMMDDTHHMMSSZ) → America/New_York wall time string"""
    utc_dt = datetime.strptime(utc_str, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
    et_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
    return et_dt.strftime("%Y%m%dT%H%M%S")

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
            new_lines.append(line + "\n")
            if not inserted_calname:
                new_lines.append("X-WR-CALNAME:Fall 2025\n")
                inserted_calname = True
            if not inserted_timezone:
                new_lines.append("X-WR-TIMEZONE:America/New_York\n")
                new_lines.append(NY_VTIMEZONE + "\n")
                inserted_timezone = True

        elif line.startswith("DTSTART:") or line.startswith("DTEND:"):
            tag, value = line.split(":", 1)
            if value.endswith("Z"):  # convert UTC → ET
                value = utc_to_et(value)
            new_lines.append(f"{tag};TZID=America/New_York:{value}\n")

        else:
            new_lines.append(line + "\n")

        i += 1

    Path(output_path).write_text("".join(new_lines), encoding="utf-8")

if __name__ == "__main__":
    process_ics_file("raw.ics", "processed.ics")
