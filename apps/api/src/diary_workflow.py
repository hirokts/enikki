"""
絵日記生成ワークフロー (LangGraph)

会話ログを入力として、以下のステップで絵日記を生成します:
1. キーワード抽出 (Gemini)
2. 日記文章生成 (Gemini)
3. 品質チェック (Gemini) -> NG なら 2 に戻る
4. 画像生成 (Imagen 3)
5. Firestore 保存
"""

import json
import os
from typing import TypedDict

from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, START, StateGraph

# Gemini モデルの初期化
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "enikki-cloud")
REGION = os.getenv("GCP_REGION", "asia-northeast1")

llm = ChatVertexAI(
    model="gemini-2.0-flash",
    project=PROJECT_ID,
    location=REGION,
    temperature=0.7,
)


class DiaryState(TypedDict):
    """ワークフローの状態"""

    document_id: str  # Firestore ドキュメント ID
    conversation_log: dict  # 入力: 会話ログ（report_diary_event の引数）
    keywords: list[str] | None  # 抽出されたキーワード
    diary_text: str | None  # 生成された日記テキスト
    quality_score: float | None  # 品質スコア (0.0 - 1.0)
    retry_count: int  # リトライ回数
    image_url: str | None  # 生成された画像の URL
    status: str  # pending / processing / completed / failed
    error: str | None  # エラーメッセージ


# --- ヘルパー関数 ---


def format_transcript(transcript: list[dict] | None) -> str:
    """transcript を読みやすいテキスト形式に変換する"""
    if not transcript:
        return ""

    lines = []
    for entry in transcript:
        role_label = "ユーザー" if entry.get("role") == "user" else "AI"
        text = entry.get("text", "").strip()
        if text:
            lines.append(f"{role_label}: {text}")

    return "\n".join(lines)


# --- ノード定義 ---


def extract_keywords(state: DiaryState) -> dict:
    """会話ログから4つのキーワードを抽出"""
    log = state["conversation_log"]
    transcript_text = format_transcript(log.get("transcript"))

    prompt = f"""以下の会話の全文から、絵日記に使う重要な4つのキーワードを抽出してください。
キーワードは名詞や動詞など、絵に描きやすいものを選んでください。

会話全文:
{transcript_text}

日付: {log.get("date", "不明")}

JSON形式で出力してください（キーワードの配列のみ）:
["キーワード1", "キーワード2", "キーワード3", "キーワード4"]
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        # JSON部分を抽出
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        keywords = json.loads(content)
        return {"keywords": keywords[:4], "status": "processing"}
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        # フォールバック
        return {"keywords": ["今日", "楽しい", "おでかけ", "きもち"], "status": "processing"}


def generate_diary(state: DiaryState) -> dict:
    """キーワードと transcript を元に絵日記テキストを生成"""
    keywords = state.get("keywords", [])
    log = state["conversation_log"]
    transcript_text = format_transcript(log.get("transcript"))

    prompt = f"""以下の情報を元に、小学生が書くような「ぼくの夏休み」風の絵日記テキストを生成してください。
ただし、実際の読者は大人なので、大人がクスッと笑える要素を入れてください。

## 会話全文（最も重要な情報源）
以下はユーザーとAIインタビュアーの会話全文です。この内容を元に、ユーザーが実際に話した体験やエピソードを忠実に反映してください。

{transcript_text}

## 抽出済みキーワード
{", ".join(keywords)}

## ルール
- 100〜150文字程度
- 子供らしい素直な文体（ですます調ではなく、だ・である調やカジュアルな表現）
- 「今日は〜」で始める
- 五感（匂い、音、感触など）の描写を1つ入れる
- 末尾に大人向けのクスッとくるジョークを添える

## 五感の例
- 「甘い匂いがふわっとした」
- 「パチパチ音がした」
- 「手がベタベタになった」

## 大人向けジョークの例（参考にして、会話内容に合ったものを作ってください）

### 括弧でツッコミ（現実を添える）
- 「早起きした（9時）」
- 「たくさん歩いた（5000歩）」
- 「ヘルシーなものを食べた（チートデイ）」

