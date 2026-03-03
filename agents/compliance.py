# Compliance Agent - 合规检查智能体

## 核心代码实现

```python
class ComplianceAgent:
    """
    金融风控合规检查智能体
    负责 AML/KYC 规则检查、监管报告生成、审计日志记录
    """
    
    def __init__(self):
        self.aml_rules = self._load_aml_rules()
        self.kyc_requirements = self._load_kyc_requirements()
        self.report_templates = self._load_report_templates()
    
    async def execute(self, action: str, payload: dict) -> dict:
        """
        执行合规检查任务
        """
        if action == 'check_aml_violations':
            return await self.check_aml_violations(payload)
        elif action == 'verify_kyc':
            return await self.verify_kyc_status(payload)
        elif action == 'generate_sar_report':
            return await self.generate_suspicious_activity_report(payload)
        elif action == 'audit_trail':
            return await self.generate_audit_trail(payload)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def check_aml_violations(self, payload: dict) -> dict:
        """
        检查反洗钱规则违反
        """
        account_id = payload['account_id']
        transactions = payload['transactions']
        customer_info = payload.get('customer_info', {})
        
        violations = []
        
        # 规则 1: 大额交易报告 (CTR) 阈值检查
        ctr_violations = self._check_ctr_violations(transactions)
        if ctr_violations:
            violations.extend(ctr_violations)
        
        # 规则 2: 可疑交易模式检查
        sar_triggers = self._check_sar_triggers(transactions)
        if sar_triggers:
            violations.extend(sar_triggers)
        
        # 规则 3: 制裁名单匹配
        sanction_matches = await self._check_sanctions_list(customer_info)
        if sanction_matches:
            violations.extend(sanction_matches)
        
        # 规则 4: PEP (政治公众人物) 检查
        pep_match = await self._check_pep_status(customer_info)
        if pep_match:
            violations.append({
                'type': 'PEP_MATCH',
                'severity': 'HIGH',
                'details': pep_match,
                'regulation': 'AML-KYC-PEP-001',
                'action': 'ENHANCED_DUE_DILIGENCE'
            })
        
        # 规则 5: 高风险国家/地区交易
        high_risk_country = self._check_high_risk_jurisdictions(transactions)
        if high_risk_country:
            violations.append({
                'type': 'HIGH_RISK_JURISDICTION',
                'severity': 'MEDIUM',
                'details': high_risk_country,
                'regulation': 'AML-GEO-001',
                'action': 'ENHANCED_MONITORING'
            })
        
        # 计算违规评分
        violation_score = self._calculate_violation_score(violations)
        
        return {
            'account_id': account_id,
            'violation_count': len(violations),
            'violation_score': violation_score,
            'violations': violations,
            'requires_sar': violation_score >= 50,
            'requires_ctr': any(v['type'] == 'CTR_THRESHOLD' for v in violations),
            'recommended_actions': self._generate_compliance_actions(violations)
        }
    
    def _check_ctr_violations(self, transactions: list) -> list:
        """
        检查大额交易报告 (Currency Transaction Report) 阈值
        中国规定：单笔或当日累计 5 万元以上
        """
        violations = []
        
        # 检查单笔大额
        large_single_txs = [tx for tx in transactions if tx['amount'] >= 50000]
        for tx in large_single_txs:
            violations.append({
                'type': 'CTR_THRESHOLD',
                'severity': 'MEDIUM',
                'transaction_id': tx['id'],
                'amount': tx['amount'],
                'regulation': 'PBOC-CTR-2026',
                'description': f"单笔交易 {tx['amount']:.2f} 元，达到 CTR 报告阈值",
                'action': 'FILE_CTR'
            })
        
        # 检查当日累计
        daily_totals = self._group_by_date(transactions)
        for date, txs in daily_totals.items():
            daily_sum = sum(tx['amount'] for tx in txs)
            if daily_sum >= 50000:
                violations.append({
                    'type': 'CTR_CUMULATIVE',
                    'severity': 'MEDIUM',
                    'date': date,
                    'total_amount': daily_sum,
                    'transaction_count': len(txs),
                    'regulation': 'PBOC-CTR-2026',
                    'description': f"当日累计交易 {daily_sum:.2f} 元，达到 CTR 报告阈值",
                    'action': 'FILE_CTR'
                })
        
        return violations
    
    def _check_sar_triggers(self, transactions: list) -> list:
        """
        检查可疑交易报告 (Suspicious Activity Report) 触发条件
        """
        violations = []
        
        # 触发条件 1: 结构化交易规避报告
        structuring = self._detect_structuring_for_sar(transactions)
        if structuring:
            violations.append({
                'type': 'SAR_STRUCTURING',
                'severity': 'HIGH',
                'details': structuring,
                'regulation': 'PBOC-SAR-001',
                'description': "检测到结构化交易模式，疑似规避 CTR 报告",
                'action': 'FILE_SAR'
            })
        
        # 触发条件 2: 与客户身份/业务不符的交易
        unusual_pattern = self._detect_unusual_pattern(transactions)
        if unusual_pattern:
            violations.append({
                'type': 'SAR_UNUSUAL_PATTERN',
                'severity': 'HIGH',
                'details': unusual_pattern,
                'regulation': 'PBOC-SAR-002',
                'description': "交易模式与客户身份/业务明显不符",
                'action': 'FILE_SAR'
            })
        
        # 触发条件 3: 无明确商业目的的复杂交易
        complex_no_purpose = self._detect_complex_no_purpose(transactions)
        if complex_no_purpose:
            violations.append({
                'type': 'SAR_COMPLEX_NO_PURPOSE',
                'severity': 'MEDIUM',
                'details': complex_no_purpose,
                'regulation': 'PBOC-SAR-003',
                'description': "复杂交易无明显商业目的",
                'action': 'FILE_SAR'
            })
        
        # 触发条件 4: 频繁跨境转移
        frequent_cross_border = self._detect_frequent_cross_border(transactions)
        if frequent_cross_border:
            violations.append({
                'type': 'SAR_FREQUENT_CROSS_BORDER',
                'severity': 'HIGH',
                'details': frequent_cross_border,
                'regulation': 'PBOC-SAR-004',
                'description': "频繁跨境资金转移，疑似洗钱",
                'action': 'FILE_SAR'
            })
        
        return violations
    
    async def _check_sanctions_list(self, customer_info: dict) -> list:
        """
        检查制裁名单匹配
        对接 UN、OFAC、中国公安部等制裁名单
        """
        violations = []
        
        name = customer_info.get('name', '')
        id_number = customer_info.get('id_number', '')
        
        # 模拟制裁名单检查（实际应调用 API）
        sanctions_lists = ['UN', 'OFAC', 'CHINA_MPS', 'EU']
        
        # 这里简化处理，实际应调用外部 API
        # 如果命中制裁名单
        if self._is_sanctioned(name, id_number):
            violations.append({
                'type': 'SANCTIONS_MATCH',
                'severity': 'CRITICAL',
                'lists_matched': ['UN', 'OFAC'],  # 示例
                'regulation': 'INTERNATIONAL_SANCTIONS',
                'description': "客户命中国际制裁名单",
                'action': 'FREEZE_AND_REPORT'
            })
        
        return violations
    
    async def _check_pep_status(self, customer_info: dict) -> dict:
        """
        检查 PEP (政治公众人物) 状态
        """
        name = customer_info.get('name', '')
        position = customer_info.get('position', '')
        
        # PEP 类别
        pep_categories = {
            'HEAD_OF_STATE': '国家元首、政府首脑',
            'SENIOR_OFFICIAL': '高级政府官员',
            'JUDICIAL': '高级司法官员',
            'MILITARY': '高级军官',
            'SOE_EXECUTIVE': '国企高管',
            'POLITICAL_PARTY': '政党高级成员',
            'FAMILY_MEMBER': '上述人员家庭成员',
            'CLOSE_ASSOCIATE': '上述人员密切关系人'
        }
        
        # 检查是否匹配 PEP
        if self._is_pep(name, position):
            category = self._determine_pep_category(position)
            return {
                'is_pep': True,
                'category': category,
                'position': position,
                'risk_level': 'HIGH' if category in ['HEAD_OF_STATE', 'SENIOR_OFFICIAL'] else 'MEDIUM',
                'edd_required': True
            }
        
        return None
    
    async def verify_kyc_status(self, payload: dict) -> dict:
        """
        验证 KYC 状态
        """
        customer_id = payload['customer_id']
        
        # 检查 KYC 完整性
        kyc_status = await self._get_kyc_status(customer_id)
        
        missing_items = []
        required_items = [
            'identity_document',
            'address_proof',
            'source_of_funds',
            'occupation',
            'expected_transaction_volume'
        ]
        
        for item in required_items:
            if item not in kyc_status or not kyc_status[item]:
                missing_items.append(item)
        
        # KYC 等级判定
        kyc_level = 'COMPLETE' if not missing_items else 'INCOMPLETE'
        
        # 风险等级评估
        risk_level = self._assess_kyc_risk(kyc_status)
        
        return {
            'customer_id': customer_id,
            'kyc_level': kyc_level,
            'kyc_status': kyc_status,
            'missing_items': missing_items,
            'risk_level': risk_level,
            'edd_required': risk_level == 'HIGH',
            'recommended_actions': self._generate_kyc_actions(missing_items, risk_level)
        }
    
    async def generate_suspicious_activity_report(self, payload: dict) -> dict:
        """
        生成可疑活动报告 (SAR - Suspicious Activity Report)
        符合中国人民银行格式要求
        """
        account_id = payload['account_id']
        violations = payload['violations']
        investigation_results = payload.get('investigation_results', {})
        
        # SAR 报告编号
        sar_id = f"SAR-{datetime.now().strftime('%Y%m%d')}-{account_id[-6:]}"
        
        # 构建 SAR 报告
        sar_report = {
            'report_id': sar_id,
            'report_date': datetime.now().isoformat(),
            'reporting_institution': 'XX 银行',
            'subject_information': {
                'account_id': account_id,
                'customer_name': payload.get('customer_name', 'N/A'),
                'id_type': payload.get('id_type', 'N/A'),
                'id_number': payload.get('id_number', 'N/A'),
                'contact_info': payload.get('contact_info', 'N/A')
            },
            'suspicious_activity': {
                'activity_type': self._classify_activity_type(violations),
                'date_range': {
                    'start': payload.get('start_date', 'N/A'),
                    'end': payload.get('end_date', 'N/A')
                },
                'total_amount': payload.get('total_amount', 0),
                'transaction_count': payload.get('transaction_count', 0),
                'description': self._generate_activity_description(violations, investigation_results)
            },
            'violations_summary': [
                {
                    'type': v['type'],
                    'severity': v['severity'],
                    'regulation': v.get('regulation', 'N/A')
                }
                for v in violations
            ],
            'supporting_evidence': {
                'transaction_ids': payload.get('transaction_ids', []),
                'investigation_findings': investigation_results.get('findings', []),
                'network_analysis': investigation_results.get('network', {}),
                'fund_flow_paths': investigation_results.get('fund_flow', [])
            },
            'recommended_action': payload.get('recommended_action', 'INVESTIGATE'),
            'prepared_by': 'FinGuard AI System',
            'review_status': 'PENDING_MANUAL_REVIEW'
        }
        
        # 生成 PDF 报告（模拟）
        pdf_url = await self._generate_pdf_report(sar_report)
        
        return {
            'sar_id': sar_id,
            'status': 'GENERATED',
            'report': sar_report,
            'pdf_url': pdf_url,
            'submitted_to_pboC': False,
            'next_steps': [
                '人工复核 SAR 报告内容',
                '补充必要证据材料',
                '提交中国人民银行反洗钱监测分析中心',
                '保存报告副本（至少 5 年）'
            ]
        }
    
    async def generate_audit_trail(self, payload: dict) -> dict:
        """
        生成审计日志
        满足监管审计要求
        """
        audit_entries = []
        
        # 记录所有风控操作
        operations = payload.get('operations', [])
        
        for op in operations:
            audit_entries.append({
                'timestamp': op['timestamp'],
                'operation': op['type'],
                'operator': op.get('operator', 'SYSTEM'),
                'target': op.get('target', 'N/A'),
                'result': op.get('result', 'N/A'),
                'ip_address': op.get('ip', 'N/A'),
                'session_id': op.get('session_id', 'N/A')
            })
        
        return {
            'audit_id': f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'entry_count': len(audit_entries),
            'entries': audit_entries,
            'integrity_hash': self._calculate_hash(audit_entries),
            'retention_period': '5 years',
            'compliance_standard': 'PBOC-AML-2026'
        }
    
    def _calculate_violation_score(self, violations: list) -> int:
        """
        计算违规评分 (0-100)
        """
        severity_weights = {
            'CRITICAL': 40,
            'HIGH': 20,
            'MEDIUM': 10,
            'LOW': 5
        }
        
        score = sum(severity_weights.get(v['severity'], 0) for v in violations)
        return min(score, 100)
    
    def _generate_compliance_actions(self, violations: list) -> list:
        """
        生成合规行动建议
        """
        actions = []
        
        has_critical = any(v['severity'] == 'CRITICAL' for v in violations)
        has_high = any(v['severity'] == 'HIGH' for v in violations)
        
        if has_critical:
            actions.append({
                'action': 'IMMEDIATE_FREEZE',
                'priority': 'CRITICAL',
                'description': '立即冻结账户并上报'
            })
        
        if has_high:
            actions.append({
                'action': 'FILE_SAR',
                'priority': 'HIGH',
                'description': '提交可疑活动报告',
                'deadline': '5 working days'
            })
        
        ctr_required = any(v['type'] == 'CTR_THRESHOLD' for v in violations)
        if ctr_required:
            actions.append({
                'action': 'FILE_CTR',
                'priority': 'MEDIUM',
                'description': '提交大额交易报告',
                'deadline': '5 working days'
            })
        
        if not actions:
            actions.append({
                'action': 'CONTINUE_MONITORING',
                'priority': 'LOW',
                'description': '继续常规监控'
            })
        
        return actions
```

