"""
絵日記生成ワークフロー (LangGraph)

会話ログを入力として、以下のステップで絵日記を生成します:
1. キーワード抽出 (Gemini)
2. 日記文章生成 (Gemini)
3. 品質チェック (Gemini) -> NG なら 2 に戻る
4. 画像生成 (Imagen 3)
5. Firestore 保存
"""

from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


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


# --- ノード定義 ---


def extract_keywords(state: DiaryState) -> dict:
    """会話ログから4つのキーワードを抽出"""
    # TODO: Gemini API を使ってキーワード抽出
    # 仮実装: conversation_log から直接取得
    log = state["conversation_log"]
    keywords = [
        log.get("activity", ""),
        log.get("feeling", ""),
        log.get("location", "場所不明"),
        "今日",
    ]
    return {"keywords": keywords, "status": "processing"}


def generate_diary(state: DiaryState) -> dict:
    """キーワードを元に絵日記テキストを生成"""
    # TODO: Gemini API を使って日記生成
    # 仮実装: シンプルなテンプレート
    keywords = state.get("keywords", [])
    log = state["conversation_log"]
    summary = log.get("summary", "今日は楽しかったです。")
    
    diary_text = f"今日は{log.get('location', 'どこか')}で{log.get('activity', '遊びました')}。{log.get('feeling', '楽しかった')}です。"
    
    return {"diary_text": diary_text}


def check_quality(state: DiaryState) -> dict:
    """生成された日記の品質をチェック"""
    # TODO: Gemini API を使って品質評価
    # 仮実装: 常に OK
    return {"quality_score": 0.8}


def should_retry(state: DiaryState) -> str:
    """品質チェックの結果に基づいて次のノードを決定"""
    quality_score = state.get("quality_score", 0.0)
    retry_count = state.get("retry_count", 0)
    
    if quality_score >= 0.7:
        return "generate_image"
    elif retry_count < 3:
        return "generate_diary"
    else:
        return "fallback"


def increment_retry(state: DiaryState) -> dict:
    """リトライカウントをインクリメント"""
    return {"retry_count": state.get("retry_count", 0) + 1}


def generate_image(state: DiaryState) -> dict:
    """絵日記用の画像を生成"""
    # TODO: Imagen 3 API を使って画像生成
    # TODO: Cloud Storage に保存
    # 仮実装: プレースホルダー URL
    image_url = "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60"
    return {"image_url": image_url}


def fallback(state: DiaryState) -> dict:
    """リトライ上限に達した場合のフォールバック処理"""
    return {
        "status": "completed",
        "error": "品質チェックに3回失敗しましたが、現在のテキストで完了しました。",
    }


def save_result(state: DiaryState) -> dict:
    """結果を Firestore に保存"""
    # TODO: Firestore への保存処理
    # 仮実装: ステータスを完了に
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
