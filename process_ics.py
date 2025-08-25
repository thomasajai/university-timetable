import re

input_file = "raw.ics"
output_file = "processed.ics"

with open(input_file, "r", encoding="utf-8") as f:
    ics_data = f.read()

# Unfold lines: lines that start with space or tab are continuations
ics_data = re.sub(r'\n[ \t]', '', ics_data)

# Update calendar name
ics_data = re.sub(r"(BEGIN:VCALENDAR\n.*?)(?=BEGIN:VEVENT)", r"\1X-WR-CALNAME:Fall 2025\n", ics_data, flags=re.DOTALL)

# Function to rearrange event summary
def rearrange_summary(match):
    summary = match.group(1)
    # Replace HTML entity &bull; or escaped \; with proper bullet
    summary = summary.replace("&bull\\;", "•").replace("&bull;", "•")
    parts = [part.strip() for part in summary.split("•")]
    if len(parts) == 3:
        course, section, name = parts
        new_summary = f"{name} • {section} • {course}"
        return f"SUMMARY:{new_summary}"
    else:
        # leave as-is if unexpected format
        return f"SUMMARY:{summary}"

# Replace each SUMMARY line
ics_data = re.sub(r"SUMMARY:(.+)", rearrange_summary, ics_data)

# Write to new file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(ics_data)

print(f"Processed ICS file written to {output_file}")
