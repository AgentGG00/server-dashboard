from typing import Any
from supabase import Client
from services.encryption import encrypt, decrypt, hash_api_key, hash_password, verify_password


class SupabaseService:
    def __init__(self, client: Client):
        self.db = client

    async def create_server(self, name: str, ip: str, api_key: str) -> dict:
        data = {
            "name": encrypt(name),
            "ip": encrypt(ip),
            "api_key_hash": hash_api_key(api_key),
        }
        result = self.db.table("servers").insert(data).execute()
        row: Any = result.data[0]
        return dict(row)

    async def get_servers(self) -> list:
        result = self.db.table("servers").select("*").execute()
        servers = []
        for item in result.data:
            row: Any = item
            servers.append({
                "id": row["id"],
                "name": decrypt(str(row["name"])),
                "ip": decrypt(str(row["ip"])),
                "last_seen": row["last_seen"],
                "created_at": row["created_at"],
            })
        return servers

    async def verify_server_api_key(self, api_key: str) -> dict | None:
        key_hash = hash_api_key(api_key)
        result = self.db.table("servers").select("*").eq("api_key_hash", key_hash).execute()
        if not result.data:
            return None
        row: Any = result.data[0]
        return dict(row)

    async def create_session(self, token: str, expires_at: str) -> dict:
        data = {
            "token": encrypt(token),
            "expires_at": expires_at,
        }
        result = self.db.table("sessions").insert(data).execute()
        row: Any = result.data[0]
        return dict(row)

    async def get_session(self, token: str) -> dict | None:
        result = self.db.table("sessions").select("*").execute()
        for item in result.data:
            row: Any = item
            if decrypt(str(row["token"])) == token:
                return dict(row)
        return None

    async def delete_session(self, token: str) -> None:
        session = await self.get_session(token)
        if session:
            self.db.table("sessions").delete().eq("id", session["id"]).execute()

    async def set_totp_secret(self, secret: str) -> dict:
        self.db.table("totp_secrets").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        data = {"secret": encrypt(secret)}
        result = self.db.table("totp_secrets").insert(data).execute()
        row: Any = result.data[0]
        return dict(row)

    async def get_totp_secret(self) -> str | None:
        result = self.db.table("totp_secrets").select("*").limit(1).execute()
        if not result.data:
            return None
        row: Any = result.data[0]
        return decrypt(str(row["secret"]))

    async def set_admin_password(self, password: str) -> dict:
        self.db.table("admin_credentials").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        data = {"password_hash": hash_password(password)}
        result = self.db.table("admin_credentials").insert(data).execute()
        row: Any = result.data[0]
        return dict(row)

    async def verify_admin_password(self, password: str) -> bool:
        result = self.db.table("admin_credentials").select("*").limit(1).execute()
        if not result.data:
            return False
        row: Any = result.data[0]
        return verify_password(password, str(row["password_hash"]))