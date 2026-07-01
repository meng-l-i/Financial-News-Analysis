# 金融热点智能监控系统

自动化采集财联社等新闻源，通过 DeepSeek 大模型提取领域与公司、评估金融热度（0-10），前端按领域展示近 5 天热点。

## 做了什么

- **Scrapy + Playwright 爬虫**：自动抓取财联社电报，JS 渲染页面，定时增量采集
- **LangChain + DeepSeek Agent**：两条智能体管线——领域/公司提取 + 金融热度分析
- **Spring Boot 后端**：REST API（/health /login /data），JPA 持久化，HMAC 每天轮换 Token 鉴权
- **Vue 3 前端**：领域下拉列表 + 公司热点展示，登录鉴权，近 5 天筛选
- **FastAPI 调度服务**：启动→30min→1h 定时爬虫调度，爬取后自动触发 Agent 分析
- **Prometheus + Grafana 监控**：后端 JVM / 主机 CPU 内存磁盘 / MySQL 状态全覆盖
- **Docker Compose 一键部署**：11 个服务编排，Kubernetes 配置同步提供

## 项目架构

```
前端 (Vue 3 :3001)
  │  /api → nginx proxy
  ▼
后端 (Spring Boot :5070)
  │  JPA → MySQL
  ▼
MySQL (:3306) ←── Agent 写入
  ▲
爬虫 (FastAPI :5080)
  │  Scrapy + Playwright → 新闻数据
  │  LangChain + DeepSeek → 领域/公司/热度
  └─→ 入库 (t_field / t_company / t_news)

监控 (Prometheus :9090 + Grafana :3000)
  ├─ Spring Boot Micrometer :5071
  ├─ node_exporter ×3
  └─ mysqld_exporter
```

## 快速开始

### 1. 克隆后必填的隐私配置

| 文件 | 字段 | 说明 |
|------|------|------|
| `main/crawler/conf/agent.json` | `api_key` | DeepSeek API key（参考 `agent.example.json`） |

### 2. Docker Compose 一键部署

```bash
cd run
docker compose up -d --build
```

首次启动需确保数据目录权限：
```bash
sudo chown -R 65534:65534 data/prometheus
sudo chown -R 472:472 data/grafana
mkdir -p data/mysql main/crawler/output main/crawler/logs
```

对外端口：

| 服务 | 端口 | 说明 |
|------|------|------|
| Frontend | 3001 | Vue 界面 |
| Grafana | 3000 | 监控面板（admin/admin） |

## 后续改进方向

- [ ] 兼容更多的新闻网站。当前已经有接口，但未调试爬取方案
- [ ] 更有效、更丰富的 agent 结合策略。在该项目中 agent 只是用于独立分析热度和提取新闻信息，更多是用于个人学习。agent 的提示词相当简陋，分析热度也没有合理的数据支撑。后续需要从结合历史新闻入手构建评价体系。
- [ ] 更健壮的项目体系。由于开发经验、开发时间不足，许多代码解耦、结构分层、配置分离等架构工作都没有完善。
