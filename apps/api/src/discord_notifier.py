"""
Discord通知ヘルパー

絵日記生成完了時にDiscord Webhookへ通知を送信します。
Webhook URL はユーザーがフロントエンドで設定し、リクエスト経由で渡されます。
"""

import os
import httpx


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_discord_notification_sync(
    webhook_url: str,
    title: str,
    diary_text: str,
    diary_id: str | None = None,
    image_url: str | None = None,
    keywords: list[str] | None = None,
) -> bool:
    """
    Discord Webhookに絵日記完了通知を送信

    Args:
        webhook_url: Discord Webhook URL
        title: 日記のタイトル（日付など）
        diary_text: 日記本文
        diary_id: FirestoreドキュメントID（URLリンク用）
        image_url: 生成された画像のURL（オプション）
        keywords: 抽出されたキーワード（オプション）

    Returns:
        送信成功したかどうか
    """
    if not webhook_url:
        print("Discord Webhook URL is not provided, skipping notification")
        return False

    # 日記ページのURL
    diary_url = f"{FRONTEND_URL}/diaries/{diary_id}" if diary_id else None

    # Embed形式でリッチな表示
    embed = {
        "title": f"📔 {title}",
        "description": diary_text,
        "color": 0xFFB347,  # オレンジ色
    }

    # URLがあればリンクを追加
    if diary_url:
        embed["url"] = diary_url

    # キーワードがあれば追加
    if keywords:
        embed["fields"] = [
            {
                "name": "🏷️ キーワード",
                "value": " / ".join(keywords),
                "inline": False,
            }
        ]

    # 画像があれば追加
    if image_url:
        embed["image"] = {"url": image_url}

    payload = {
        "embeds": [embed],
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                webhook_url,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            print(f"Discord notification sent successfully")
            return True
    except httpx.HTTPError as e:
        print(f"Failed to send Discord notification: {e}")
        return False
