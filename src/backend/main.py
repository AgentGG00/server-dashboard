from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from services.supabase_service import SupabaseService
import os

app = FastAPI(title="server-dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL oder SUPABASE_SERVICE_ROLE_KEY nicht gesetzt")

supabase: Client = create_client(supabase_url, supabase_key)

supabase_service = SupabaseService(supabase)

@app.get("/health")
async def health():
    return {"status": "ok"}