import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.auth
import google.auth.transport.requests

app = FastAPI()

# CORS設定
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    projectId: str
    region: str


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def get_auth_token():
    """
    Vertex AI (Multimodal Live API) 接続用のアクセストークンを発行する。
    フロントエンドはこのトークンを使って Gemini に直接接続する。
    """
    # デフォルト認証情報を取得
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    # トークンをリフレッシュして取得
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    
    # 環境変数から設定を取得（デフォルト値付き）
    project_id = os.getenv("GCP_PROJECT_ID", project or "enikki-cloud")
    region = os.getenv("GCP_REGION", "asia-northeast1")
    
    return TokenResponse(
        accessToken=credentials.token,
        expiresIn=3600,
        projectId=project_id,
        region=region
    )


@app.get("/diary/stub")
def get_stub_diary():
    return {
        "imageSrc": "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHN1bW1lciUyMHZpYmV8ZW58MHx8MHx8fDA%3D",
        "text": "今日はとても良い天気でした。近くの公園まで散歩に行きました。セミの声がたくさん聞こえて、夏を感じました。お昼には冷たいそうめんを食べました。"
    }
