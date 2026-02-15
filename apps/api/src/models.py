"""Pydantic モデル定義"""

from pydantic import BaseModel


class TranscriptEntry(BaseModel):
    """会話 transcript の1エントリ"""

    role: str  # 'user' or 'model'
    text: str
    timestamp: int  # Unix ms


class ConversationLogRequest(BaseModel):
    """会話ログ（date + transcript）のリクエストモデル"""

    date: str  # ブラウザから取得した日付 (例: 2024-01-01)
    transcript: list[TranscriptEntry]
    discordWebhookUrl: str | None = None  # ユーザーが設定した Discord Webhook URL


class DiaryResponse(BaseModel):
    """絵日記作成のレスポンスモデル"""

    id: str
    status: str
