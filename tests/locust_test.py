"""
Locust 负载测试脚本 - 替代 k6

使用方法：
    pip install locust
    locust -f tests/locust_test.py --host=http://127.0.0.1:8000

    然后浏览器打开 http://localhost:8089 设置并发数和启动测试
"""

from locust import HttpUser, task, between, events
import json
import random


class ChatUser(HttpUser):
    """模拟用户行为"""
    wait_time = between(0.5, 2)  # 请求间隔 0.5-2 秒

    def on_start(self):
        """用户启动时登录"""
        self.token = None
        self.friend_id = 1

        # 注册（忽略已存在错误）
        self.client.post("/api/user/account/register/", json={
            "username": f"loadtest_{random.randint(10000, 99999)}",
            "password": "testpass123"
        })

        # 登录
        res = self.client.post("/api/user/account/login/", json={
            "username": f"loadtest_{random.randint(10000, 99999)}",
            "password": "testpass123"
        })

        if res.status_code == 200:
            data = res.json()
            self.token = data.get("access")

    def _auth_headers(self):
        """带认证的请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @task(5)
    def get_user_info(self):
        """获取用户信息 - 权重 5"""
        self.client.get(
            "/api/user/account/get_user_info/",
            headers=self._auth_headers(),
            name="/api/user/account/get_user_info/"
        )

    @task(4)
    def get_character_list(self):
        """获取角色列表 - 权重 4"""
        self.client.get(
            "/api/create/character/get_list/",
            headers=self._auth_headers(),
            name="/api/create/character/get_list/"
        )

    @task(3)
    def get_friend_list(self):
        """获取好友列表 - 权重 3"""
        self.client.get(
            "/api/friend/get_list/",
            headers=self._auth_headers(),
            name="/api/friend/get_list/"
        )

    @task(2)
    def chat_sse(self):
        """聊天 SSE - 权重 2"""
        messages = [
            "你好", "今天天气怎么样", "给我讲个笑话",
            "推荐一部电影", "什么是人工智能"
        ]
        self.client.post(
            "/api/friend/message/chat/",
            json={
                "friend_id": self.friend_id,
                "message": random.choice(messages)
            },
            headers={**self._auth_headers(), "Accept": "text/event-stream"},
            name="/api/friend/message/chat/"
        )

    @task(1)
    def homepage(self):
        """首页 - 权重 1"""
        self.client.get("/api/homepage/index/", name="/api/homepage/index/")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 50)
    print("  负载测试开始")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 50)
    print("  负载测试结束")
    print("=" * 50)
