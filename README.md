# YouTube RAG

Chat with any YouTube video using AI. Upload a video URL, extract its transcript, and ask questions using Retrieval-Augmented Generation (RAG).

## Features

- **YouTube Transcript Processing** — Paste any YouTube URL to fetch and process its transcript
- **RAG-powered Chat** — Ask questions about video content and get AI-generated answers with source context
- **User Authentication** — Secure JWT-based registration and login
- **Chat Management** — Create, view, and delete chat sessions per video
- **Video Library** — Manage processed videos with status tracking (processing, ready, failed)
- **Real-time Status** — Track video processing progress

## Tech Stack

### Frontend
- **Next.js 16** (App Router)
- **React 19**
- **TypeScript**
- **Tailwind CSS v4**
- **Zustand** — State management
- **Lucide React** — Icons
- **Sonner** — Toast notifications
- **React Markdown** — Markdown rendering

### Backend
- **FastAPI** — Async web framework
- **SQLAlchemy 2.0** — Async ORM
- **Alembic** — Database migrations
- **PostgreSQL** (asyncpg) — Relational database
- **LangChain** — LLM orchestration
- **Groq** — LLM provider (LLaMA 3.1 8B)
- **Pinecone** — Vector database for embeddings
- **Sentence Transformers** — Embedding model (all-MiniLM-L6-v2)
- **youtube-transcript-api** — Transcript extraction

## Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL
- Pinecone account
- Groq API key

## Project Structure

```
youtube-rag/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── chat.py
│   │   │       ├── rag.py
│   │   │       └── youtube.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   ├── logger.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   └── schemas/      # Pydantic schemas
│   │   ├── prompts/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    ├── app/                  # Next.js App Router pages
    ├── components/
    ├── lib/
    ├── services/
    ├── store/
    ├── types/
    └── package.json
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/youtube-rag.git
cd youtube-rag
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/youtube_rag
DIRECT_URL=postgresql://user:password@localhost:5432/youtube_rag
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=youtube-rag
SECRET_KEY=your_jwt_secret_key
DEBUG=True
```

Run database migrations:

```bash
alembic upgrade head
```

Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

The frontend `.env` is already configured:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend development server:

```bash
npm run dev
```

### 4. Open the App

Visit [http://localhost:3000](http://localhost:3000) in your browser.

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| POST | `/api/auth/refresh` | Refresh access token |

### YouTube
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/youtube/process` | Process a YouTube video |
| GET | `/api/youtube/videos` | List user's videos |
| GET | `/api/youtube/videos/{id}` | Get video details |
| DELETE | `/api/youtube/videos/{id}` | Delete a video |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/create` | Create a new chat |
| GET | `/api/chat/list` | List user's chats |
| GET | `/api/chat/{id}/messages` | Get chat history |
| DELETE | `/api/chat/{id}` | Delete a chat |

### RAG
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rag/ask` | Ask a question about a video |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## Environment Variables

### Backend (`.env`)
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL async connection string | Yes |
| `DIRECT_URL` | PostgreSQL direct connection (for Alembic) | Yes |
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | No (default: `youtube-rag`) |
| `SECRET_KEY` | JWT signing secret | Yes |
| `ALGORITHM` | JWT algorithm | No (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | No (default: `30`) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | No (default: `7`) |
| `CHUNK_SIZE` | Transcript chunk size | No (default: `800`) |
| `CHUNK_OVERLAP` | Chunk overlap | No (default: `200`) |
| `RETRIEVAL_TOP_K` | Top-k chunks for retrieval | No (default: `4`) |
| `EMBEDDING_MODEL` | HuggingFace embedding model | No (default: `sentence-transformers/all-MiniLM-L6-v2`) |
| `LLM_MODEL` | Groq LLM model | No (default: `llama-3.1-8b-instant`) |
| `DEBUG` | Enable debug mode | No (default: `False`) |

### Frontend (`.env`)
| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## How It Works

1. **User authenticates** via JWT-based login/register
2. **User pastes a YouTube URL** — backend fetches the transcript using `youtube-transcript-api`
3. **Transcript is chunked** using LangChain text splitters (800 chars, 200 overlap)
4. **Chunks are embedded** using Sentence Transformers and stored in Pinecone
5. **User asks questions** — relevant chunks are retrieved from Pinecone
6. **LLM generates answer** using Groq (LLaMA 3.1 8B) with retrieved context

## License

MIT
