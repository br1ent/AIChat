/**
 * 负载测试脚本 - 测试并发性能和 API 响应时间
 * 
 * 使用方法：
 *   1. 安装 k6: https://k6.io/docs/get-started/installation/
 *   2. 运行: k6 run tests/loadtest.js
 *   3. 自定义参数: k6 run --vus 100 --duration 2m tests/loadtest.js
 * 
 * 测试场景：
 *   - REST API 接口响应时间 (登录、用户信息、角色列表等)
 *   - SSE 聊天接口首 token 延迟 (TTFB)
 *   - 100+ 并发用户压力测试
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

// ==================== 配置 ====================

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';
const TEST_USERNAME = __ENV.TEST_USERNAME || 'testuser';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'testpass123';
const FRIEND_ID = __ENV.FRIEND_ID || '1';

// 自定义指标
const loginDuration = new Trend('login_duration', true);
const chatTTFB = new Trend('chat_ttfb', true);
const chatSuccess = new Rate('chat_success_rate');
const restApiDuration = new Trend('rest_api_duration', true);

// ==================== 测试配置 ====================

export const options = {
  stages: [
    { target: 20, duration: '30s' },   // 预热阶段: 0 -> 20 VUs
    { target: 50, duration: '30s' },   // 爬升阶段: 20 -> 50 VUs
    { target: 100, duration: '1m' },   // 压力阶段: 50 -> 100 VUs
    { target: 100, duration: '2m' },   // 持续阶段: 保持 100 VUs
    { target: 0, duration: '30s' },    // 下降阶段: 100 -> 0 VUs
  ],
  thresholds: {
    http_req_duration: ['p(95) < 200'],  // 95% 请求 < 200ms
    login_duration: ['p(95) < 300'],     // 登录 95% < 300ms
    rest_api_duration: ['p(95) < 200'],  // REST API 95% < 200ms
    chat_ttfb: ['p(95) < 1000'],         // 聊天 TTFB 95% < 1s
  },
};

// ==================== 辅助函数 ====================

function getAuthHeaders(token) {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
}

// ==================== 测试场景 ====================

export function setup() {
  console.log(`正在连接服务器: ${BASE_URL}`);

  // 1. 先尝试注册
  const registerRes = http.post(
    `${BASE_URL}/api/user/account/register/`,
    JSON.stringify({
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  console.log(`注册响应: ${registerRes.status} - ${registerRes.body.substring(0, 200)}`);

  // 2. 登录获取 token
  const loginRes = http.post(
    `${BASE_URL}/api/user/account/login/`,
    JSON.stringify({
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  console.log(`登录响应: ${loginRes.status} - ${loginRes.body.substring(0, 200)}`);

  if (loginRes.status === 200) {
    try {
      const body = JSON.parse(loginRes.body);
      console.log(`登录成功, token: ${body.access ? body.access.substring(0, 20) + '...' : 'null'}`);
      return { token: body.access, userId: body.user_id };
    } catch (e) {
      console.error(`解析登录响应失败: ${e.message}`);
    }
  }

  console.error('登录失败，请确保服务器已启动且可以访问');
  return { token: null, userId: null };
}

export default function (data) {
  if (!data.token) {
    console.warn('无有效 token，跳过测试');
    return;
  }

  group('REST API 测试', () => {
    // 测试获取用户信息
    group('获取用户信息', () => {
      const start = Date.now();
      const res = http.get(
        `${BASE_URL}/api/user/account/get_user_info/`,
        getAuthHeaders(data.token)
      );
      const duration = Date.now() - start;
      restApiDuration.add(duration);

      check(res, {
        '用户信息状态码 200': (r) => r.status === 200,
        '响应时间 < 200ms': (r) => r.timings.duration < 200,
      });
    });

    sleep(0.1);

    // 测试获取角色列表
    group('获取角色列表', () => {
      const start = Date.now();
      const res = http.get(
        `${BASE_URL}/api/create/character/get_list/`,
        getAuthHeaders(data.token)
      );
      const duration = Date.now() - start;
      restApiDuration.add(duration);

      check(res, {
        '角色列表状态码 200': (r) => r.status === 200,
        '响应时间 < 200ms': (r) => r.timings.duration < 200,
      });
    });

    sleep(0.1);

    // 测试获取好友列表
    group('获取好友列表', () => {
      const start = Date.now();
      const res = http.get(
        `${BASE_URL}/api/friend/get_list/`,
        getAuthHeaders(data.token)
      );
      const duration = Date.now() - start;
      restApiDuration.add(duration);

      check(res, {
        '好友列表状态码 200': (r) => r.status === 200,
        '响应时间 < 200ms': (r) => r.timings.duration < 200,
      });
    });
  });

  sleep(0.2);

  // 测试 SSE 聊天接口
  group('SSE 聊天测试', () => {
    const chatMessages = [
      '你好',
      '今天天气怎么样？',
      '给我讲个笑话',
      '推荐一部电影',
      '什么是人工智能？',
    ];
    const message = chatMessages[Math.floor(Math.random() * chatMessages.length)];

    const start = Date.now();
    const res = http.post(
      `${BASE_URL}/api/friend/message/chat/`,
      JSON.stringify({
        friend_id: parseInt(FRIEND_ID),
        message: message,
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${data.token}`,
          'Accept': 'text/event-stream',
        },
        timeout: '30s',
      }
    );

    const ttfb = Date.now() - start;
    chatTTFB.add(ttfb);

    const success = res.status === 200;
    chatSuccess.add(success);

    check(res, {
      '聊天状态码 200': (r) => r.status === 200,
      'TTFB < 1s': (r) => ttfb < 1000,
      '包含 SSE 数据': (r) => r.body && r.body.includes('data:'),
    });
  });

  sleep(0.5);
}

export function teardown(data) {
  // 清理：可以删除测试用户或记录最终结果
  console.log('负载测试完成');
}

// ==================== 自定义报告 ====================

export function handleSummary(data) {
  const summary = {
    '测试时间': new Date().toISOString(),
    '总请求数': data.metrics.http_reqs?.values?.count || 0,
    '平均响应时间': `${(data.metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms`,
    'P95 响应时间': `${(data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2)}ms`,
    'P99 响应时间': `${(data.metrics.http_req_duration?.values?.['p(99)'] || 0).toFixed(2)}ms`,
    '登录 P95': `${(data.metrics.login_duration?.values?.['p(95)'] || 0).toFixed(2)}ms`,
    'REST API P95': `${(data.metrics.rest_api_duration?.values?.['p(95)'] || 0).toFixed(2)}ms`,
    '聊天 TTFB P95': `${(data.metrics.chat_ttfb?.values?.['p(95)'] || 0).toFixed(2)}ms`,
    '聊天成功率': `${((data.metrics.chat_success_rate?.values?.rate || 0) * 100).toFixed(2)}%`,
  };

  console.log('\n========== 测试结果摘要 ==========');
  for (const [key, value] of Object.entries(summary)) {
    console.log(`${key}: ${value}`);
  }
  console.log('====================================\n');

  return {
    'tests/loadtest-report.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
