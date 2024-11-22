from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.face_service import face_service
import json

# 创建FastAPI应用实例，添加文档配置
app = FastAPI(
    title="Face Recognition API",
    description="多算法人脸识别系统API文档",
    version="1.0.0",
    docs_url="/docs",   # Swagger UI 地址，默认为 /docs
    redoc_url="/redoc"  # ReDoc 地址，默认为 /redoc
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register")
async def register(
    image: UploadFile = File(...),
    name: str = Form(...),
    id: str = Form(...)
):
    """
    人脸注册接口
    - **image**: 人脸图片文件
    - **name**: 用户姓名
    - **id**: 用户ID
    """
    contents = await image.read()
    user_data = {
        "name": name,
        "id": id
    }
    success, message = face_service.register_face(contents, user_data)
    return {"success": success, "message": message}

@app.post("/api/recognize")
async def recognize(image: UploadFile = File(...)):
    """
    人脸识别接口
    - **image**: 人脸图片文件
    """
    contents = await image.read()
    success, result = face_service.recognize_face(contents)
    if success:
        return {"success": True, "data": result}
    return {"success": False, "message": result}

@app.get("/")
async def root():
    """
    测试API是否正常工作
    """
    return {"status": "ok", "message": "Face Recognition API is running"}

if __name__ == "__main__":
    import uvicorn
    import logging

    # 配置日志
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("uvicorn")

    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8001,
            reload=True,          # 启用热加载
            workers=1,            # 开发时使用单个worker
            log_level="debug"     # 使用debug日志级别
        )
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise e 