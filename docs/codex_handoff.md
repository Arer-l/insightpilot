# Codex 上下文交接文档

## 当前总目标

构建一个用于 AI 应用开发工程师面试展示的项目：`InsightPilot`，定位为“电商经营数据分析与归因 Agent 平台”。

项目最终希望实现：

- 用户通过自然语言提出经营数据问题。
- 系统识别意图，生成或选择合适的 SQL/分析工具。
- 查询 PostgreSQL 中的业务数据。
- 完成 GMV、订单量、渠道、品类、城市等分析。
- 输出结构化结果和自然语言解释。
- 后续继续扩展为 LLM 驱动的 Text-to-SQL Agent、Skills、MCP 工具服务和前端 Dashboard。

当前阶段已经完成基础后端、数据库、分析工具和首版规则 Agent。下一阶段建议接入真实大模型，让 LLM 替代规则意图识别和 SQL 生成。

## 我的长期偏好

- 希望从 0 开始逐步搭建项目，并理解每一步为什么这样做。
- 希望项目适合 AI 应用开发工程师面试，而不是只做简单 demo。
- 偏好工程化、可解释、可落地的方案。
- 希望项目覆盖 Agent、Tools、Skills、MCP、SQL、Python 后端、数据分析等主流技术。
- 对 Windows + WSL2 + Docker + uv 的开发方式正在适应中，需要解释环境和命令背后的逻辑。
- 希望避免一开始引入过多复杂工具，先让核心流程跑通，再逐步扩展。
- 不希望把所有逻辑都交给大模型，认可“稳定高频能力沉淀为工具，Agent 负责编排”的设计。
- 开发环境当前以 WSL2 Ubuntu 为主，Windows 负责 VS Code/Cursor、浏览器、Docker Desktop、pgAdmin 访问。
- 敏感信息不要写入文档和仓库，包括真实邮箱、密码、API key、token。

## 当前项目/任务背景

用户是一名在广州即将毕业的计算机技术专业女硕士，掌握 Python、PyTorch、深度学习、SQL，了解 Agent 相关知识，包括 Skills、MCP、Tools。

已有经历：

- 两个月 AI 数据分析岗位实习，但实际偏 Agent 任务。
- 掌握过大模型部署实现。
- 用 Python 实现过后端服务。
- 调研过 Agent 架构。
- 学习过归因分析相关数据分析知识。
- 研究生阶段做过 PyTorch 深度学习多模态情感分析项目，发表中科院二区论文并授权发明专利。

就业方向：

- AI 应用开发工程师。

项目选型：

- 不做普通问答机器人。
- 做一个电商经营数据分析与归因 Agent 平台。
- 先完成确定性的后端工具和分析能力，再逐步接入 LLM Agent。

## 已完成事项

1. 环境规划与搭建

- 推荐使用 Windows + WSL2 Ubuntu 开发。
- 推荐项目代码放在 WSL Linux 文件系统中，而不是 `/mnt/c` 下。
- 推荐使用 Docker Desktop + WSL2 Integration。
- 推荐 Python 后端使用 `uv` 管理依赖，不使用 Conda 作为这个后端工程项目的主环境。
- PostgreSQL、Redis、pgAdmin 已通过 Docker Compose 启动。

2. Docker 基础服务

已创建并使用 `docker-compose.yml` 启动：

- PostgreSQL：业务数据库。
- Redis：缓存/任务队列预留。
- pgAdmin：PostgreSQL 可视化管理页面。

pgAdmin 曾因默认邮箱域名不合法启动失败，后来改为合法格式邮箱后已可访问。

3. 数据库和虚拟数据

已创建 PostgreSQL 数据库表：

- `ecommerce_orders`

该表代表电商订单明细，包含：

- `order_id`
- `order_date`
- `city`
- `province`
- `channel`
- `category`
- `product_name`
- `customer_segment`
- `customer_id`
- `quantity`
- `unit_price`
- `order_amount`
- `discount_amount`
- `refund_amount`
- `is_refunded`
- `payment_status`
- `satisfaction_score`
- `created_at`

已插入 1500 条虚拟电商订单数据。

注意：最初通过 PowerShell 管道导入 SQL 时中文变成 `??`，后来改用 `docker cp` 复制 SQL 文件到 PostgreSQL 容器内，再用容器内 `psql -f` 执行，中文恢复正常。

4. 项目目录

已在 WSL 中创建项目：

```bash
/home/administrator/projects/insightpilot
```

当前主要目录：

```text
insightpilot/
├── backend/
├── docs/
├── scripts/
├── docker-compose.yml
├── .gitignore
└── README.md
```

5. Python 后端环境

后端 Python 项目位于：

