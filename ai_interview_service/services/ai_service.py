import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def call_gemini_api(system_prompt: str, prompt: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY environment variable is not set")
        
    genai.configure(api_key=api_key)
    
    # Use gemini-1.5-flash, or fallback to gemini-pro if needed
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Failed to parse Gemini response or API error: {e}")
        
        # Fallback to gemini-pro if 1.5-flash is not available for this key
        try:
            print("Falling back to gemini-pro model...")
            fallback_model = genai.GenerativeModel('gemini-pro')
            combined_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}\n\nPlease respond in valid JSON format."
            response = fallback_model.generate_content(combined_prompt)
            # Try to strip markdown JSON blocks if present
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            return json.loads(clean_text.strip())
        except Exception as fallback_e:
            raise Exception(f"Failed to call Gemini API: {e} | Fallback error: {fallback_e}")

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
    
    return await call_gemini_api(SYSTEM_PROMPT, "Generate JSON output based on system instruction.")


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
    
    return await call_gemini_api(SYSTEM_PROMPT, "Generate JSON output based on system instruction.")
