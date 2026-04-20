### MCP 서버를 만드는 방법

1. 개발 환경 구축

- uv 설치

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

- FastMCP 설치

```bash
pip install fastmcp
python -m pip install --upgrade --force-reinstall fastmcp
```

```bash
fastmcp version
```


2. MCP 서버 프로젝트 구조

```text
C:\
└─ MCP
   └─ Datetime-MCP
      └─ server.py
```

- server.py 파이썬 파일

```python
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP(name="Datetime-MCP")

@mcp.tool()
def get_current_datetime() -> str:
    """현재 날짜와 시각을 반환합니다."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
```

```bash
python -m venv venv
.\venv\Scripts\activate
pip install fastmcp
fastmcp install claude-desktop server.py
```

```text
Datetime-MCP 서버를 사용하여 현재 날짜를 알려줘.
```

---

```text
[ROLE]
당신은 FastMCP 기반 MCP 서버를 설계하는 Python 백엔드 개발자입니다.

[TASK]
사칙연산 기능(add, sub, mul, div)을 제공하는 MCP 서버를 구현하세요.

[REQUIREMENTS]
다음 요구사항을 반드시 만족해야 합니다:

1. FastMCP 라이브러리를 사용한다.
2. MCP 서버 이름은 "Calculator-MCP"로 설정한다.
3. 각 연산은 MCP tool로 구현한다.
4. 각 tool은 다음 조건을 만족해야 한다:
   - name 명시
   - description 포함
   - 타입 힌트 사용 (int → int, div는 float)
   - docstring 포함
5. div 함수는 0으로 나누는 경우 예외를 발생시켜야 한다.
6. 메인 실행 코드에서 mcp.run()을 호출한다.

[TOOLS SPEC]
- add: 두 수를 더함
- sub: 두 수를 뺌
- mul: 두 수를 곱함
- div: 두 수를 나눔 (float 반환)

[OUTPUT FORMAT]
- Python 코드만 출력
- 코드 외 설명 금지
- 실행 가능한 완전한 파일 형태로 작성

[STYLE]
- 가독성 높은 코드
- 일관된 docstring 스타일 유지
- 불필요한 코드 금지
```

```text
FastMCP를 사용해 add, sub, mul, div tool을 가진 Calculator MCP 서버를 Python으로 구현해줘. div는 0 나누기 예외 처리 포함, 실행 코드 포함, 설명 없이 코드만 출력.
```

```bash
fastmcp install claude-desktop calculator_mcp.py
```

```text
calculator-mcp를 사용하여 6,7의 사칙연산을 수행해줘.
```