```bash
/home/administrator/projects/insightpilot/backend
```

已使用 `uv` 创建后端专用虚拟环境：

```bash
/home/administrator/projects/insightpilot/backend/.venv
```

后端依赖写入：

```bash
/home/administrator/projects/insightpilot/backend/pyproject.toml
```

锁定文件：

```bash
/home/administrator/projects/insightpilot/backend/uv.lock
```

已安装主要依赖：

- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg
- pydantic-settings
- python-dotenv
- httpx

曾误在项目根目录初始化过 uv workspace，导致和 `backend` 依赖冲突。后来已清理根目录误生成的 `.venv.bak`、`pyproject.toml.bak`、`uv.lock.bak`、`main.py`、`.python-version`，统一只使用 `backend/.venv`。

6. FastAPI 基础接口

已实现：

```text
GET /health
```

用于确认后端服务可用。

7. 订单查询接口

已实现：

```text
GET /api/orders/summary
GET /api/orders/metrics
GET /api/orders/by-channel
GET /api/orders/by-category
GET /api/orders/recent
```

这些接口用于：

- 城市 GMV 汇总。
- 核心经营指标。
- 渠道 GMV 汇总。
- 品类 GMV 汇总。
- 最近订单明细。

8. GMV 变化分析接口

已实现：

```text
GET /api/analysis/gmv-change
```

支持参数：

- `current_days`
- `compare_days`
- `city`

功能：

- 计算当前周期 GMV。
- 计算对比周期 GMV。
- 计算变化金额。
- 计算变化率。
- 按渠道拆解变化。
- 按品类拆解变化。
- 生成规则摘要。

9. SQL 安全工具层

已实现：

```text
GET  /api/database/schema
POST /api/sql/execute
```

功能：

- 读取数据库 schema。
- 校验 SQL 是否只读。
- 只允许 `SELECT` 或 `WITH`。
- 禁止 `DROP`、`DELETE`、`UPDATE`、`INSERT` 等危险语句。
- 自动限制返回行数。
- 将查询结果转为 JSON 安全格式。

已验证：

- schema 查询返回 200。
- 合法 SELECT 可以执行。
- `DROP TABLE ecommerce_orders` 会被拦截。

10. 首版自然语言 Agent 接口

已实现：

```text
POST /api/agent/query
```

当前是规则版 Agent，还未接入真实大模型。

它能做：

- 识别 GMV 变化归因问题，并调用 `analyze_gmv_change`。
- 识别渠道、品类、城市汇总问题，并生成只读 SQL。
- 识别最近订单查询，并生成只读 SQL。
- 调用 SQL 安全执行工具。
- 返回意图、工具名、参数、SQL、结构化结果、自然语言回答和推理步骤。

11. Text-to-SQL Skill 文档

已创建：

```bash
/home/administrator/projects/insightpilot/backend/app/skills/text_to_sql/SKILL.md
```

内容包括：

- 适用场景。
- 可用表和字段。
- 指标口径。
- SQL 安全规则。
- 工具调用流程。
- 输出格式。

后续可作为 LLM prompt 或 Agent Skill 规范。

## 关键决策

1. 使用 WSL2 Ubuntu 而不是纯 Windows 原生开发

原因：

- Python 后端、Docker、PostgreSQL、未来可能的本地模型和 MCP Server 在 Linux 环境更稳定。
- 网上教程和生产环境更接近 Linux。
- Windows 负责可视化工具，WSL 负责运行服务。

2. 使用 Docker Desktop + WSL2 Integration

原因：

- 避免在 WSL 里手动装 Docker Engine 带来的冲突。
- Docker Desktop 可以统一管理 PostgreSQL、Redis、pgAdmin。

3. 使用 PostgreSQL 而不是 SQLite

原因：

- 更贴近真实业务数据库。
- 适合 Text-to-SQL 场景。
- 支持结构化业务数据。
- 后续可通过 pgvector 扩展到 RAG。

4. 使用 uv 而不是 Conda 管理后端

原因：

- 该项目偏 AI 应用工程、后端服务、Docker 部署，不是深度学习实验。
- `uv + pyproject.toml + uv.lock` 更贴近现代 Python 后端工程。
- Conda 更适合模型训练、CUDA、Jupyter 实验项目。

5. 先做固定工具和分析接口，再做 LLM Agent

原因：

- 不能一开始让大模型随便生成 SQL 并执行，风险高。
- 固定分析工具稳定、可测试、口径统一。
- Agent 应该负责理解意图和编排工具，而不是承担全部计算逻辑。

最终设计不是“固定 SQL”与“Agent 生成 SQL”二选一，而是混合模式：

```text
标准高频问题 -> 调用确定性工具
自由探索问题 -> Text-to-SQL
复杂报告问题 -> Skill 编排多个工具
```

