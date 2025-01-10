# Cohere Cookbook

> Note: Fork and clone this repository if needed

### 1. Create and activate a virtual environment

```shell
python3 -m venv ~/.venvs/aienv
source ~/.venvs/aienv/bin/activate
```

### 2. Export your `CO_API_KEY`

```shell
export CO_API_KEY=***
```

### 3. Install libraries

```shell
pip install -U cohere duckduckgo-search duckdb yfinance phidata
```

### 4. Run Agent without Tools

- Streaming on

```shell
python cookbook/models/cohere/basic_stream.py
```

- Streaming off

```shell
python cookbook/models/cohere/basic.py
```

### 5. Run Agent with Tools

- DuckDuckGo Search with streaming on

```shell
python cookbook/models/cohere/agent_stream.py
```

- DuckDuckGo Search without streaming

```shell
python cookbook/models/cohere/agent.py
```

- Finance Agent

```shell
python cookbook/models/cohere/finance_agent.py
```

- Data Analyst

```shell
python cookbook/models/cohere/data_analyst.py
```
- Web Search

```shell
python cookbook/models/cohere/web_search.py
```

### 6. Run Agent that returns structured output

```shell
python cookbook/models/cohere/structured_output.py
```

### 7. Run Agent that uses storage

```shell
python cookbook/models/cohere/storage.py
```

### 8. Run Agent that uses knowledge

```shell
python cookbook/models/cohere/knowledge.py
```