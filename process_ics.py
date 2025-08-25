from pathlib import Path
from datetime import datetime, timedelta

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

def subtract_4h(utc_str: str) -> str:
    """Take YYYYMMDDTHHMMSSZ and subtract 4 hours, return local string."""
    dt = datetime.strptime(utc_str, "%Y%m%dT%H%M%SZ")
    dt = dt - timedelta(hours=4)
    return dt.strftime("%Y%m%dT%H%M%S")

def fix_times(infile="raw.ics", outfile="processed.ics"):
    out_lines = []
    with open(infile, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("DTSTART:") or line.startswith("DTEND:"):
                tag, val = line.strip().split(":", 1)
                if val.endswith("Z"):
                    local_val = subtract_4h(val)
                    out_lines.append(f"{tag};TZID=America/New_York:{local_val}\n")
                else:
                    out_lines.append(line)
            elif line.startswith("CALSCALE:"):
                out_lines.append(line)
                out_lines.append("X-WR-CALNAME:Fall 2025\n")
                out_lines.append("X-WR-TIMEZONE:America/New_York\n")
                out_lines.append(NY_VTIMEZONE + "\n")
            else:
                out_lines.append(line)

    Path(outfile).write_text("".join(out_lines), encoding="utf-8")

if __name__ == "__main__":
    fix_times()
