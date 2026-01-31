from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class ConversationLogRequest(BaseModel):
    """
    日記生成のための会話ログリクエスト
    Multimodal Live API の `report_diary_event` ツールの引数をそのまま受け取る想定
    """

    date: str = Field(..., description="出来事の日付 (例: 2024-01-01)")
    location: Optional[str] = Field(None, description="場所")
    activity: str = Field(..., description="何をしたか")
    feeling: str = Field(..., description="感想")
    summary: str = Field(..., description="会話の要約（絵日記の本文用）")

    # 大人向けジョークのヒント
    joke_hint: Optional[str] = Field(
        None, description="大人向けジョークのヒント（起床時間、歩数、食べた量など）"
    )

    # 拡張用: 将来的に生の会話履歴などを含める場合
    raw_logs: Optional[List[Dict[str, Any]]] = Field(
        None, description="生の会話ログ（オプション）"
    )


class DiaryResponse(BaseModel):
    id: str = Field(..., description="生成された日記データのID (Firestore Document ID)")
    status: str = Field(
        ..., description="処理ステータス (pending, processing, completed)"
    )
