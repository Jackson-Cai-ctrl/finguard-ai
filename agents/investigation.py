# Investigation Agent - 深度调查智能体

## 核心代码实现

```python
class InvestigationAgent:
    """
    金融风控深度调查智能体
    负责追踪资金流向、分析关联账户网络、识别洗钱模式
    """
    
    def __init__(self):
        self.max_depth = 5  # 最大追踪层级
        self.suspicious_patterns = self._load_suspicious_patterns()
    
    async def execute(self, action: str, payload: dict) -> dict:
        """
        执行调查任务
        """
        if action == 'trace_funds':
            return await self.trace_fund_flow(payload)
        elif action == 'analyze_network':
            return await self.analyze_account_network(payload)
        elif action == 'detect_pattern':
            return await self.detect_laundry_pattern(payload)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def trace_fund_flow(self, payload: dict) -> dict:
        """
        追踪资金流向链路
        使用 BFS/DFS 算法追踪多层资金转移
        """
        account_id = payload['account_id']
        start_transactions = payload['transactions']
        
        # 构建资金流向图
        fund_flow_graph = self._build_fund_flow_graph(start_transactions)
        
        # BFS 追踪资金流向（最多 5 层）
        flow_paths = self._trace_bfs(account_id, fund_flow_graph, max_depth=self.max_depth)
        
        # 识别可疑路径
        suspicious_paths = self._identify_suspicious_paths(flow_paths)
        
        # 生成资金流向报告
        report = {
            'source_account': account_id,
            'total_paths': len(flow_paths),
            'suspicious_paths': len(suspicious_paths),
            'flow_paths': flow_paths[:10],  # 限制返回数量
            'suspicious_details': suspicious_paths,
            'ultimate_destinations': self._find_ultimate_destinations(flow_paths),
            'risk_indicators': self._extract_risk_indicators(suspicious_paths)
        }
        
        return report
    
    def _build_fund_flow_graph(self, transactions: list) -> dict:
        """
        构建资金流向图（邻接表表示）
        """
        graph = {}
        
        for tx in transactions:
            source = tx['from_account']
            target = tx['to_account']
            amount = tx['amount']
            
            if source not in graph:
                graph[source] = []
            
            graph[source].append({
                'to': target,
                'amount': amount,
                'timestamp': tx['timestamp'],
                'tx_id': tx['id']
            })
        
        return graph
    
    def _trace_bfs(self, start_account: str, graph: dict, max_depth: int) -> list:
        """
        使用 BFS 算法追踪资金流向
        """
        from collections import deque
        
        paths = []
        queue = deque([(start_account, [start_account], 0)])  # (当前账户，路径，深度)
        visited = set()
        
        while queue:
            current, path, depth = queue.popleft()
            
            if depth >= max_depth:
                paths.append(path)
                continue
            
            if current in visited:
                continue
            visited.add(current)
            
            if current not in graph:
                paths.append(path)
                continue
            
            for edge in graph[current]:
                next_account = edge['to']
                new_path = path + [next_account]
                queue.append((next_account, new_path, depth + 1))
        
        return paths
    
    def _identify_suspicious_paths(self, paths: list) -> list:
        """
        识别可疑资金路径
        使用 ToT (Tree of Thoughts) 多路径推理
        """
        suspicious = []
        
        for path in paths:
            risk_score = 0
            risk_reasons = []
            
            # 规则 1: 路径长度异常（>4 层）
            if len(path) > 4:
                risk_score += 20
                risk_reasons.append(f"资金转移层级过深 ({len(path)}层)")
            
            # 规则 2: 路径中存在离岸账户
            offshore_accounts = [acc for acc in path if self._is_offshore_account(acc)]
            if offshore_accounts:
                risk_score += 25
                risk_reasons.append(f"涉及离岸账户: {offshore_accounts}")
            
            # 规则 3: 资金回流（路径中出现重复账户）
            if len(path) != len(set(path)):
                risk_score += 30
                risk_reasons.append("资金循环回流嫌疑")
            
            # 规则 4: 路径终点为高风险司法管辖区
            high_risk_jurisdictions = ['KY', 'BVI', 'Panama', 'Seychelles']
            for acc in path:
                if self._get_jurisdiction(acc) in high_risk_jurisdictions:
                    risk_score += 20
                    risk_reasons.append(f"涉及高风险司法管辖区: {acc}")
                    break
            
            if risk_score >= 30:
                suspicious.append({
                    'path': path,
                    'risk_score': risk_score,
                    'risk_reasons': risk_reasons,
                    'length': len(path)
                })
        
        return sorted(suspicious, key=lambda x: x['risk_score'], reverse=True)
    
    async def analyze_account_network(self, payload: dict) -> dict:
        """
        分析关联账户网络
        识别资金聚集、分散、循环等模式
        """
        target_account = payload['account_id']
        transactions = payload['transactions']
        
        # 构建关联网络
        network = self._build_account_network(transactions)
        
        # 计算网络指标
        network_metrics = self._calculate_network_metrics(network, target_account)
        
        # 识别网络模式
        network_pattern = self._identify_network_pattern(network, network_metrics)
        
        # 检测中心节点（疑似控制人）
        hub_accounts = self._find_hub_accounts(network)
        
        # 检测孤立子图（疑似独立洗钱网络）
        isolated_clusters = self._find_isolated_clusters(network)
        
        return {
            'target_account': target_account,
            'network_size': len(network['nodes']),
            'transaction_count': len(network['edges']),
            'network_metrics': network_metrics,
            'pattern': network_pattern,
            'hub_accounts': hub_accounts,
            'isolated_clusters': isolated_clusters,
            'visualization_data': self._generate_network_viz(network)
        }
    
    def _build_account_network(self, transactions: list) -> dict:
        """
        构建账户关联网络
        """
        nodes = set()
        edges = []
        
        for tx in transactions:
            nodes.add(tx['from_account'])
            nodes.add(tx['to_account'])
            edges.append({
                'source': tx['from_account'],
                'target': tx['to_account'],
                'weight': tx['amount'],
                'count': 1
            })
        
        # 合并重复边
        edge_map = {}
        for edge in edges:
            key = (edge['source'], edge['target'])
            if key in edge_map:
                edge_map[key]['weight'] += edge['weight']
                edge_map[key]['count'] += 1
            else:
                edge_map[key] = edge
        
        return {
            'nodes': list(nodes),
            'edges': list(edge_map.values())
        }
    
    def _calculate_network_metrics(self, network: dict, target: str) -> dict:
        """
        计算网络中心性指标
        """
        # 度中心性（直接关联账户数）
        degree centrality = self._calculate_degree_centrality(network, target)
        
        # 介数中心性（在网络中的桥梁作用）
        betweenness = self._calculate_betweenness(network, target)
        
        # 接近中心性（与其他账户的平均距离）
        closeness = self._calculate_closeness(network, target)
        
        # 页面排名（重要性评分）
        pagerank = self._calculate_pagerank(network, target)
        
        return {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness,
            'closeness_centrality': closeness,
            'pagerank_score': pagerank,
            'network_density': len(network['edges']) / (len(network['nodes']) ** 2)
        }
    
    def _identify_network_pattern(self, network: dict, metrics: dict) -> str:
        """
        识别网络模式类型
        """
        pattern = 'NORMAL'
        
        # 模式 1: 星型网络（中心化）
        if metrics['degree_centrality'] > 0.7:
            pattern = 'STAR_NETWORK'  # 疑似资金池
        
        # 模式 2: 链式网络（线性转移）
        if metrics['betweenness_centrality'] > 0.6 and metrics['degree_centrality'] < 0.3:
            pattern = 'CHAIN_NETWORK'  # 疑似分层转移
        
        # 模式 3: 密集网络（复杂交易）
        if metrics['network_density'] > 0.5:
            pattern = 'MESH_NETWORK'  # 疑似复杂洗钱网络
        
        # 模式 4: 分散转入集中转出
        in_degree = self._calculate_in_degree(network, metrics['target'])
        out_degree = self._calculate_out_degree(network, metrics['target'])
        if in_degree > out_degree * 3:
            pattern = 'CONCENTRATED_INFLOW'
        elif out_degree > in_degree * 3:
            pattern = 'CONCENTRATED_OUTFLOW'
        
        return pattern
    
    async def detect_laundry_pattern(self, payload: dict) -> dict:
        """
        检测具体洗钱模式
        """
        transactions = payload['transactions']
        
        detected_patterns = []
        
        # 检测结构化交易（Smurfing）
        structuring = self._detect_structuring(transactions)
        if structuring:
            detected_patterns.append(structuring)
        
        # 检测分层转移（Layering）
        layering = self._detect_layering(transactions)
        if layering:
            detected_patterns.append(layering)
        
        # 检测资金往返（Round Tripping）
        round_trip = self._detect_round_tripping(transactions)
        if round_trip:
            detected_patterns.append(round_trip)
        
        # 检测贸易洗钱（TBML）
        tbml = self._detect_trade_based_laundry(transactions)
        if tbml:
            detected_patterns.append(tbml)
        
        return {
            'patterns_detected': len(detected_patterns),
            'patterns': detected_patterns,
            'overall_risk': 'HIGH' if len(detected_patterns) >= 2 else 'MEDIUM' if len(detected_patterns) == 1 else 'LOW'
        }
    
    def _detect_structuring(self, transactions: list) -> dict:
        """
        检测结构化交易（拆分交易规避报告）
        """
        # 检测接近报告阈值（5 万）的交易
        threshold = 50000
        suspicious_range = (45000, 50000)
        
        structuring_txs = [
            tx for tx in transactions
            if suspicious_range[0] <= tx['amount'] <= suspicious_range[1]
        ]
        
        if len(structuring_txs) >= 3:
            return {
                'pattern': 'STRUCTURING',
                'confidence': 'HIGH',
                'evidence': {
                    'count': len(structuring_txs),
                    'total_amount': sum(tx['amount'] for tx in structuring_txs),
                    'time_span': self._calculate_time_span(structuring_txs),
                    'transactions': [tx['id'] for tx in structuring_txs[:5]]
                },
                'description': "检测到多笔接近 5 万阈值的交易，疑似结构化拆分规避报告"
            }
        return None
    
    def _detect_layering(self, transactions: list) -> dict:
        """
        检测分层转移（多层资金转移）
        """
        # 构建资金流向图并检测深度
        graph = self._build_fund_flow_graph(transactions)
        
        # 检测 3 层以上的转移
        deep_paths = []
        for source in graph:
            paths = self._trace_bfs(source, graph, max_depth=5)
            for path in paths:
                if len(path) >= 4:
                    deep_paths.append(path)
        
        if len(deep_paths) >= 2:
            return {
                'pattern': 'LAYERING',
                'confidence': 'MEDIUM',
                'evidence': {
                    'deep_paths_count': len(deep_paths),
                    'max_depth': max(len(p) for p in deep_paths),
                    'sample_paths': deep_paths[:3]
                },
                'description': "检测到多层资金转移，疑似分层洗钱"
            }
        return None
    
    def _detect_round_tripping(self, transactions: list) -> dict:
        """
        检测资金往返（出境后回流）
        """
        # 检测跨境转出后短期内回流
        outbound = [tx for tx in transactions if tx.get('is_cross_border', False) and tx['direction'] == 'out']
        inbound = [tx for tx in transactions if tx.get('is_cross_border', False) and tx['direction'] == 'in']
        
        round_trips = []
        for out_tx in outbound:
            for in_tx in inbound:
                # 检查金额相近且时间间隔<30 天
                amount_diff = abs(out_tx['amount'] - in_tx['amount']) / out_tx['amount']
                time_diff = (in_tx['timestamp'] - out_tx['timestamp']).days
                
                if amount_diff < 0.2 and 0 < time_diff < 30:
                    round_trips.append({
                        'outbound': out_tx['id'],
                        'inbound': in_tx['id'],
                        'amount': out_tx['amount'],
                        'days_gap': time_diff
                    })
        
        if round_trips:
            return {
                'pattern': 'ROUND_TRIPPING',
                'confidence': 'HIGH',
                'evidence': {
                    'count': len(round_trips),
                    'total_amount': sum(rt['amount'] for rt in round_trips),
                    'details': round_trips[:5]
                },
                'description': "检测到资金出境后短期内回流，疑似伪装外资"
            }
        return None
    
    def _detect_trade_based_laundry(self, transactions: list) -> dict:
        """
        检测贸易洗钱（虚高/虚低报价）
        """
        # 检测与贸易相关的异常交易
        trade_txs = [tx for tx in transactions if tx.get('type') == 'trade']
        
        if not trade_txs:
            return None
        
        # 检测价格异常（与市场价偏差>30%）
        overpriced = [
            tx for tx in trade_txs
            if tx.get('price_deviation', 0) > 0.3
        ]
        
        if len(overpriced) >= 2:
            return {
                'pattern': 'TRADE_BASED_LAUNDERING',
                'confidence': 'MEDIUM',
                'evidence': {
                    'count': len(overpriced),
                    'total_value': sum(tx['amount'] for tx in overpriced),
                    'avg_deviation': sum(tx['price_deviation'] for tx in overpriced) / len(overpriced)
                },
                'description': "检测到贸易报价异常，疑似通过虚高/虚低报价洗钱"
            }
        return None
```

## 调查输出示例

```json
{
  "investigation_id": "inv_20260303_001",
  "target_account": "88888888",
  "fund_flow_analysis": {
    "total_paths": 15,
    "suspicious_paths": 3,
    "ultimate_destinations": [
      {"account": "KY_12345", "jurisdiction": "Cayman Islands", "risk": "HIGH"},
      {"account": "BVI_67890", "jurisdiction": "British Virgin Islands", "risk": "HIGH"}
    ]
  },
  "network_analysis": {
    "network_size": 47,
    "pattern": "STAR_NETWORK",
    "hub_accounts": ["88888888", "99999999"],
    "centrality_score": 0.82
  },
  "detected_patterns": [
    {
      "pattern": "STRUCTURING",
      "confidence": "HIGH",
      "description": "检测到 5 笔 49000-50000 元交易"
    },
    {
      "pattern": "ROUND_TRIPPING",
      "confidence": "HIGH", 
      "description": "检测到 2 笔资金往返"
    }
  ],
  "overall_risk_score": 87,
  "recommendation": "FREEZE_ACCOUNT_AND_REPORT"
}
```