6. 当前 Agent 先用规则版

原因：

- 先跑通自然语言入口、意图识别、工具选择、SQL 安全执行、结果返回的完整链路。
- 后续再把规则识别替换成 LLM 调用。

## 重要文件路径

项目根目录：

```bash
/home/administrator/projects/insightpilot
```

Windows 访问路径：

```text
\\wsl.localhost\Ubuntu-24.04\home\administrator\projects\insightpilot
```

Docker Compose：

```bash
/home/administrator/projects/insightpilot/docker-compose.yml
```

数据库初始化 SQL：

```bash
/home/administrator/projects/insightpilot/scripts/init_ecommerce_orders.sql
```

后端根目录：

```bash
/home/administrator/projects/insightpilot/backend
```

后端虚拟环境：

```bash
/home/administrator/projects/insightpilot/backend/.venv
```

后端依赖：

```bash
/home/administrator/projects/insightpilot/backend/pyproject.toml
/home/administrator/projects/insightpilot/backend/uv.lock
```

后端环境变量：

```bash
/home/administrator/projects/insightpilot/backend/.env
/home/administrator/projects/insightpilot/backend/.env.example
```

不要在交接文档中写入 `.env` 的真实内容。

FastAPI 入口：

```bash
/home/administrator/projects/insightpilot/backend/app/main.py
```

API 层：

```bash
/home/administrator/projects/insightpilot/backend/app/api/health.py
/home/administrator/projects/insightpilot/backend/app/api/orders.py
/home/administrator/projects/insightpilot/backend/app/api/analysis.py
/home/administrator/projects/insightpilot/backend/app/api/database.py
/home/administrator/projects/insightpilot/backend/app/api/sql.py
/home/administrator/projects/insightpilot/backend/app/api/agent.py
```

配置和数据库连接：

```bash
/home/administrator/projects/insightpilot/backend/app/core/config.py
/home/administrator/projects/insightpilot/backend/app/db/session.py
```

业务服务层：

```bash
/home/administrator/projects/insightpilot/backend/app/services/order_service.py
/home/administrator/projects/insightpilot/backend/app/services/analysis_service.py
/home/administrator/projects/insightpilot/backend/app/services/agent_service.py
```

工具层：

```bash
/home/administrator/projects/insightpilot/backend/app/tools/sql_tools.py
```

数据模型：

```bash
/home/administrator/projects/insightpilot/backend/app/schemas/sql.py
/home/administrator/projects/insightpilot/backend/app/schemas/agent.py
```

Skill 文档：

```bash
/home/administrator/projects/insightpilot/backend/app/skills/text_to_sql/SKILL.md
```

项目文档预留：

```bash
/home/administrator/projects/insightpilot/docs/project_overview.md
/home/administrator/projects/insightpilot/docs/database_schema.md
```

## 重要命令与结果

WSL 检查：

```bash
wsl --list --verbose
```

结果显示：

```text
Ubuntu-24.04 Running VERSION 2
docker-desktop Running VERSION 2
```

Docker 服务查看：

```bash
docker ps
```

关键结果：

```text
insightpilot-postgres running, 5432->5432
insightpilot-redis running, 6379->6379
insightpilot-pgadmin running, 5050->80
```

启动 Docker Compose：

```bash
cd ~/projects/insightpilot
docker compose up -d
```

停止 Docker Compose：

```bash
cd ~/projects/insightpilot
docker compose down
```

导入数据库初始化脚本时，最终采用：

```bash
docker cp ./scripts/init_ecommerce_orders.sql insightpilot-postgres:/tmp/init_ecommerce_orders.sql
docker exec insightpilot-postgres psql -U <db_user> -d <db_name> -f /tmp/init_ecommerce_orders.sql
```

结果：

```text
INSERT 0 1500
total_orders = 1500
```

启动后端：

```bash
cd ~/projects/insightpilot/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
http://localhost:8000/docs
http://localhost:8000/health
```

健康检查结果：

```json
{"status":"ok","service":"insightpilot-backend"}
```

已验证的接口：

```text
GET /api/orders/summary
GET /api/orders/metrics
GET /api/orders/by-channel
GET /api/orders/by-category
GET /api/orders/recent
GET /api/analysis/gmv-change
GET /api/database/schema
POST /api/sql/execute
POST /api/agent/query
```

SQL 安全验证结果：

- 合法 SELECT 返回 200。
- `DROP TABLE ecommerce_orders` 被拦截，返回 `is_valid=false`。

Agent 验证结果：

请求：

```json
{
  "query": "为什么最近14天广州GMV下降？",
  "limit": 5
}
```

结果：

