# Pratirupa / Incarnation

Pratirupa is a digital-clone prototype that combines persona memory retrieval, Gemini-generated replies, Gmail automation, and a Simli avatar demo.

The project is organized around one idea: ingest a person's communication style and reference material into ChromaDB, retrieve the most relevant memories for a new message, and generate a reply that sounds like that person.

## What This Project Includes

- `Mohini/app.py`: Streamlit tool to upload persona documents, chunk them, embed them with Gemini embeddings, and store them in ChromaDB.
- `Mohini/brain_api.py`: FastAPI service that retrieves relevant memories and generates a structured clone reply.
- `Mohini/gmail_listener.py`: Gmail polling script that sends unread emails to the brain API and auto-replies only when confidence is high.
- `Mohini/vapi_server.py`: FastAPI endpoint shaped like a chat-completions API for voice/avatar integrations.
- `Mohini/voice_ui.py`: Streamlit-based voice control UI for Vapi.
- `Mohini/create-simli-agent/`: Next.js demo client for testing the avatar interaction flow with Simli and Daily.
- `data/chroma_db/` and `Mohini/chroma_db/`: local persistent vector database files.

## High-Level Flow

1. Upload persona material such as emails, blogs, WhatsApp exports, PDFs, CSVs, or DOCX files.
2. The ingester cleans text, chunks it, generates embeddings with Gemini, and stores it in ChromaDB.
3. A new incoming email or prompt is sent to the clone brain.
4. The brain retrieves the most relevant memory snippets for that person.
5. Gemini generates a draft reply in that person's style.
6. If confidence is high enough, the Gmail listener can send the reply automatically; otherwise it stays pending.

## Project Structure

```text
pratirupa/
├─ README.md
├─ data/
│  └─ chroma_db/
├─ Mohini/
│  ├─ app.py
│  ├─ brain_api.py
│  ├─ gmail_listener.py
│  ├─ ingestion_utils.py
│  ├─ requirements.txt
│  ├─ vapi_server.py
│  ├─ voice_ui.py
│  └─ create-simli-agent/
│     ├─ app/
│     ├─ public/
│     ├─ media/
│     └─ package.json
└─ Solution Challenge 2026 - Incarnation.pdf
```

## Requirements

- Python 3.10+
- Node.js 18+
- A Google AI Studio API key with access to Gemini models
- A Gmail account with a Google App Password if you want email automation
- Simli and Daily credentials if you want the avatar demo

## Python Setup

From the repository root:

```powershell
cd Mohini
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `Mohini/.env` with at least:

```env
GOOGLE_API_KEY=your_google_api_key
GENERATION_MODEL=gemini-2.5-flash
PERSON_NAME=Your Name
```

For Gmail automation, also add:

```env
GMAIL_EMAIL=yourname@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
BRAIN_API_URL=http://127.0.0.1:8000/clone/process
```

## Load Persona Memory

Run the Streamlit uploader:

```powershell
cd Mohini
streamlit run app.py
```

In the UI you can:

- enter the person's name
- upload `txt`, `csv`, `pdf`, or `docx` files
- store persona Q&A answers
- test retrieval from the stored memory

The ingested chunks are stored in the `person_memory` Chroma collection.

## Run The Brain API

Start the clone reply service:

```powershell
cd Mohini
uvicorn brain_api:app --reload
```

This exposes:

- `POST /clone/process`

Example request:

```json
{
  "person_name": "Suyash",
  "sender_name": "Alice",
  "message_text": "Subject: Project update\n\nBody: Can you send the final deck by tonight?"
}
```

Example response shape:

```json
{
  "original_sender": "Alice",
  "original_message": "Subject: Project update\n\nBody: Can you send the final deck by tonight?",
  "clone_draft": "Thanks for the note. I'll send the final deck by tonight.",
  "confidence_score": 92,
  "reasoning": "The reply matches the user's concise professional tone.",
  "status": "auto_sent"
}
```

## Run Gmail Automation

Once the brain API is running and your Gmail credentials are configured:

```powershell
cd Mohini
python gmail_listener.py
```

Behavior:

- polls Gmail for unread emails every 90 seconds
- sends each email to the brain API
- auto-sends a reply only when `confidence_score >= 90`
- leaves lower-confidence drafts pending for manual review

Important:

- use a Gmail App Password, not your regular Gmail password
- enable 2-Step Verification on the Gmail account first

## Run The Voice/Avatar Backend

For the Vapi-style chat endpoint:

```powershell
cd Mohini
uvicorn vapi_server:app --reload
```

This exposes:

- `POST /chat/completions`

The endpoint supports both normal JSON responses and a simple event-stream response when `stream: true` is sent.

## Optional Streamlit Voice UI

You can also run the Streamlit voice console:

```powershell
cd Mohini
streamlit run voice_ui.py
```

Note:

- `voice_ui.py` currently contains blank `PUBLIC_KEY` and `ASSISTANT_ID` placeholders in the embedded JavaScript
- it will need those values filled in before the UI can start calls successfully

## Simli Frontend Demo

The avatar test client lives in `Mohini/create-simli-agent`.

Install and run it:

```powershell
cd Mohini\create-simli-agent
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

The UI lets you:

- enter Simli API settings
- set the clone API URL
- send a test prompt
- join a Daily room and render the avatar feed

Recommended `.env` values for the Next.js app:

```env
NEXT_PUBLIC_SIMLI_API_KEY=your_simli_api_key
NEXT_PUBLIC_SIMLI_FACE_ID=your_face_id
NEXT_PUBLIC_SIMLI_VOICE_ID=your_voice_id
NEXT_PUBLIC_SIMLI_ROOM_URL=your_daily_room_url
NEXT_PUBLIC_CLONE_API_URL=http://127.0.0.1:8000/chat/completions
```

## API And Data Notes

- Embeddings are generated with `models/gemini-embedding-001`.
- Reply generation defaults to `gemini-2.5-flash` unless `GENERATION_MODEL` overrides it.
- Chroma uses a persistent local folder, so data survives restarts.
- Persona data is filtered by `person_name` during retrieval.

## Known Caveats

- There are two Chroma database locations in the repo; keep your services pointed at the same one if you want shared memory.
- `voice_ui.py` is not ready out of the box because the Vapi keys are still placeholders.
- The Simli demo stores config in browser local storage and is mainly a test console, not a production UI.
- `vapi_server.py` is tuned for short hackathon-style spoken answers rather than long-form email drafting.

## Suggested Local Run Order

1. Create `Mohini/.env`.
2. Install Python dependencies.
3. Run `streamlit run app.py` and ingest persona data.
4. Run `uvicorn brain_api:app --reload`.
5. Optionally run `python gmail_listener.py`.
6. Optionally run `uvicorn vapi_server:app --reload`.
7. Optionally run the Next.js client in `Mohini/create-simli-agent`.

## Future Improvements

- unify all services around one ChromaDB path
- add authentication and approval workflow for pending drafts
- persist generated drafts to a database
- improve confidence scoring beyond model self-reporting
- add tests for ingestion, retrieval, and API parsing
- move secrets and runtime configuration into documented env templates

## License

No explicit license is currently defined in the root project.
# Incarnation
# Incarnation
