# RiskDetector Agent - 风险检测智能体

## 核心代码实现

```python
class RiskDetectorAgent:
    """
    金融风控风险检测智能体
    负责实时识别交易异常模式，计算风险评分
    """
    
    def __init__(self):
        self.risk_patterns = self._load_risk_patterns()
        self.thresholds = {
            'large_amount': 50000,      # 大额交易阈值
            'frequent_count': 5,         # 频繁交易次数
            'cross_border_ratio': 0.3,   # 跨境交易占比
            'velocity_window_hours': 24  # 速度监控时间窗口
        }
    
    async def execute(self, action: str, payload: dict) -> dict:
        """
        执行风险检测任务
        """
        if action == 'analyze_transaction':
            return await self.analyze_transactions(payload)
        elif action == 'monitor_account':
            return await self.monitor_account(payload)
        elif action == 'detect_pattern':
            return await self.detect洗钱_pattern(payload)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def analyze_transactions(self, payload: dict) -> dict:
        """
        分析交易数据，识别异常模式
        """
        account_id = payload['account_id']
        transactions = payload['transactions']
        
        # Step 1: 基础统计分析
        stats = self._calculate_stats(transactions)
        
        # Step 2: 异常模式检测
        anomalies = self._detect_anomalies(transactions)
        
        # Step 3: 风险评分计算
        risk_score = self._calculate_risk_score(anomalies)
        
        # Step 4: 风险等级判定
        risk_level = self._classify_risk(risk_score)
        
        return {
            'account_id': account_id,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'anomalies': anomalies,
            'statistics': stats,
            'alert_flags': self._generate_alerts(anomalies)
        }
    
    def _detect_anomalies(self, transactions: list) -> list:
        """
        检测多种异常交易模式
        使用 CoT 推理识别复杂模式
        """
        anomalies = []
        
        # 模式 1: 大额交易异常
        large_txs = [t for t in transactions if t['amount'] > self.thresholds['large_amount']]
        if len(large_txs) > 3:
            anomalies.append({
                'type': 'LARGE_AMOUNT',
                'severity': 'high',
                'count': len(large_txs),
                'total_amount': sum(t['amount'] for t in large_txs),
                'description': f"检测到 {len(large_txs)} 笔大额交易，总计 {sum(t['amount'] for t in large_txs):.2f} 元"
            })
        
        # 模式 2: 频繁交易（结构化交易/拆分交易）
        time_windows = self._group_by_time_window(transactions, hours=1)
        frequent_windows = [w for w in time_windows if len(w) >= self.thresholds['frequent_count']]
        if frequent_windows:
            anomalies.append({
                'type': 'FREQUENT_TRADING',
                'severity': 'medium',
                'windows': len(frequent_windows),
                'description': "检测到频繁交易模式，疑似结构化拆分交易"
            })
        
        # 模式 3: 跨境交易异常
        cross_border_txs = [t for t in transactions if t.get('is_cross_border', False)]
        if len(cross_border_txs) / len(transactions) > self.thresholds['cross_border_ratio']:
            anomalies.append({
                'type': 'CROSS_BORDER_ANOMALY',
                'severity': 'high',
                'count': len(cross_border_txs),
                'countries': list(set(t.get('country', 'Unknown') for t in cross_border_txs)),
                'description': "跨境交易占比异常，需关注资金外流风险"
            })
        
        # 模式 4: 快进快出（资金停留时间过短）
        velocity_anomalies = self._detect_velocity_anomaly(transactions)
        if velocity_anomalies:
            anomalies.append({
                'type': 'VELOCITY_ANOMALY',
                'severity': 'high',
                'details': velocity_anomalies,
                'description': "资金快进快出，疑似过桥转账"
            })
        
        # 模式 5: 关联账户网络异常
        network_anomalies = self._detect_network_anomaly(transactions)
        if network_anomalies:
            anomalies.append({
                'type': 'NETWORK_ANOMALY',
                'severity': 'medium',
                'details': network_anomalies,
                'description': "关联账户网络存在异常资金循环"
            })
        
        return anomalies
    
    def _calculate_risk_score(self, anomalies: list) -> int:
        """
        基于异常模式计算综合风险评分 (0-100)
        使用加权算法
        """
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 8,
            'low': 3
        }
        
        base_score = 0
        for anomaly in anomalies:
            base_score += severity_weights.get(anomaly['severity'], 0)
        
        # 异常数量加成
        count_bonus = min(len(anomalies) * 2, 10)
        
        # 综合评分 (上限 100)
        risk_score = min(base_score + count_bonus, 100)
        
        return risk_score
    
    def _classify_risk(self, score: int) -> str:
        """
        风险等级分类
        """
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _detect_velocity_anomaly(self, transactions: list) -> list:
        """
        检测资金速度异常（快进快出）
        """
        anomalies = []
        
        # 按时间排序
        sorted_txs = sorted(transactions, key=lambda x: x['timestamp'])
        
        for i in range(len(sorted_txs) - 1):
            inflow = sorted_txs[i]
            outflow = sorted_txs[i + 1]
            
            # 如果入账后短时间内（<2 小时）大额转出
            time_diff = (outflow['timestamp'] - inflow['timestamp']).total_seconds() / 3600
            if time_diff < 2 and outflow['amount'] > inflow['amount'] * 0.8:
                anomalies.append({
                    'inflow_id': inflow['id'],
                    'outflow_id': outflow['id'],
                    'time_gap_hours': round(time_diff, 2),
                    'amount_ratio': round(outflow['amount'] / inflow['amount'], 2)
                })
        
        return anomalies
    
    def _detect_network_anomaly(self, transactions: list) -> dict:
        """
        检测关联账户网络异常
        识别资金循环、分散转入集中转出等模式
        """
        # 构建资金流向图
        counterparties = {}
        for tx in transactions:
            counterparty = tx['counterparty_account']
            if counterparty not in counterparties:
                counterparties[counterparty] = {'inflow': 0, 'outflow': 0}
            
            if tx['direction'] == 'in':
                counterparties[counterparty]['inflow'] += tx['amount']
            else:
                counterparties[counterparty]['outflow'] += tx['amount']
        
        # 检测分散转入集中转出
        total_inflow = sum(c['inflow'] for c in counterparties.values())
        total_outflow = sum(c['outflow'] for c in counterparties.values())
        
        network_pattern = 'NORMAL'
        if len(counterparties) > 5:
            if total_inflow > total_outflow * 2:
                network_pattern = 'CONCENTRATED_INFLOW'  # 分散转入
            elif total_outflow > total_inflow * 2:
                network_pattern = 'CONCENTRATED_OUTFLOW'  # 集中转出
        
        return {
            'counterparty_count': len(counterparties),
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'pattern': network_pattern
        }
    
    def _generate_alerts(self, anomalies: list) -> list:
        """
        生成预警信号
        """
        alerts = []
        for anomaly in anomalies:
            if anomaly['severity'] in ['critical', 'high']:
                alerts.append({
                    'level': 'RED' if anomaly['severity'] == 'critical' else 'ORANGE',
                    'type': anomaly['type'],
                    'message': anomaly['description'],
                    'action_required': True
                })
        return alerts
```

