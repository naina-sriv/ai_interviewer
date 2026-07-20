from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from models.interview import InteriewStatusEnum
from request_model.AnswerRequest import AnswerRequest
from response_model.AnswerResponse import AnswerResponse
from services.ai_service import create_interview_context, evaluate_interview_answers, generate_followup
from services.interview_service import create_session, get_session, save_answer
from util.file_util import extract_text, validate_file

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)

@router.post("/generate-question")
async def init_interview_context(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    # Validate resume file
    await validate_file(resume)

    # Extract text from resume
    resume_text = await extract_text(resume)

    # Generate questions and intro text using title, decription, resume content
    context_data = await create_interview_context(job_title=job_title, job_description=job_description, resume_text=resume_text)

    session = create_session()
    session.questions = context_data.get("questions")
    session.introText = context_data.get("introText")

    return { "session_id": session.session_id }



@router.get("/start/{session_id}")
async def start_interview(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")

    return {
        "introText": session.introText,
        "firstQuestion": session.questions[0]
    }


@router.post("/submit")
async def submit_answer(answerReq: AnswerRequest):
    # Check valid session_id
    session = get_session(answerReq.session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")

    # The question the candidate just answered
    current_question = session.questions[session.current_index]

    # save answer in interview session
    save_answer(answerReq.answer, answerReq.skip, session)

    # If all main questions are done after saving, end the interview
    if session.status == InteriewStatusEnum.COMPLETED:
        return {
            "interviewEnded": True,
            "responseText": "Thank you so much for your time! That wraps up our interview. Let me prepare your report."
        }

    # Get remaining questions for context
    remaining_questions = session.questions[session.current_index:]

    # Generate a conversational follow-up using AI
    followup_data = await generate_followup(
        question=current_question,
        answer=answerReq.answer or "",
        remaining_questions=remaining_questions,
        was_skipped=answerReq.skip
    )

    response_text = followup_data.get("response_text", "")
    followup_question = followup_data.get("followup_question")
    move_to_next = followup_data.get("move_to_next", True)

    # If AI wants a follow-up and we haven't hit the limit (1 follow-up per main question)
    if followup_question and not move_to_next and session.followup_count < 1:
        session.followup_count += 1
        # Don't advance current_index — we're still on the same main question
        # But we need to undo the index advance that save_answer did
        session.current_index -= 1
        session.status = InteriewStatusEnum.IN_PROGRESS
        from store.session_store import session_store
        session_store.save_session(session)

        return {
            "interviewEnded": False,
            "responseText": response_text,
            "nextQuestion": followup_question
        }
    else:
        # Moving to next main question — reset followup count
        session.followup_count = 0
        from store.session_store import session_store
        session_store.save_session(session)

        next_question = session.questions[session.current_index]
        return {
            "interviewEnded": False,
            "responseText": response_text,
            "nextQuestion": next_question
        }

@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    session.status = InteriewStatusEnum.COMPLETED

    return {
            "interviewEnded": True
    }

@router.get("/report/{session_id}")
async def get_interview_report(session_id: str):
    # Check valid session_id
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    evaluation_data = await evaluate_interview_answers(answers=session.answers)

    return { "result":  evaluation_data }
