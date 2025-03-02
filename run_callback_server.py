from gewechat_client.callback.server import run_server

if __name__ == '__main__':
    # 默认在3001端口启动服务器
    # 可以通过传入port参数修改端口号，例如：run_server(port=5000)
    run_server()