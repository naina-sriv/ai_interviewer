import uuid
from models.interview import Answer, InterviewSession, InteriewStatusEnum
from store.session_store import session_store


def create_session() -> InterviewSession:
    session_id = str(uuid.uuid4())

    interview_session = InterviewSession(
        session_id=session_id
    )

    session_store.save_session(interview_session)
    return interview_session

def get_session(session_id: str) -> InterviewSession:
    return session_store.get_session(session_id)


def save_answer(answer: str | None, skip: bool, session: InterviewSession):
    question = session.questions[session.current_index]

    session.answers.append(
        Answer(
            question= question,
            answer= None if skip else answer,
            skip=skip
        )
    )

    session.current_index += 1

    if session.current_index == len(session.questions):
        session.status = InteriewStatusEnum.COMPLETED

    # Crucial: Push the mutated session back to the store!
    session_store.save_session(session)