config 파일에 tavily의 MCP 설정 정보를 추가

```json
{
  "mcpServers": {
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.2"],
      "env": {
        "TAVILY_API_KEY": "[YOUR_TAVILY_KEY]"
      }
    }
  },
  "preferences": {
    "coworkWebSearchEnabled": true,
    "coworkScheduledTasksEnabled": true,
    "ccdScheduledTasksEnabled": true
  }
}
```

검색하기

```text
Tavily MCP 서버를 사용하여 오늘의 한국 경제 시장의 전반적인 데이터를 분석해서 알려줘.
```

검색 깊이 조절 :

```text
Tavily MCP 서버를 사용하여 MCP(Model Context Protocol)에 밀접하게 연관된 내용을 검색해서 알려줘.
```

---

### 트위터 MCP 서버를 이용하여 포스팅과 검색

```json
{
  "mcpServers": {
    "twitter-mcp": {
      "command": "npx",
      "args": ["-y", "@enescinar/twitter-mcp"],
      "env": {
        "API_KEY": "<API 키>",
        "API_SECRET_KEY": "<API 시크릿 키>",
        "ACCESS_TOKEN": "<액세스 토큰>",
        "ACCESS_TOKEN_SECRET": "<액세스 토큰 시크릿>"
      }
    }
  }
}
```

```text
MCP(Model Context Protocol)에 대한 내용을 200자 이내로 작성하여 X(트위터)에 올려줘.
```

---

# References

https://github.com/awslabs/agentcore-samples/tree/main/02-use-cases/A2A-multi-agent-incident-response
