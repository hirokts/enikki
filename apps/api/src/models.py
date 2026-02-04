"""Pydantic モデル定義"""

from pydantic import BaseModel


class ConversationLogRequest(BaseModel):
    """会話ログ（要約データ）のリクエストモデル"""

    date: str
    location: str
    activity: str
    feeling: str
    summary: str
    joke_hint: str | None = None


class DiaryResponse(BaseModel):
    """絵日記作成のレスポンスモデル"""

    id: str
    status: str
