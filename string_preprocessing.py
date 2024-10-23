import re


def normalize_spoken_email(spoken_email):
    replacements = {
        " dot ": ".",
        " period ": ".",
        " at the rate ": "@",
        " at ": "@",
        "g mail dot com": "gmail.com",
        "gmail dot com": "gmail.com",
        " g mail ": "gmail",
    }

    # Normalize spoken email by replacing phrases
    for phrase, replacement in replacements.items():
        spoken_email = spoken_email.replace(phrase, replacement)

    # Handle cases where "therate" might appear due to speech recognition
    spoken_email = re.sub(
        r'(the rate)([a-zA-Z.]+)', lambda match: f"@{match.group(2)}", spoken_email)

    # Remove extra spaces and trim
    spoken_email = re.sub(r'\s+', ' ', spoken_email).strip()

    return spoken_email.lower()


def process_recognition_results(result, id):
    q = result.strip()

    # Normalize email if needed
    if id == "email":
        q = normalize_spoken_email(q)
        q = q.replace(" ", "")
    elif id == "pnr":
        q = q.replace(" ", "")

    return q
