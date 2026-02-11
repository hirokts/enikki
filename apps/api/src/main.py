import datetime
import os

import google.auth
import google.auth.transport.requests
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth, credentials

from src.models import ConversationLogRequest, DiaryResponse

app = FastAPI()

# Firebase Admin 初期化
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "enikki-cloud")

if not firebase_admin._apps:
    try:
        # 明示的にプロジェクトIDを指定して初期化
        firebase_admin.initialize_app(options={'projectId': project_id})
        print(f"Firebase Admin initialized for project: {project_id}")
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")
        firebase_admin.initialize_app()

# CORS設定（環境変数から許可オリジンを取得）
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Firebase Token 検証
def verify_firebase_token(x_firebase_token: str = Header(..., alias="X-Firebase-Token")):
    """Firebase ID トークンを検証する"""
    try:
        decoded_token = auth.verify_id_token(x_firebase_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase token")


class TokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    projectId: str
    region: str


# Firestore クライアント初期化
# ローカル開発などでプロジェクトIDが自動取得できない場合や、環境変数で指定したい場合に対応
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "enikki-cloud")
try:
    db = firestore.Client(project=project_id)
except Exception as e:
    print(f"Warning: Failed to initialize Firestore client: {e}")
    db = None


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def get_auth_token(decoded_token: dict = Depends(verify_firebase_token)):
    """
    Vertex AI (Multimodal Live API) 接続用のアクセストークンを発行する。
    フロントエンドはこのトークンを使って Gemini に直接接続する。

    認証: X-Firebase-Token ヘッダーが必要
    """

    # デフォルト認証情報を取得
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # トークンをリフレッシュして取得
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)

    # 環境変数から設定を取得（デフォルト値付き）
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", project or "enikki-cloud")
    region = os.getenv("GCP_REGION", "asia-northeast1")

    return TokenResponse(
        accessToken=credentials.token,
        expiresIn=3600,
        projectId=project_id,
        region=region,
    )


def process_diary_in_background(document_id: str, conversation_log: dict):
    """バックグラウンドで絵日記ワークフローを実行"""
    from src.diary_workflow import run_diary_workflow

    try:
        # ステータスを processing に更新
        db.collection("diaries").document(document_id).update({
            "status": "processing",
            "updatedAt": datetime.datetime.now(datetime.timezone.utc),
        })

        result = run_diary_workflow(document_id, conversation_log)

        # ワークフロー結果で Firestore を更新
        update_data = {
            "status": result.get("status", "completed"),
            "keywords": result.get("keywords"),
            "diaryText": result.get("diary_text"),
            "imageUrl": result.get("image_url"),
            "updatedAt": datetime.datetime.now(datetime.timezone.utc),
        }
        if result.get("error"):
            update_data["error"] = result["error"]

        db.collection("diaries").document(document_id).update(update_data)
        print(f"Diary {document_id} completed successfully")
    except Exception as e:
        # エラー時は Firestore にエラーを記録
        print(f"Error processing diary {document_id}: {e}")
        db.collection("diaries").document(document_id).update({
            "status": "failed",
            "error": str(e),
            "updatedAt": datetime.datetime.now(datetime.timezone.utc),
        })


@app.post("/diaries", response_model=DiaryResponse)
def create_diary(
    request: ConversationLogRequest,
    background_tasks: BackgroundTasks,
    decoded_token: dict = Depends(verify_firebase_token),
):
    """
    会話ログ（要約データ）を受け取り、Firestoreに保存し、
    バックグラウンドで LangGraph ワークフローを実行する。
    """
    # トークンからUIDを取得
    user_id = decoded_token.get("uid", "unknown-user")

    if not db:
        raise HTTPException(status_code=500, detail="Firestore database not connected")

    try:
        # 保存するデータの構築
        doc_data = request.model_dump()
        doc_data.update(
            {
                "userId": user_id,
                "status": "pending",  # 待機中
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
            }
        )

        # Firestore に保存 (自動生成ID)
        update_time, doc_ref = db.collection("diaries").add(doc_data)
        document_id = doc_ref.id

        # 会話ログを構築
        conversation_log = {
            "date": request.date,
            "location": request.location,
            "activity": request.activity,
            "feeling": request.feeling,
            "summary": request.summary,
            "joke_hint": request.joke_hint,
        }

        # バックグラウンドでワークフローを実行
        background_tasks.add_task(process_diary_in_background, document_id, conversation_log)

        # 即座に pending ステータスを返す
        return DiaryResponse(id=document_id, status="pending")
    except Exception as e:
        print(f"Error creating diary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create diary: {str(e)}")


@app.get("/diary/stub")
def get_stub_diary():
    return {
        "imageSrc": "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHN1bW1lciUyMHZpYmV8ZW58MHx8MHx8fDA%3D",
        "text": "今日はとても良い天気でした。近くの公園まで散歩に行きました。セミの声がたくさん聞こえて、夏を感じました。お昼には冷たいそうめんを食べました。",
    }
