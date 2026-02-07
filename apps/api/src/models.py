"""Pydantic モデル定義"""

from pydantic import BaseModel


class ConversationLogRequest(BaseModel):
    """会話ログ（要約データ）のリクエストモデル"""

    date: str | None = None
    location: str | None = None
    activity: str | None = None
    feeling: str | None = None
    conversation_transcript: str  # 会話の全文（JSON形式）


class DiaryResponse(BaseModel):
    """絵日記作成のレスポンスモデル"""

    id: str
    status: str
