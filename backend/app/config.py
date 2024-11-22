from pathlib import Path
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 基础配置
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 模型存储目录
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# 设置 DeepFace 模型存储路径（使用绝对路径更可靠）
os.environ["DEEPFACE_HOME"] = str(MODEL_DIR.absolute())

# MongoDB配置
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "face_recognition"
COLLECTION_NAME = "face_embeddings"