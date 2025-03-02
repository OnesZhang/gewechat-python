from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .dispatcher import Dispatcher
import uvicorn
from ..util.logger import logger

app = FastAPI(title="GeWechat Callback Service")
dispatcher = Dispatcher()

@app.post("/callback")
async def handle_callback(request: Request):
    try:
        # 获取回调消息
        message = await request.json()
        logger.debug(f"接收到回调消息: {message}")
        
        # 使用dispatcher处理消息
        result = dispatcher.dispatch(message)
        logger.info(f"消息处理完成: {result}")
        
        return JSONResponse(content={
            "code": 0,
            "message": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"处理回调消息时发生错误: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"处理回调消息时发生错误: {str(e)}",
                "data": None
            }
        )

def run_server(port: int = 3001):
    """启动回调服务器
    
    Args:
        port (int, optional): 服务器端口号. Defaults to 3001.
    """
    try:
        logger.info(f"正在启动回调服务器，端口: {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"启动回调服务器失败: {str(e)}", exc_info=True)
        raise