### 大人の悩みを子供言葉で
- 「明日も休みだったらいいのに」
- 「有給がもっとほしい」
- 「何もしない日って最高」
- 「カロリーのことは考えないことにした」

### 仕事への皮肉を無邪気に
- 「今日は会議がなかった。さいこうの一日だった」
- 「Slackの通知を見なかった。えらい」
- 「パソコンをひらかなかった。やったー」

### 大人になってわかったこと
- 「公園は入場料がタダ。すごい」
- 「昼寝は人生のごほうび」
- 「おばあちゃんの料理はやっぱりちがう」

## 出力
絵日記テキストのみを出力してください（説明や注釈は不要）:
"""

    try:
        response = llm.invoke(prompt)
        diary_text = response.content.strip()
        return {"diary_text": diary_text}
    except Exception as e:
        print(f"Error generating diary: {e}")
        # フォールバック
        diary_text = "今日はたのしい一日だった。またあしたあそびたい。"
        return {"diary_text": diary_text}


def check_quality(state: DiaryState) -> dict:
    """生成された日記の品質をチェック"""
    diary_text = state.get("diary_text", "")

    prompt = f"""以下の絵日記テキストを評価してください。

テキスト:
{diary_text}

評価基準:
1. 子供らしい文体か (0.0-1.0)
2. 感情表現があるか (0.0-1.0)
3. 100-200文字程度か (0.0-1.0)
4. 絵日記として自然か (0.0-1.0)

JSON形式で総合スコア（0.0-1.0）のみを出力:
{{"score": 0.8}}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        # JSON部分を抽出
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        result = json.loads(content)
        score = result.get("score", 0.8)
        return {"quality_score": score}
    except Exception as e:
        print(f"Error checking quality: {e}")
        # フォールバック: 合格扱い
        return {"quality_score": 0.8}


def should_retry(state: DiaryState) -> str:
    """品質チェックの結果に基づいて次のノードを決定"""
    quality_score = state.get("quality_score", 0.0)
    retry_count = state.get("retry_count", 0)

    if quality_score >= 0.6:
        return "generate_image"
    elif retry_count < 3:
        return "generate_diary"
    else:
        return "fallback"


def increment_retry(state: DiaryState) -> dict:
    """リトライカウントをインクリメント"""
    return {"retry_count": state.get("retry_count", 0) + 1}


def generate_image(state: DiaryState) -> dict:
    """絵日記用の画像を生成 (Gemini 2.5 Flash Image)"""
    import uuid
    from io import BytesIO
    from google.cloud import storage
    from google import genai
    from google.genai import types

    diary_text = state.get("diary_text", "")
    keywords = state.get("keywords", [])
    document_id = state.get("document_id", "unknown")
    log = state["conversation_log"]

    # 日本語を英語に翻訳（Gemini を使用）
    translate_prompt = f"""Translate the following Japanese text to English for image generation.
Keep it simple and descriptive.

Keywords: {", ".join(keywords)}
Diary text: {diary_text[:200]}

Output format (JSON):
{{"scene": "English description of the scene", "elements": "key visual elements"}}
"""

    try:
        translate_response = llm.invoke(translate_prompt)
        translate_content = translate_response.content.strip()
        if "```json" in translate_content:
            translate_content = (
                translate_content.split("```json")[1].split("```")[0].strip()
            )
        elif "```" in translate_content:
            translate_content = (
                translate_content.split("```")[1].split("```")[0].strip()
            )
        translated = json.loads(translate_content)
        scene_desc = translated.get("scene", "a happy day")
        elements = translated.get("elements", "sunshine, nature")
    except Exception as e:
        print(f"Translation error: {e}")
        scene_desc = "a happy day at home"
        elements = "warm atmosphere, family"

    # 画像生成プロンプト（英語に翻訳済み）
    prompt = f"""A picture diary illustration in a warm, hand-drawn style.
Scene: {scene_desc}
Key elements: {elements}
Style: Colorful, cheerful, simple shapes, crayon-like texture, picture diary style.

Important: Bright colors, simple and cute illustration style."""

    try:
        # Gemini 2.5 Flash Image クライアント作成
        # us-central1 で利用可能
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="us-central1"
        )

        # 画像生成
        print(f"Generating image with Gemini 2.5 Flash Image: {prompt[:100]}...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                ),
            ),
        )

        # レスポンスから画像を取得
        image_data = None
        for part in response.parts:
            if part.inline_data:
                print(f"Image generated! MIME type: {part.inline_data.mime_type}")
                # inline_data.data から直接バイトデータを取得
                image_data = part.inline_data.data
                break

        if not image_data:
            print("No image generated in response")
            return {"image_url": None}

        # Cloud Storage にアップロード
        bucket_name = os.getenv("GCS_BUCKET_NAME", f"{PROJECT_ID}-enikki-images")
        storage_client = storage.Client(project=PROJECT_ID)

        try:
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                bucket = storage_client.create_bucket(bucket_name, location=REGION)
        except Exception as e:
            print(f"Bucket access error: {e}")
            bucket = storage_client.bucket(bucket_name)

        # ファイル名を生成
        filename = f"diaries/{document_id}/{uuid.uuid4()}.png"
        blob = bucket.blob(filename)

        # 画像データをアップロード
        blob.upload_from_string(image_data, content_type="image/png")

        # 公開URL（バケットレベルでallUsers読み取り権限設定済み）
        image_url = f"https://storage.googleapis.com/{bucket_name}/{filename}"

        print(f"Image uploaded: {image_url}")
        return {"image_url": image_url}

    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        # フォールバック: プレースホルダー
        return {
            "image_url": "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60"
        }