## AML 规则清单

```python
AML_RULES = {
    'CTR-001': {
        'name': '大额交易报告',
        'threshold': 50000,  # 人民币
        'regulation': 'PBOC-CTR-2026',
        'action': 'FILE_CTR',
        'deadline': '5 working days'
    },
    'SAR-001': {
        'name': '可疑交易报告',
        'triggers': [
            '结构化交易',
            '与客户身份不符',
            '无明确商业目的',
            '频繁跨境转移'
        ],
        'regulation': 'PBOC-SAR-2026',
        'action': 'FILE_SAR',
        'deadline': '5 working days'
    },
    'KYC-001': {
        'name': '客户身份识别',
        'required_documents': [
            '身份证件',
            '地址证明',
            '资金来源说明'
        ],
        'regulation': 'PBOC-KYC-2026',
        'action': 'REQUEST_DOCUMENTS'
    },
    'EDD-001': {
        'name': '强化尽职调查',
        'applicable_to': [
            'PEP 客户',
            '高风险国家客户',
            '现金密集型业务'
        ],
        'regulation': 'PBOC-EDD-2026',
        'action': 'ENHANCED_DUE_DILIGENCE'
    },
    'SANCTIONS-001': {
        'name': '制裁名单筛查',
        'lists': ['UN', 'OFAC', 'CHINA_MPS', 'EU'],
        'regulation': 'INTERNATIONAL_SANCTIONS',
        'action': 'FREEZE_AND_REPORT'
    }
}
```

