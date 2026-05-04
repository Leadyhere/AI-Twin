import os
import json
import time
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

try:
    from .ingestion_utils import get_embedding
except ImportError:
    from ingestion_utils import get_embedding

load_dotenv()

# --- 1. INITIALIZE THE BRAIN ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
PERSON_NAME = os.getenv("PERSON_NAME", "").strip()

# --- 2. INITIALIZE THE MEMORY ---
db_path = "chroma_db" 
print(f"🗄️ Connecting to ChromaDB at: {db_path}")

chroma_client = chromadb.PersistentClient(path=db_path)

# Connect to the exact collection name you created earlier
try:
    collection = chroma_client.get_collection(name="person_memory")
    print("✅ Successfully connected to user memory!")
except Exception as e:
    print("⚠️ WARNING: Could not find memory collection.")
    collection = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat/completions")
async def vapi_chat_endpoint(request: Request):
    payload = await request.json()
    messages = payload.get("messages", [])
    is_stream = payload.get("stream", False) # Vapi usually sets this to True
    
    # Extract the user's latest message
    user_message = ""
    if messages:
        user_message = messages[-1].get("content", "")
    
    print(f"\n📞 Judge said: {user_message}")
    
    try:
        # --- 3. RETRIEVE MEMORIES ---
        retrieved_context = ""
        if collection:
            query_embedding = get_embedding(
                user_message,
                task_type="RETRIEVAL_QUERY"
            )
            query_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": 2
            }

            if PERSON_NAME:
                query_kwargs["where"] = {"person_name": PERSON_NAME}

            results = collection.query(
                **query_kwargs
            )
            if results and results['documents'] and results['documents'][0]:
                retrieved_context = "\n".join(results['documents'][0])
                print(f"🧠 Retrieved Memory: {retrieved_context}")
        
        # --- 4. GENERATE THE REPLY ---
        prompt = f"""
        You are my digital twin, presenting our project at a 24-hour hackathon. 
        Keep your answer conversational, punchy, and short (under 2 sentences). Do not use emojis or hashtags.
        
        Database Context:
        {retrieved_context}
        
        Judge asks: "{user_message}"
        
        Respond naturally as me:
        """
        
        response = model.generate_content(prompt)
        ai_reply = response.text.strip()
        
    except Exception as e:
        print(f"❌ Error thinking: {e}")
        ai_reply = "I'm processing that in my vector database, give me one second."

    print(f"🤖 Clone replied: {ai_reply}")

    # --- 5. THE FIX: SEND BACK A FAKE STREAM ---
    if is_stream:
        async def generate_stream():
            # Chunk 1: The actual text
            chunk = {
                "id": "chatcmpl-hackathon",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "hackathon-model",
                "choices": [{"index": 0, "delta": {"role": "assistant", "content": ai_reply}, "finish_reason": None}]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            
            # Chunk 2: The stop signal telling Vapi it can start talking
            end_chunk = {
                "id": "chatcmpl-hackathon",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "hackathon-model",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(end_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    
    # Fallback if Vapi doesn't request a stream
    else:
        vapi_response = {
            "id": "chatcmpl-hackathon",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "hackathon-model",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": ai_reply}, "finish_reason": "stop"}]
        }
        return JSONResponse(content=vapi_response)