```text
intent = gmv_change_analysis
tool_name = analyze_gmv_change
```

请求：

```json
{
  "query": "最近30天各渠道GMV排名",
  "limit": 5
}
```

结果：

```text
intent = channel_summary
tool_name = execute_readonly_sql
```

注意：在 PowerShell 中调用 WSL 命令时，中文输出可能乱码。这是终端编码问题，浏览器访问 FastAPI JSON 通常正常。

## 待办事项

优先级最高：

1. 接入真实大模型

- 在 `agent_service.py` 中增加 LLM 调用。
- 用 LLM 做意图识别、参数抽取和 SQL 生成。
- 保留 SQL 安全校验和只读执行工具。

2. 设计 LLM Provider 配置

- 增加 `.env.example` 中的模型配置模板。
- 不要提交真实 API key。
- 可选 DeepSeek、Qwen、OpenAI 等。

3. 完善 Text-to-SQL Agent 流程

建议流程：

```text
用户问题
  ↓
读取 database schema
  ↓
加载 Text-to-SQL Skill 规则
  ↓
LLM 生成 SQL 或选择工具
  ↓
validate_readonly_sql
  ↓
execute_readonly_sql
  ↓
LLM 生成最终回答
```

4. 增加测试

- 测试 SQL 安全拦截。
- 测试 schema 接口。
- 测试 Agent 意图识别。
- 测试 GMV 分析结果结构。

5. 补充文档

- `README.md`
- `backend/README.md`
- `docs/project_overview.md`
- `docs/database_schema.md`
- `docs/agent_workflow.md`

后续扩展：

- MCP Server，将 SQL 工具、GMV 分析工具暴露为 MCP tools。
- 前端 Dashboard。
- 报告生成接口。
- 更多业务表，例如流量表、用户反馈表。
- 引入用户反馈/情感分析，结合用户已有 PyTorch 多模态情感分析背景。

## 已知问题/风险

1. 当前 Agent 是规则版

还没有真正接入 LLM，所以不能处理复杂自然语言、模糊时间表达、复杂 SQL 查询。

2. SQL 生成目前是模板式

`agent_service.py` 中的 SQL 不是 LLM 生成，而是规则拼接。

3. SQL 安全工具仍需加强

当前只是基础关键词拦截和只允许 SELECT/WITH。后续可加入：

- SQL parser。
- 查询超时。
- 最大扫描行数限制。
- 表白名单。
- 字段白名单。
- 防止复杂 CTE 绕过。

4. 终端中文乱码

PowerShell 调 WSL 时可能显示中文乱码。浏览器和 API JSON 正常概率较高。

5. `.env` 存在本地数据库连接

不要提交 `.env`。`.gitignore` 已忽略 `.env`。

6. 文档仍然不足

README 和 docs 目前多为空或预留，面试展示前必须补充。

7. 当前只有一张订单表

真实数据分析场景通常还需要流量表、商品表、用户反馈表、活动表等。

## 下次新对话启动提示词

请读取以下上下文文档，并继续帮我开发 InsightPilot 项目：

```text
C:\Users\Administrator\Documents\work\project\codex_handoff.md
```

项目实际路径在 WSL：

```bash
/home/administrator/projects/insightpilot
```

当前目标是把现有规则版 Agent 升级为真实 LLM 驱动的 Text-to-SQL Agent。请先检查当前项目文件，再继续实现。注意不要读取或输出 `.env` 中的敏感信息，不要提交真实 API key。

优先下一步：

1. 设计 LLM provider 配置。
2. 更新 `.env.example`，只写变量名模板。
3. 新增 LLM client/service。
4. 让 `/api/agent/query` 可以选择走 LLM 生成 SQL。
5. 所有 LLM 生成的 SQL 必须经过 `validate_readonly_sql` 和 `execute_readonly_sql`。

## 更新日志

2026-06-15 至 2026-06-22：

- 明确项目方向：AI 数据分析与归因 Agent 平台。
- 完成 Windows + WSL2 + Docker 开发环境设计。
- 创建 Docker Compose 服务：PostgreSQL、Redis、pgAdmin。
- 创建并导入 `ecommerce_orders` 虚拟数据表。
- 搭建 FastAPI 后端。
- 使用 uv 管理后端虚拟环境和依赖。
- 实现健康检查接口。
- 实现订单查询接口。
- 实现 GMV 变化分析接口。
- 实现数据库 schema 查询接口。
- 实现只读 SQL 安全执行接口。
- 实现首版规则 Agent 自然语言查询接口。
- 创建 Text-to-SQL Skill 文档。
- 清理误生成的根目录 uv 环境和缓存文件。
- 本文档创建于 2026-06-22，用于后续新 Codex 对话交接。
