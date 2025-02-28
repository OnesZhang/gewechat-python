import unittest
from gewechat_client.message_handler import MessageHandler

class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MessageHandler()

    def test_receive_message(self):
        # 测试接收消息的逻辑
        self.assertIsNone(self.handler.receive_message('test message'))

if __name__ == '__main__':
    unittest.main() 