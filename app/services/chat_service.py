from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

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

# 👇 استخدم prompt بمتغيرات متوافقة
prompt = ChatPromptTemplate.from_messages([
    ("system", "أنت مساعد زراعي خبير. أجب باحتراف وباللغة العربية."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# مؤقتًا نخزن المحادثات هنا (ممكن تحويله ل Redis أو DB لاحقًا)
chat_memory_store = {}

# runnable history chain - only create if model is available
chat_chain = None
if model is not None:
    chat_chain = RunnableWithMessageHistory(
        prompt | model | StrOutputParser(),
        lambda session_id: chat_memory_store.setdefault(session_id, ChatMessageHistory()),
        input_messages_key="input",
        history_messages_key="history",
    )
