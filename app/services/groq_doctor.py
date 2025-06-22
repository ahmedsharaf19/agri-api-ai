import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Get API key with fallback
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("Warning: GROQ_API_KEY not found in environment variables")
    groq_api_key = "dummy_key"  # Fallback to prevent crashes

# Initialize model with error handling
try:
    model = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)
except Exception as e:
    print(f"Error initializing ChatGroq model: {e}")
    model = None

# Initialize prompt and chain if model is available
if model:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "أنت طبيب زراعي خبير. أعطني علاجًا مفصلًا لهذه الأمراض: {diseases}"),
        ("user", "{diseases}")
    ])
    parser = StrOutputParser()
    chain = prompt | model | parser
else:
    chain = None

async def get_treatment_text(diseases: str):
    try:
        # Check if model and chain are available
        if model is None or chain is None:
            return "خدمة العلاج غير متاحة حالياً. يرجى التحقق من إعدادات API."

        result = await chain.ainvoke({"diseases": diseases})
        return result
    except Exception as e:
        print(f"Error getting treatment: {e}")
        return f"حدث خطأ في الحصول على العلاج: {str(e)}"
