# FinGuard AI 演示脚本

## 演示场景：可疑跨境转账分析

### 场景背景
账户 `88888888` 在过去 3 天内发生多笔大额跨境转账，触发风控系统预警。

---

## 演示流程

### Step 1: 用户提交查询

```
用户：分析账户 88888888 的最近交易，怀疑存在洗钱风险
```

### Step 2: Coordinator Agent 接收并分解任务

```python
# Coordinator 分析意图
intent = {
    'type': 'account_analysis',
    'entities': {
        'account_id': '88888888',
        'time_range': 'last_3_days'
    },
    'urgency': 'high'
}

# 分解为 3 个子任务
tasks = [
    {'agent': 'risk_detector', 'action': 'analyze_transaction', 'payload': {...}},
    {'agent': 'investigation', 'action': 'trace_funds', 'payload': {...}},
    {'agent': 'compliance', 'action': 'check_aml_violations', 'payload': {...}}
]
```

### Step 3: RiskDetector Agent 执行风险检测

**输入数据：**
```json
{
  "account_id": "88888888",
  "transactions": [
    {"id": "tx001", "amount": 49500, "type": "cross_border", "direction": "out", "country": "US"},
    {"id": "tx002", "amount": 49800, "type": "cross_border", "direction": "out", "country": "HK"},
    {"id": "tx003", "amount": 49200, "type": "cross_border", "direction": "out", "country": "SG"},
    {"id": "tx004", "amount": 48900, "type": "cross_border", "direction": "out", "country": "KY"},
    {"id": "tx005", "amount": 49600, "type": "cross_border", "direction": "out", "country": "BVI"}
  ]
}
```

**RiskDetector 输出：**
```json
{
  "risk_score": 87,
  "risk_level": "CRITICAL",
  "anomalies": [
    {
      "type": "STRUCTURING",
      "severity": "HIGH",
      "description": "检测到 5 笔 49000-50000 元交易，疑似规避 CTR 报告阈值",
      "total_amount": 247000
    },
    {
      "type": "CROSS_BORDER_ANOMALY",
      "severity": "HIGH",
      "description": "跨境交易占比 100%，涉及多个离岸司法管辖区",
      "countries": ["US", "HK", "SG", "KY", "BVI"]
    },
    {
      "type": "FREQUENT_TRADING",
      "severity": "MEDIUM",
      "description": "3 天内 5 笔大额交易，频率异常"
    }
  ],
  "alert_flags": [
    {"level": "RED", "message": "高风险评分 87，建议立即冻结账户"},
    {"level": "ORANGE", "message": "疑似结构化交易，需提交 SAR 报告"}
  ]
}
```

### Step 4: Investigation Agent 深度调查

**资金流向追踪结果：**
```json
{
  "total_paths": 12,
  "suspicious_paths": 3,
  "flow_paths": [
    ["88888888", "US_12345", "KY_67890", "BVI_11111", "88888888"],
    ["88888888", "HK_22222", "SG_33333", "CN_44444"]
  ],
  "suspicious_details": [
    {
      "path": ["88888888", "US_12345", "KY_67890", "BVI_11111", "88888888"],
      "risk_score": 95,
      "risk_reasons": [
        "资金循环回流（路径中出现重复账户）",
        "涉及离岸账户：KY_67890, BVI_11111",
        "资金转移层级过深 (5 层)",
        "涉及高风险司法管辖区：Cayman Islands, BVI"
      ]
    }
  ],
  "ultimate_destinations": [
    {"account": "KY_67890", "jurisdiction": "Cayman Islands", "risk": "HIGH"},
    {"account": "BVI_11111", "jurisdiction": "British Virgin Islands", "risk": "HIGH"}
  ]
}
```

**关联账户网络分析：**
```json
{
  "network_size": 23,
  "pattern": "STAR_NETWORK",
  "hub_accounts": ["88888888", "CN_44444"],
  "centrality_score": 0.85,
  "isolated_clusters": [
    {"accounts": ["US_12345", "KY_67890", "BVI_11111"], "suspicion": "离岸洗钱网络"}
  ]
}
```

**洗钱模式检测：**
```json
{
  "patterns_detected": 2,
  "patterns": [
    {
      "pattern": "STRUCTURING",
      "confidence": "HIGH",
      "evidence": {
        "count": 5,
        "total_amount": 247000,
        "time_span": "72 hours"
      },
      "description": "检测到多笔接近 5 万阈值的交易，疑似结构化拆分规避报告"
    },
    {
      "pattern": "ROUND_TRIPPING",
      "confidence": "HIGH",
      "evidence": {
        "count": 2,
        "total_amount": 98000,
        "days_gap": 7
      },
      "description": "检测到资金出境后 7 天内回流，疑似伪装外资"
    }
  ],
  "overall_risk": "HIGH"
}
```

### Step 5: Compliance Agent 合规检查

