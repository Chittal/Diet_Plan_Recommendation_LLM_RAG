import re

def validate_symptoms(input):
    parts = input.split(",")
    pattern = r'^[a-zA-Z\s-]+$'
    if all(re.match(pattern, part) for part in parts):
        return 200, input
    else:
        return 400, "Please provide valid symptoms."
    

def check_questions(input):
    pattern = r'^[A-Za-z\s]+[\?]?$'
    if bool(re.match(pattern, input.strip())):
        return 200, input.strip()
    else:
        return 400, "Please provide a valid query."