## 典型洗钱模式识别

```python
MONEY_LAUNDERING_PATTERNS = {
    'structuring': {
        'name': '结构化交易（Smurfing）',
        'indicators': [
            '多笔略低于报告阈值的交易',
            '同一人控制多个账户',
            '短时间内频繁存款'
        ],
        'detection_logic': '检测连续多笔 49000-50000 元区间的交易'
    },
    'layering': {
        'name': '分层转移（Layering）',
        'indicators': [
            '资金在多个账户间快速转移',
            '跨境多层转账',
            '复杂的所有权结构'
        ],
        'detection_logic': '追踪资金流向图，检测 3 层以上转移'
    },
    'integration': {
        'name': '整合阶段（Integration）',
        'indicators': [
            '资金以合法形式回流',
            '购买高价值资产',
            '投资企业或房地产'
        ],
        'detection_logic': '检测大额投资与已知收入不符'
    },
    'round_tripping': {
        'name': '资金往返（Round Tripping）',
        'indicators': [
            '资金出境后短期内回流',
            '伪装成外资投资',
            '避税或洗钱目的'
        ],
        'detection_logic': '检测相同资金 30 天内往返跨境'
    }
}
```

## 风险评分卡

| 异常类型 | 基础分 | 严重程度 | 说明 |
|---------|-------|---------|------|
| 大额交易 (>5 万) | 15 | High | 单笔或累计超阈值 |
| 频繁交易 (1 小时>5 笔) | 15 | Medium | 疑似拆分交易 |
| 跨境交易占比>30% | 15 | High | 资金外流风险 |
| 快进快出 (<2 小时) | 20 | High | 过桥转账嫌疑 |
| 关联账户网络异常 | 10 | Medium | 资金循环嫌疑 |
| 命中黑名单账户 | 25 | Critical | 直接高风险 |
| 夜间异常交易 | 8 | Low | 非正常时间交易 |

**风险等级**: 
- CRITICAL (≥80): 立即冻结 + 上报监管
- HIGH (≥60): 人工复核 + 限制交易
- MEDIUM (≥40): 加强监控 + 收集信息
- LOW (≥20): 常规监控
- MINIMAL (<20): 正常交易