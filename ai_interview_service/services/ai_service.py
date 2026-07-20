import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def call_ai_api(system_prompt: str, prompt: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY environment variable is not set")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=60.0)

        if response.status_code != 200:
            print(f"Groq API Error: {response.status_code} - {response.text}")
            raise Exception(f"Failed to call Groq API: {response.status_code} - {response.text}")

        data = response.json()

        try:
            text_response = data['choices'][0]['message']['content']
            return json.loads(text_response.strip())
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Failed to parse Groq response: {e}")
            raise Exception("Invalid response format from Groq")



async def create_interview_context(job_title: str, job_description: str, resume_text: str):
    SYSTEM_PROMPT = f"""
        You are an AI interview expert, who generates questions based on candidate's job_title, job_description, resume_text.
        You need to find out candidate's name, you need to generate an introduction text including candidate's name, you need to generate questions
        based on job_description, job_title, user's skills, years of experience from resume_text.

        Input:
            job_title: {job_title},
            job_description: {job_description},
            resume_text: {resume_text}

        Output:
            questions: array,
            introText: string,
            candidate_name: string

        Rules:
            - For Questions:
                a) Generate 2-3 questions.
                b) Consider years of experince to label of difficulty of interview questions.
                c) Questions should be easy to hard manner.
                d) Questions related to only Skills metioned in resume, job_description and job_title
                e) Questions are needs to be small and to the point and some time scenario based.
            - For Introduction Text:
                a) It's simple text introduction which is going to played on brower before starting the interview
                b) Include candidate name, job title in the text.
                c) Add your own creativity
            - For Candidate Name:
                a) Extract candidate name from resume, if candidate not found then consider candidate name as "Candidate".

            - Output:
                Output needs to be in json format and it should have questions, introText, candidate_name

        Example 1:
        Input:
            job_title: Senior Java Developer
            job_description: Candidate should have experinece on core java, spring boot, spring security etc......
            resume_text: Name- John Doe, ..., Skills: Java, Spring, Node JS, React Js, ....
        
        Output:
            questions: ["What is java?", "What is the difference between List and Set", ...]
            introText: "Hi John Doe, This is your mock interview for Senior Java Developer."
            candidate_name: John Doe
    """
    
    return await call_ai_api(SYSTEM_PROMPT, "Generate JSON output based on system instruction.")


async def evaluate_interview_answers(answers: list):
    # Convert list of pydantic models to dict if necessary, or let json handle it. 
    # answers is a list of Answer objects.
    answers_data = [a.model_dump() if hasattr(a, 'model_dump') else a for a in answers]
    
    SYSTEM_PROMPT = f"""
        You are an expert AI interviewer, who analyse the answers based on questions, and share the feedbacks.
        You need to find out Score in percentage, Total Correct Answers and details areas of improvment based (not more then 5 points).

        Input: {json.dumps(answers_data)}

        Input Structure:
        answers is an array. which will have objects. 
        - array[]
            - object
                - question: string = it'll contain question in string.
                - answer: string | None = if skip is true then answer will be None else answer will have string.
                - skip: bool = if user gives answer then skip = False else skip = True

        Output Structure:
        I need output in JSON format. and it'll contain below object
        - Object
            - score: string = It should calculate percentage from correct (answer / total question) % 100
            - correct_answer: number = number of correct answer
            - improvment_area: array of string = it'll contain area of improvment areas. not more then 5 points.

        Rule:
         - Don't be so strict to evaluate the answer.
         - Consider the answer is correct if candidate at least answered 70%. But provide the feedback
         - If candidate didn't answer anything then mark score 0%, correct_answer 0 and improvment_area as it is provide.
    """
    
    return await call_ai_api(SYSTEM_PROMPT, "Generate JSON output based on system instruction.")
