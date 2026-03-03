# FinGuard AI - 快速开始指南

## 🚀 5 分钟上手

### 前置要求
- OpenClaw 环境已配置
- Python 3.9+
- 金融风控业务理解

### 安装步骤

```bash
# 1. 进入项目目录
cd finguard_ai

# 2. 安装依赖 (如有需要)
pip install openclaw-sdk networkx pandas

# 3. 配置环境变量
export OPENCLAW_GATEWAY="ws://127.0.0.1:18789"
export OPENCLAW_TOKEN="1f0cc87ba26e977f97c702714de8ec288e0e2f0bd1d40a19"
```

---

## 📖 使用示例

### 示例 1: 基础账户分析

```python
from agents.coordinator import CoordinatorAgent

# 创建协调器
coordinator = CoordinatorAgent()

# 提交分析请求
result = await coordinator.process_request(
    "分析账户 88888888 的最近交易，怀疑存在洗钱风险"
)

# 查看结果
print(f"风险评分：{result['risk_level']}")
print(f"建议行动：{result['recommendations']}")
```

### 示例 2: 多智能体协作

```python
# 并行执行 3 个智能体
tasks = [
    {'agent': 'risk_detector', 'action': 'analyze_transaction', 'payload': data},
    {'agent': 'investigation', 'action': 'trace_funds', 'payload': data},
    {'agent': 'compliance', 'action': 'check_aml', 'payload': data}
]

results = await coordinator.execute_parallel(tasks)

# 汇总结果
final_report = coordinator.synthesize_results(results)
```

### 示例 3: 生成 SAR 报告

```python
from agents.compliance import ComplianceAgent

compliance = ComplianceAgent()

sar_report = await compliance.generate_suspicious_activity_report({
    'account_id': '88888888',
    'violations': violations,
    'investigation_results': investigation_data,
    'customer_name': '张三',
    'total_amount': 247000
})

# 导出 PDF
pdf_url = sar_report['pdf_url']
print(f"SAR 报告已生成：{pdf_url}")
```

---

## 🎯 典型场景

### 场景 1: 可疑跨境转账

**输入**:
```
账户 88888888 在 3 天内发生 5 笔 49000-50000 元跨境转账，
收款方涉及美国、香港、新加坡、开曼群岛、BVI
```

**输出**:
```
风险评分：87/100 (CRITICAL)
检测到模式:
  ✅ 结构化交易 (STRUCTURING)
  ✅ 资金往返 (ROUND_TRIPPING)
  ✅ 跨境异常 (CROSS_BORDER_ANOMALY)

建议行动:
  🔴 立即冻结账户
  🟠 提交 SAR 报告 (5 个工作日内)
  🟡 提交 CTR 报告
```

### 场景 2: 关联账户网络分析

**输入**:
```
分析账户 88888888 的关联账户网络
```

**输出**:
```
网络规模：23 个账户
网络模式：STAR_NETWORK (星型)
中心节点：88888888, 99999999
中心性评分：0.85

可疑子网络:
  - [US_12345, KY_67890, BVI_11111]
    嫌疑：离岸洗钱网络
```

### 场景 3: 合规检查

**输入**:
```
检查账户 88888888 的 AML 合规状态
```

**输出**:
```
违规数量：6 项
违规评分：85/100

违规详情:
  ❌ SAR_STRUCTURING (HIGH) - 结构化交易
  ❌ SAR_FREQUENT_CROSS_BORDER (HIGH) - 频繁跨境
  ⚠️ CTR_CUMULATIVE (MEDIUM) - 大额累计
  ⚠️ HIGH_RISK_JURISDICTION (MEDIUM) - 高风险管辖区

需要提交:
  ✅ SAR 报告
  ✅ CTR 报告
```

---

## 📊 输出格式

### 标准响应结构

```json
{
  "report_id": "RPT-20260303-888888",
  "account_id": "88888888",
  "overall_risk_score": 87,
  "risk_level": "CRITICAL",
  "summary": "存在严重洗钱嫌疑...",
  
  "evidence_chain": [
    "证据 1...",
    "证据 2...",
    "证据 3..."
  ],
  
  "recommendations": [
    {
      "action": "FREEZE_ACCOUNT",
      "priority": "CRITICAL",
      "reason": "风险评分 87"
    }
  ],
  
  "generated_reports": [
    {"type": "SAR", "id": "SAR-xxx", "status": "PENDING"},
    {"type": "CTR", "id": "CTR-xxx", "status": "PENDING"}
  ],
  
  "timestamp": "2026-03-03T21:15:00+08:00"
}
```

---

## 🔧 配置选项

### 风险阈值配置

```python
# 在 risk_detector.py 中配置
thresholds = {
    'large_amount': 50000,      # 大额交易阈值
    'frequent_count': 5,         # 频繁交易次数
    'cross_border_ratio': 0.3,   # 跨境交易占比
    'velocity_window_hours': 24  # 速度监控时间窗口
}
```

### 风险评分权重

```python
severity_weights = {
    'critical': 25,
    'high': 15,
    'medium': 8,
    'low': 3
}
```

### 风险等级分类

```python
def classify_risk(score):
    if score >= 80: return 'CRITICAL'
    elif score >= 60: return 'HIGH'
    elif score >= 40: return 'MEDIUM'
    elif score >= 20: return 'LOW'
    else: return 'MINIMAL'
```

---

## 📝 最佳实践

### 1. 批量处理

```python
# 推荐：批量分析多个账户
accounts = ['88888888', '99999999', '11111111']
results = await asyncio.gather(
    *[coordinator.process_request(f"分析账户 {acc}") for acc in accounts]
)
```

### 2. 结果缓存

```python
# 对相同账户的分析结果进行缓存
@cache(ttl=3600)
async def analyze_account(account_id):
    return await coordinator.process_request(f"分析账户 {account_id}")
```

### 3. 错误处理

```python
try:
    result = await coordinator.process_request(query)
except TimeoutError:
    logger.error("分析超时")
    result = {'error': 'TIMEOUT', 'message': '分析超时，请稍后重试'}
except Exception as e:
    logger.exception(f"分析失败：{e}")
    result = {'error': 'UNKNOWN', 'message': str(e)}
```

---

## 🐛 常见问题

### Q1: 风险评分为什么是 87 分？

**A**: 风险评分基于检测到的异常模式加权计算：
- 结构化交易：+15 分
- 跨境异常：+15 分
- 资金回流：+30 分
- 频繁交易：+8 分
- 异常数量加成：+19 分
- **总计**: 87 分

### Q2: 如何调整阈值？

**A**: 在 `risk_detector.py` 的 `__init__` 方法中修改 `thresholds` 字典。

### Q3: SAR 报告如何提交给人行？

**A**: 当前生成 SAR 报告草稿，需要人工复核后通过人行反洗钱系统提交。

### Q4: 能处理多少笔交易？

**A**: 单次分析支持约 1000 笔交易，更大规模建议分批处理。

---

## 📚 扩展阅读

- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构设计
- [DEMO.md](DEMO.md) - 完整演示脚本
- [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) - 技术总结

---

## 🎯 下一步

1. **运行 Demo**: `python demo.py --scenario cross_border`
2. **查看报告**: `open reports/SAR-20260303-888888.pdf`
3. **自定义配置**: 修改阈值和权重
4. **集成测试**: 连接真实数据源测试

---

**FinGuard AI - 智能风控，从对话到执行** 🚀