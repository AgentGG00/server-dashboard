import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from supabase import create_client, Client  # noqa: E402
from services.supabase_service import SupabaseService  # noqa: E402
from routers.auth import router as auth_router  # noqa: E402
from routers.settings import router as settings_router  # noqa: E402
from middleware.device_check import DeviceCheckMiddleware  # noqa: E402

app = FastAPI(title="server-dashboard")
app.include_router(settings_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DeviceCheckMiddleware)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL oder SUPABASE_SERVICE_ROLE_KEY nicht gesetzt")

supabase: Client = create_client(supabase_url, supabase_key)
supabase_service = SupabaseService(supabase)
app.state.supabase = supabase

app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
