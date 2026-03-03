# FinGuard AI - 金融风控多智能体系统

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                         │
│                   (任务协调与决策中枢)                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ RiskDetector  │    │ Investigation │    │  Compliance   │
│    Agent      │    │    Agent      │    │    Agent      │
│  (风险检测)    │    │  (深度调查)    │    │  (合规检查)    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 智能体职责

### 1. Coordinator Agent (协调器)
- 接收用户查询，分析意图
- 分配任务给子智能体
- 汇总结果，生成最终报告
- 决策是否触发自动化行动

### 2. RiskDetector Agent (风险检测)
- 实时监控交易数据
- 识别异常模式（大额、频繁、跨境）
- 计算风险评分
- 标记可疑交易

### 3. Investigation Agent (深度调查)
- 追踪资金流向链路
- 分析关联账户网络
- 识别洗钱模式（分散转入集中转出等）
- 生成调查报告

### 4. Compliance Agent (合规检查)
- 检查 AML/KYC 规则违反
- 生成监管报告
- 建议合规行动
- 记录审计日志

## MCP 协议通信

智能体间使用标准化消息格式：
```json
{
  "from": "coordinator",
  "to": "risk_detector",
  "action": "analyze_transaction",
  "payload": {
    "account_id": "88888888",
    "transaction_ids": ["tx1", "tx2"],
    "context": "大额跨境转账"
  },
  "priority": "high"
}
```

## ReAct 推理框架

每个智能体遵循 ReAct 循环：
1. **Thought**: 分析当前状态
2. **Action**: 调用工具/函数
3. **Observation**: 获取结果
4. **Repeat**: 直到任务完成

## 技术栈

- **LLM**: Qwen 3.5 Plus (262K 上下文)
- **Agent 框架**: 基于 OpenClaw sessions_spawn
- **通信协议**: MCP (Model Context Protocol)
- **数据存储**: Feishu Bitable
- **报告生成**: Feishu Doc