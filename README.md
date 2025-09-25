# DataFlowAgent - 智能数据分析助手

<div align="center">

![GitHub](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**智能数据分析代理 | 自动拆解需求 | 智能代码解释器**

</div>


## 📖 简介
DataFlowAgent 是一个先进的自动数据分析代理系统，能够通过自然语言对话自动完成数据库连接、SQL/Python代码生成与执行、数据分析报告生成等复杂任务。


## 🌟 核心特性

### 🤖 智能对话交互
- 通过自然语言对话理解用户数据分析需求
- 自动判断任务类型并选择最优执行方案

### 🔌 自动数据连接
- 支持多种数据库自动连接（目前只支持Mysql）
- 智能识别数据结构与类型

### 💻 代码生成与执行
- **自动SQL代码生成**：根据需求生成优化的SQL查询语句
- **自动Python代码生成**：支持数据分析、可视化等Python代码生成
- **安全代码执行**：在隔离环境中安全运行生成的代码

### 🔍 智能审查系统
- **自动代码审查**：对生成的代码进行质量检查和优化
- **深度Debug功能**：自动识别并修复代码错误
- **文本内容审查**：确保输出内容的准确性和安全性

### 🎯 三种工作模式
- **普通模式**：适合常规数据分析任务，平衡效率与准确性
- **增强模式**：开启复杂任务拆解和深度debug，提升处理能力
- **开发者模式**：交互式确认流程，代码审查、任务拆解功能，适合开发人员精细控制

## 📋 安装要求

### 环境依赖
```bash
# 创建虚拟环境（推荐）
python -m venv dataflow_env
source dataflow_env/bin/activate  # Linux/Mac
# 或
dataflow_env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 环境配置
1. 复制环境配置文件：
```bash
cp env.example .env
```

2. 在`.env`文件中配置必要的API密钥和数据库连接信息

## 🚀 快速开始

### 快速验证
```shell
python ./run.py
```

### 基本使用示例

```python
from data_analyst_agent import DataFlowAgent
# 初始化代理
agent = DataFlowAgent()
# 开始对话分析
agent.run("统计user_demographics数据表的数据量")
```

### 高级配置示例

```python
from data_analyst_agent import DataFlowAgent, InterProject, AvailableFunctions
from data_analyst_agent import (
    python_inter, sql_inter, extract_data,fig_inter
)

af = AvailableFunctions(
    functions_list=[sql_inter, extract_data, python_inter, fig_inter]
)
pro = InterProject(project_name='../../mg测试项目', doc_name='mg测试文档')
# 开发者模式配置
agent = DataFlowAgent(
    model="deepseek-chat",
    project=pro,
    available_functions=af,
    is_developer_mode=True,
    is_enhanced_mode=True
)
```

## ⚙️ 配置参数

### DataFlowAgent 初始化参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `model` | str | "deepseek-chat" | 使用的AI模型类型 |
| `env_path` | str | "../../env" | 环境变量文件路径 |
| `system_content_list` | list | [] | 系统消息或外部文档列表 |
| `project` | Project | None | 项目配置对象 |
| `messages` | list | None | 对话历史消息 |
| `available_functions` | list | None | 可用外部工具函数 |
| `is_enhanced_mode` | bool | False | 是否开启增强模式 |
| `is_developer_mode` | bool | False | 是否开启开发者模式 |

## 📊 功能详解

### 自动SQL生成与执行
- 智能解析自然语言查询需求
- 生成优化的SQL语句
- 自动执行并验证结果

### Python代码生成
- 数据分析代码生成
- 数据可视化代码
- 机器学习模型代码

### 智能审查机制
- **代码质量检查**：语法、逻辑、性能审查
- **安全审查**：防止危险操作
- **结果验证**：确保分析准确性

## 🛠️ 开发模式

开发者模式提供以下高级功能：
- 代码执行前确认
- 逐步调试支持
- 自定义函数集成
- 详细执行日志

## 📁 项目结构

```
dataflow-agent/
│   README.md
│   requirements.txt
│   run.py
│   setup.py
│       
├───data_analyst_agent/      # 源代码目录
│   │   config.py
│   │   __init__.py
│   │   
│   ├───api/                # 大模型api服务
│   │   │   llms.py
│   │   └───__init__.py
│   │           
│   ├───core/               # 核心组件
│   │           
│   ├───functions_lib       # 外部函数   
│   └───utils               # 工具库 
│       └───helpers.py      
├───docs
└───tests
        module_test.py
```

## 🏗️ 系统架构
- [点击此处进行查看](assets/技术架构图.png)


## 🤝 贡献指南

我们欢迎社区贡献！请参考：
1. Fork 本项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系我们

- 项目主页：https://github.com/lzlxyc/AutoSearchAgen
- 问题反馈：https://github.com/lzlxyc/AutoSearchAgen/issues
- 邮箱：lzl_xyc@163.com
- 作者：林晚飞
---

## 🔮 路线图

- [ ] 支持更多数据库类型
- [ ] 增强可视化能力
- [ ] 集成更多AI模型
- [ ] 提供Web界面
- [ ] 增加团队协作功能

---

*让数据分析变得更简单、更智能！*