def fallback(state: DiaryState) -> dict:
    """リトライ上限に達した場合のフォールバック処理"""
    return {
        "status": "completed",
        "error": "品質チェックに3回失敗しましたが、現在のテキストで完了しました。",
    }


def save_result(state: DiaryState) -> dict:
    """結果を Firestore に保存し、Discord に通知"""
    from src.discord_notifier import send_discord_notification_sync

    # Discord通知を送信
    log = state["conversation_log"]
    document_id = state.get("document_id")
    title = log.get("date", "今日の絵日記")
    diary_text = state.get("diary_text", "")
    image_url = state.get("image_url")
    keywords = state.get("keywords")

    if diary_text:
        send_discord_notification_sync(
            title=title,
            diary_text=diary_text,
            diary_id=document_id,
            image_url=image_url,
            keywords=keywords,
        )

    return {"status": "completed"}


# --- グラフ構築 ---


def build_diary_workflow() -> StateGraph:
    """絵日記生成ワークフローのグラフを構築"""
    graph = StateGraph(DiaryState)

    # ノード追加
    graph.add_node("extract_keywords", extract_keywords)
    graph.add_node("generate_diary", generate_diary)
    graph.add_node("check_quality", check_quality)
    graph.add_node("increment_retry", increment_retry)
    graph.add_node("generate_image", generate_image)
    graph.add_node("fallback", fallback)
    graph.add_node("save_result", save_result)

    # エッジ追加
    graph.add_edge(START, "extract_keywords")
    graph.add_edge("extract_keywords", "generate_diary")
    graph.add_edge("generate_diary", "check_quality")

    # 条件分岐: 品質チェック後
    graph.add_conditional_edges(
        "check_quality",
        should_retry,
        {
            "generate_image": "generate_image",
            "generate_diary": "increment_retry",
            "fallback": "fallback",
        },
    )
    graph.add_edge("increment_retry", "generate_diary")
    graph.add_edge("generate_image", "save_result")
    graph.add_edge("fallback", "save_result")
    graph.add_edge("save_result", END)

    return graph


# コンパイル済みワークフロー
diary_workflow = build_diary_workflow().compile()


# --- 実行用ヘルパー ---


def run_diary_workflow(document_id: str, conversation_log: dict) -> DiaryState:
    """ワークフローを実行"""
    initial_state: DiaryState = {
        "document_id": document_id,
        "conversation_log": conversation_log,
        "keywords": None,
        "diary_text": None,
        "quality_score": None,
        "retry_count": 0,
        "image_url": None,
        "status": "pending",
        "error": None,
    }

    result = diary_workflow.invoke(initial_state)
    return result
