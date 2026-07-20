COMPANY_QUESTIONS = {
    "google": [
        "How would you design a scalable system like YouTube?",
        "Explain the time and space complexity of your approach.",
        "How do you handle distributed transactions across multiple microservices?",
        "Describe a time you had to optimize a slow-performing system.",
        "How would you implement a rate limiter?"
    ],
    "amazon": [
        "Tell me about a time you had to dive deep into a problem to find the root cause.",
        "How would you design Amazon's shopping cart system?",
        "Describe a situation where you had to disagree and commit.",
        "How do you ensure high availability in a distributed system?",
        "Explain how you would handle thousands of concurrent orders during Prime Day."
    ],
    "meta": [
        "How would you design the news feed for Facebook?",
        "Explain how you would scale a real-time chat application.",
        "How do you handle data consistency across data centers?",
        "Describe a time you moved fast and broke things, and how you recovered.",
        "How would you optimize the loading speed of a web application with heavy images?"
    ],
    "microsoft": [
        "How would you design an online collaborative document editor like Office 365?",
        "Explain the principles of SOLID design.",
        "How do you approach debugging a memory leak in a large codebase?",
        "Describe a time you had to work with a difficult team member.",
        "How would you implement a thread-safe singleton pattern?"
    ],
    "apple": [
        "How would you design an API that millions of iOS devices will call simultaneously?",
        "Explain how you would ensure user data privacy in your architecture.",
        "Describe a time you had to pay extreme attention to detail.",
        "How do you handle battery optimization in background processes?",
        "How would you design the backend for a secure messaging app?"
    ],
    "netflix": [
        "How would you design a global video streaming service?",
        "Explain chaos engineering and how you would test system resilience.",
        "How do you handle eventual consistency in a microservices architecture?",
        "Describe a time you had to take a calculated risk.",
        "How would you implement a personalized recommendation engine?"
    ]
}

def get_company_questions(company_name: str) -> list[str]:
    """Retrieve commonly asked questions for a specific company."""
    if not company_name:
        return []
    
    # Normalize company name to lowercase and strip whitespace
    normalized_name = company_name.lower().strip()
    
    # Look for partial matches (e.g., "amazon inc" -> matches "amazon")
    for key, questions in COMPANY_QUESTIONS.items():
        if key in normalized_name:
            return questions
            
    return []