**AML 违规检查：**
```json
{
  "violation_count": 6,
  "violation_score": 85,
  "violations": [
    {
      "type": "SAR_STRUCTURING",
      "severity": "HIGH",
      "regulation": "PBOC-SAR-001",
      "description": "检测到结构化交易模式，疑似规避 CTR 报告",
      "action": "FILE_SAR"
    },
    {
      "type": "SAR_FREQUENT_CROSS_BORDER",
      "severity": "HIGH",
      "regulation": "PBOC-SAR-004",
      "description": "频繁跨境资金转移，疑似洗钱",
      "action": "FILE_SAR"
    },
    {
      "type": "CTR_CUMULATIVE",
      "severity": "MEDIUM",
      "regulation": "PBOC-CTR-2026",
      "description": "当日累计交易 148500 元，达到 CTR 报告阈值",
      "action": "FILE_CTR"
    },
    {
      "type": "HIGH_RISK_JURISDICTION",
      "severity": "MEDIUM",
      "regulation": "AML-GEO-001",
      "description": "涉及开曼群岛、BVI 等高风险司法管辖区",
      "action": "ENHANCED_MONITORING"
    }
  ],
  "requires_sar": true,
  "requires_ctr": true,
  "recommended_actions": [
    {"action": "FILE_SAR", "priority": "HIGH", "deadline": "5 working days"},
    {"action": "FILE_CTR", "priority": "MEDIUM", "deadline": "5 working days"},
    {"action": "ENHANCED_MONITORING", "priority": "MEDIUM"}
  ]
}
```

### Step 6: Coordinator 汇总结果并生成最终报告

**最终风险评估报告：**
```json
{
  "report_id": "RPT-20260303-888888",
  "account_id": "88888888",
  "overall_risk_score": 87,
  "risk_level": "CRITICAL",
  "summary": "该账户存在严重的洗钱嫌疑，包括结构化交易规避报告、资金往返离岸管辖区、多层复杂资金转移等特征",
  
  "evidence_chain": [
    "5 笔 49000-50000 元交易，疑似规避 CTR 阈值",
    "资金流向开曼群岛、BVI 等离岸账户后回流",
    "3 天内频繁跨境转账，无合理商业目的",
    "关联账户网络呈现星型结构，疑似资金池"
  ],
  
  "recommendations": [
    {
      "action": "FREEZE_ACCOUNT",
      "priority": "CRITICAL",
      "reason": "风险评分 87，存在严重洗钱嫌疑"
    },
    {
      "action": "FILE_SAR",
      "priority": "HIGH",
      "reason": "触发多项 SAR 报告条件",
      "deadline": "2026-03-10"
    },
    {
      "action": "FILE_CTR",
      "priority": "MEDIUM",
      "reason": "大额交易达到报告阈值",
      "deadline": "2026-03-10"
    },
    {
      "action": "MANUAL_REVIEW",
      "priority": "HIGH",
      "reason": "需要人工复核证据材料"
    }
  ],
  
  "auto_actions_taken": [
    "账户交易限额已降低至 10000 元/日",
    "已标记为高风险客户",
    "已生成 SAR 报告草稿"
  ],
  
  "generated_reports": [
    {"type": "SAR", "id": "SAR-20260303-888888", "status": "PENDING_REVIEW"},
    {"type": "CTR", "id": "CTR-20260303-888888", "status": "PENDING_REVIEW"},
    {"type": "AUDIT_TRAIL", "id": "AUDIT-20260303211500", "status": "COMPLETED"}
  ],
  
  "timestamp": "2026-03-03T21:15:00+08:00",
  "processed_by": "FinGuard AI Multi-Agent System"
}
```

---

## 演示亮点

### 1. Multi-Agent 协作
- ✅ 4 个智能体并行工作
- ✅ MCP 协议标准化通信
- ✅ 结果自动汇总合成

### 2. 复杂推理能力
- ✅ CoT (Chain of Thought): 逐步推理洗钱模式
- ✅ ToT (Tree of Thoughts): 多路径资金流向分析
- ✅ ReAct 框架：推理 - 行动循环

### 3. 任务执行体演进
- ✅ 不仅回答问题，还自动执行：
  - 降低账户交易限额
  - 标记高风险客户
  - 生成监管报告草稿
  - 记录审计日志

### 4. 专业合规能力
- ✅ 符合中国人民银行 AML 规定
- ✅ 自动生成 SAR/CTR 报告
- ✅ 完整的审计追踪

---

## 技术栈展示

| 技术 | 实现 |
|------|------|
| Multi-Agent | 4 个专业智能体协作 |
| MCP 协议 | 标准化 JSON 消息格式 |
| CoT/ToT | 复杂推理引擎 |
| ReAct | 推理 - 行动循环 |
| Function Calling | 调用外部 API、数据库 |
| Context Management | 动态上下文维护 |
| Post-training | SFT/RL 优化模型能力 |

---

## 部署说明

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/finguard-ai.git

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
export OPENCLAW_GATEWAY="ws://127.0.0.1:18789"
export OPENCLAW_TOKEN="your-token"

# 4. 运行演示
python demo.py --scenario cross_border_laundry

# 5. 查看报告
open reports/SAR-20260303-888888.pdf
```

---

**FinGuard AI - 从对话式 AI 到任务执行体的演进** 🚀