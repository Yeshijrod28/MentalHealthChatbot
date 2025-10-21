from typing import List
import random

CRISIS_KEYWORDS: List[str] = [
    "suicidal", "suicide", "kill myself", "want to die", "hopeless", "worthless",
    "can't go on", "give up", "ending it all", "no reason to live", "alone", 
    "depressed", "depression", "overwhelmed", "self-harm", "hurt myself", 
    "numb", "pain", "destroy myself", "die", "hopelessness", "failure", 
    "useless", "life not worth living", "burden", "suffering", "exhausted", 
    "trapped", "escape", "end it", "can't handle it", "worthless life", 
    "tired of living"
]

SAFETY_MESSAGES = [
    "💡 It sounds like you're going through a really tough time. "
    "You're not alone, and there are people who want to help you. "
    "Please consider reaching out to a mental health professional or contacting a helpline:\n\n"
    "(+975) 02 332862, enquiry@thepema.gov.bt\n"
    "You matter. ❤️❤️❤️",

    "💖 I'm really concerned about you. Remember, asking for help is a sign of strength. "
    "You can call a trained professional for support:\n\n"
    "(+975) 02 332862, enquiry@thepema.gov.bt\n"
    "You are important and loved. 🌟",

    "🛑 It sounds like you're feeling overwhelmed. "
    "Please reach out to someone you trust or a mental health professional immediately:\n\n"
    "(+975) 02 332862, enquiry@thepema.gov.bt\n"
    "Your life is valuable. 💛",

    "🌈 Even in tough times, you are not alone. "
    "Talking to a trained listener can help:\n\n"
    "(+975) 02 332862, enquiry@thepema.gov.bt\n"
    "You are not a burden. ❤️"
]



def contains_crisis_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)

def get_safety_message() -> str:
    return random.choice(SAFETY_MESSAGES)