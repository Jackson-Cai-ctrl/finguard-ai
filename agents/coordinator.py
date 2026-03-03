# Coordinator Agent - 协调器智能体

## 核心代码实现

```python
class CoordinatorAgent:
    """
    金融风控多智能体系统的协调器
    负责任务分解、智能体调度、结果汇总
    """
    
    def __init__(self):
        self.agents = {
            'risk_detector': RiskDetectorAgent(),
            'investigation': InvestigationAgent(),
            'compliance': ComplianceAgent()
        }
        self.context = []
        
    async def process_request(self, user_query: str):
        """
        处理用户请求的主流程
        """
        # Step 1: 意图识别
        intent = self._analyze_intent(user_query)
        
        # Step 2: 任务分解
        tasks = self._decompose_tasks(intent)
        
        # Step 3: 并行执行子任务
        results = await self._execute_parallel(tasks)
        
        # Step 4: 结果汇总
        final_report = self._synthesize_results(results)
        
        # Step 5: 决策建议
        recommendations = self._generate_recommendations(final_report)
        
        return {
            'report': final_report,
            'recommendations': recommendations,
            'risk_level': final_report['overall_risk_score']
        }
    
    def _analyze_intent(self, query: str) -> dict:
        """
        分析用户意图
        使用 CoT (Chain of Thought) 推理
        """
        # 思考过程：
        # 1. 识别查询类型（账户分析/交易监控/合规检查）
        # 2. 提取关键实体（账户 ID、时间范围、金额阈值）
        # 3. 判断紧急程度
        
        return {
            'type': 'account_analysis',  # 或 transaction_monitoring
            'entities': self._extract_entities(query),
            'urgency': self._assess_urgency(query)
        }
    
    async def _execute_parallel(self, tasks: list) -> dict:
        """
        并行执行多个子任务
        使用 MCP 协议与子智能体通信
        """
        import asyncio
        
        coroutines = []
        for task in tasks:
            agent = self.agents[task['agent']]
            coroutines.append(agent.execute(task['action'], task['payload']))
        
        results = await asyncio.gather(*coroutines)
        return dict(zip([t['agent'] for t in tasks], results))
    
    def _synthesize_results(self, results: dict) -> dict:
        """
        汇总各智能体的结果
        使用 ToT (Tree of Thoughts) 进行多路径推理
        """
        # 综合风险评估
        risk_scores = [
            results['risk_detector']['score'],
            results['investigation']['risk_score'],
            results['compliance']['violation_score']
        ]
        
        overall_score = self._weighted_average(risk_scores)
        
        return {
            'overall_risk_score': overall_score,
            'risk_breakdown': results,
            'evidence_chain': self._build_evidence_chain(results),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, report: dict) -> list:
        """
        基于风险评估生成行动建议
        """
        recommendations = []
        
        if report['overall_risk_score'] >= 80:
            recommendations.append({
                'action': 'FREEZE_ACCOUNT',
                'reason': '高风险评分，建议立即冻结账户',
                'priority': 'critical'
            })
            recommendations.append({
                'action': 'GENERATE_REPORT',
                'reason': '生成反洗钱监管报告',
                'priority': 'high'
            })
        elif report['overall_risk_score'] >= 50:
            recommendations.append({
                'action': 'MANUAL_REVIEW',
                'reason': '中等风险，建议人工复核',
                'priority': 'medium'
            })
        else:
            recommendations.append({
                'action': 'CONTINUE_MONITORING',
                'reason': '低风险，继续常规监控',
                'priority': 'low'
            })
        
        return recommendations
```

## MCP 消息格式

```json
{
  "message_id": "msg_001",
  "from": "coordinator",
  "to": "risk_detector",
  "action": "analyze_transaction",
  "payload": {
    "account_id": "88888888",
    "transaction_ids": ["tx_001", "tx_002", "tx_003"],
    "time_range": "2026-03-01 to 2026-03-03",
    "threshold": 50000
  },
  "priority": "high",
  "timeout_ms": 30000,
  "callback": "coordinator/results"
}
```

## ReAct 推理示例

```
用户查询: "分析账户 88888888 的最近 5 笔大额转账"

Thought: 这是一个账户分析请求，需要检测交易风险、调查资金流向、检查合规性
Action: 分解为 3 个子任务
  - risk_detector: 分析交易异常模式
  - investigation: 追踪资金流向
  - compliance: 检查 AML 规则

Observation: 收到 3 个智能体的返回结果

Thought: 综合评估风险评分为 87/100，属于高风险
Action: 生成冻结账户建议 + 监管报告

Final Response: 
{
  "risk_score": 87,
  "recommendations": ["FREEZE_ACCOUNT", "GENERATE_SAR_REPORT"],
  "evidence": [...]
}
```