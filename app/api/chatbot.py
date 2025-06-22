from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from fastapi import Body
from app.services.chat_service import chat_chain
import uuid

router = APIRouter()

@router.post("/chatbot")
async def chatbot_api(
    request: Request,
    user_input: str = Form(None),
    body: dict = Body(None)
):
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))

    # دعم كل من Form و JSON
    if body and "user_input" in body:
        user_input = body["user_input"]

    if not user_input:
        return JSONResponse(content={"error": "user_input is required."}, status_code=422)

    try:
        # Check if chat_chain is available
        if chat_chain is None:
            return JSONResponse(content={
                "response": "خدمة المساعد الزراعي غير متاحة حالياً. يرجى التحقق من إعدادات API.",
                "session_id": session_id
            })

        response = await chat_chain.ainvoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        return JSONResponse(content={"response": response, "session_id": session_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
