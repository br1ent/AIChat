# 测试脚本说明

## 目录结构

```
tests/
├── loadtest.js              # k6 负载测试脚本
├── evaluate_rag.py          # RAG 检索准确率评估脚本
├── test_queries.json        # RAG 评估测试数据集
├── requirements.txt         # Python 依赖
└── README.md               # 本文件
```

## 1. 负载测试 (k6)

### 安装 k6

```bash
# Windows (winget)
winget install k6

# Windows (choco)
choco install k6

# macOS
brew install k6

# Linux
sudo snap install k6
```

### 运行测试

```bash
# 使用默认配置 (100 VUs, 4 分钟)
k6 run tests/loadtest.js

# 自定义并发数和持续时间
k6 run --vus 100 --duration 2m tests/loadtest.js

# 自定义服务器地址和测试用户
k6 run --env BASE_URL=http://your-server:8000 \
       --env TEST_USERNAME=testuser \
       --env TEST_PASSWORD=testpass123 \
       tests/loadtest.js
```

### 测试指标

| 指标 | 说明 | 达标值 |
|------|------|--------|
| http_req_duration | 所有 HTTP 请求响应时间 | p95 < 200ms |
| login_duration | 登录接口响应时间 | p95 < 300ms |
| rest_api_duration | REST API 接口响应时间 | p95 < 200ms |
| chat_ttfb | 聊天 SSE 首 token 延迟 | p95 < 1000ms |
| chat_success_rate | 聊天接口成功率 | > 95% |

### 测试场景

1. **预热阶段**: 0 → 20 VUs (30秒)
2. **爬升阶段**: 20 → 50 VUs (30秒)
3. **压力阶段**: 50 → 100 VUs (1分钟)
4. **持续阶段**: 保持 100 VUs (2分钟)
5. **下降阶段**: 100 → 0 VUs (30秒)

### 输出

- 控制台实时输出测试结果
- 生成 `tests/loadtest-report.json` 详细报告

---

## 2. RAG 检索准确率评估

### 安装依赖

```bash
cd backend
pip install -r ../tests/requirements.txt
```

### 运行评估

```bash
cd backend
python -m tests.evaluate_rag
```

### 评估指标

| 指标 | 说明 | 达标值 |
|------|------|--------|
| Recall@3 | Top-3 结果中包含相关文档的比例 | ≥ 85% |
| Recall@5 | Top-5 结果中包含相关文档的比例 | ≥ 90% |
| Precision@3 | Top-3 结果中相关文档的占比 | 参考 |
| MRR | 第一个相关文档的平均倒数排名 | ≥ 0.8 |
| Hit Rate | 至少命中一个相关文档的查询比例 | ≥ 90% |

### 测试数据集

`test_queries.json` 包含 15 个测试查询，覆盖以下主题：

- 后端技术栈 (Java, Spring Boot, MyBatis)
- 用户认证 (JWT, Spring Security)
- 前端技术栈 (Vue 3, Vuex)
- 实时通信 (WebSocket)
- 数据库 (MySQL)
- 架构设计 (微服务)

### 输出

- 控制台输出每个查询的详细评估结果
- 生成 `tests/rag_evaluation_report.json` 详细报告

---

## 3. 结果解读

### 负载测试达标标准

- **100+ 并发**: 在 100 VUs 持续压力下，系统稳定运行
- **API 响应 < 200ms**: 95% 的 REST API 请求响应时间 < 200ms
- **SSE TTFB < 1s**: 95% 的聊天请求首 token 延迟 < 1秒

### RAG 评估达标标准

- **Recall@3 ≥ 85%**: Top-3 检索结果中，85% 的相关关键词被覆盖
- **MRR ≥ 0.8**: 第一个相关文档平均排在前 1.25 位
- **Hit Rate ≥ 90%**: 90% 的查询至少命中一个相关文档

---

## 4. 注意事项

1. **测试环境**: 建议在与生产环境相近的配置下运行测试
2. **数据准备**: 确保 LanceDB 知识库已正确初始化
3. **用户账号**: 负载测试需要有效的测试用户账号
4. **网络条件**: 测试结果受网络延迟影响，建议在内网环境测试
5. **SSE 测试**: 聊天接口使用 SSE 流式响应，k6 测量的是完整响应时间，实际 TTFB 可能更短
