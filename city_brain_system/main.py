from fastapi import FastAPI
from api.routes import router
from api.progressive_routes import router as progressive_router

app = FastAPI(
    title="城市大脑企业信息处理系统",
    description="一个智能信息处理平台，通过结合本地数据库、联网搜索和大语言模型技术，为用户提供企业及其关联产业信息的结构化总结。",
    version="1.0.0"
)

app.include_router(router)
app.include_router(progressive_router)

@app.get("/")
async def root():
    return {"message": "欢迎使用城市大脑企业信息处理系统"}