## SAR 报告模板

```
===========================================
    可疑活动报告 (Suspicious Activity Report)
===========================================

报告编号：SAR-20260303-888888
报告日期：2026 年 3 月 3 日
报告机构：XX 银行

【客户信息】
账户号码：88888888
客户姓名：张三
证件类型：身份证
证件号码：11010119900101XXXX

【可疑活动概述】
活动类型：疑似结构化交易 + 资金往返
时间范围：2026 年 3 月 1 日 - 2026 年 3 月 3 日
涉及金额：人民币 245,000 元
交易笔数：8 笔

【详细描述】
该账户在 3 日内发生多笔接近 5 万元阈值的交易，
疑似故意规避大额交易报告。同时检测到资金
出境后 7 天内回流，疑似伪装外资。

【违规类型】
1. SAR-STRUCTURING (HIGH) - 结构化交易
2. SAR-ROUND_TRIPPING (HIGH) - 资金往返
3. CTR-THRESHOLD (MEDIUM) - 大额交易阈值

【建议行动】
□ 提交 SAR 报告至人民银行
□ 提交 CTR 报告
□ 冻结账户
☑ 人工复核
□ 继续监控

【附件】
- 交易明细清单
- 资金流向图
- 关联账户网络分析

报告生成：FinGuard AI System
复核状态：待人工复核
===========================================
```