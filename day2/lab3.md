### MCP 서버를 만드는 방법

### Lab3

data.csv

```csv
이름,나이,도시,키
Ethan,32,Berlin,180
Sophia,24,Sydney,NaN
Liam,29,Toronto,172
Olivia,41,Singapore,NaN
Noah,36,San Francisco,178
Mina,52,Seoul,169
Mina,52,Seoul,169
```

```text
● [ROLE]
  당신은 FastMCP 기반 MCP 서버를 설계하는 Python 데이터 엔지니어입니다.
  pandas를 활용한 데이터 분석 도구를 MCP tool 형태로 노출하는 구조화된 서버를 작성합니다.

  [TASK]
  CSV 파일을 메모리에 캐싱하고, 그 DataFrame을 대상으로 기본 점검·컬럼 분석·전처리·필터링·그룹 집계를
  수행하는 "Analytics-MCP" 서버를 단일 Python 파일로 구현하세요.

  [REQUIREMENTS]
  다음 요구사항을 반드시 만족해야 합니다:

  1. 라이브러리
     - fastmcp의 FastMCP 사용
     - pandas 사용
     - typing.Annotated 와 pydantic.Field 를 조합해 각 파라미터의 description 을 지정

  2. MCP 인스턴스
     - 이름: "Analytics-MCP"
     - dependencies 옵션에 ["pandas"] 명시

  3. 데이터 캐시
     - 모듈 최상단에 dict 형태의 전역 캐시 `_df_cache = {}` 선언
     - CSV 경로는 문자열 변수 `csv_path` 로 분리 (기본값: "C:\\claude\\mcp\\data.csv")
     - 모듈 로드 시점에 `pd.read_csv(csv_path)` 결과를 `_df_cache["df"]` 에 저장
     - 이후 모든 tool은 이 캐시를 읽거나 갱신하는 방식으로만 DataFrame에 접근

  4. Tool 공통 규칙
     - 각 tool은 `@mcp.tool(name=..., description=...)` 데코레이터로 등록
     - description 은 영어로 작성하며, 지원 operation 목록을 반드시 포함
     - 파라미터는 Annotated[type, Field(description=...)] 형식으로 타입 힌트 부여
     - docstring 에는 `Args:` 와 `Returns:` 섹션을 동일한 스타일로 유지
     - operation 분기는 **dict + lambda 디스패치 패턴**으로 통일
     - 지원되지 않는 operation 입력 시 `ValueError(f"Unsupported operation: {operation}")` 발생

  5. 예외 처리
     - `load_df` : 캐시에 "df" 키가 없으면 ValueError 발생
       ("No DataFrame found in cache. Please save a DataFrame with save_df first.")
     - `column_data_check` : 대상 column 이 DataFrame 에 없으면 ValueError 발생
     - 모든 tool : 지원되지 않는 operation 문자열에 대해 ValueError 발생

  6. 메인 실행부
     - `if __name__ == "__main__":` 블록에서 `mcp.run()` 호출

  [TOOLS SPEC]

  ① load_df
     - 시그니처: `load_df()`
     - 설명: "Load the DataFrame from the cache."
     - 동작: `_df_cache["df"]` 반환, 없으면 ValueError

  ② basic_data_check
     - 시그니처: `basic_data_check(operation: str)`
     - 설명: "Run a basic data check operation on the cached DataFrame.
             Supported operations: shape, dtypes, missing, columns, describe"
     - operation 매핑
       * "shape"    → df.shape
       * "dtypes"   → df.dtypes
       * "missing"  → df.isnull().sum()
       * "columns"  → list(df.columns)
       * "describe" → df.describe()

  ③ column_data_check
     - 시그니처: `column_data_check(operation: str, column: str)`
     - 설명: "Run a column-specific data check operation on the cached DataFrame.
             Supported operations: unique, value_counts"
     - operation 매핑
       * "unique"       → df[column].unique()
       * "value_counts" → df[column].value_counts()
     - column 이 df.columns 에 없으면 ValueError

  ④ data_preprocess
     - 시그니처: `data_preprocess(operation: str)`
     - 설명: "Run a basic data preprocessing operation on the cached DataFrame and update the cache.
             Supported operations: dropna, drop_duplicates"
     - operation 매핑
       * "dropna"          → df.dropna()
       * "drop_duplicates" → df.drop_duplicates()
     - 결과를 `_df_cache["df"]` 에 다시 저장한 뒤 반환 (캐시 갱신)

  ⑤ col_data_analysis
     - 시그니처: `col_data_analysis(operation: str, column: str, condition_value: int)`
     - 설명: "Column-based data analysis.
             Supported operations: filter_gt (greater than), filter_eq (equal to), filter_lt (less than)"
     - operation 매핑
       * "filter_gt" → df[df[column] >  condition_value]
       * "filter_eq" → df[df[column] == condition_value]
       * "filter_lt" → df[df[column] <  condition_value]

  ⑥ group_data_analysis
     - 시그니처: `group_data_analysis(operation: str, group_column: str, target_column: str)`
     - 설명: "Group-based data analysis.
             Supported operations: mean, max, sum, count"
     - operation 매핑
       * "mean"  → df.groupby(group_column)[target_column].mean()
       * "max"   → df.groupby(group_column)[target_column].max()
       * "sum"   → df.groupby(group_column)[target_column].sum()
       * "count" → df.groupby(group_column)[target_column].count()

  [STYLE]
  - 각 tool 위에는 한국어 한 줄 주석으로 역할 요약 (예: `# DataFrame의 기본 정보(shape, dtypes 등)를 확인하는 함수`)
  - docstring 은 Args / Returns 포맷을 모든 tool 에서 동일하게 유지
  - 분기는 if/elif 체인 대신 dict + lambda 패턴으로 통일
  - 중복 로직 없이 간결하게, 불필요한 import·헬퍼·주석 금지
  - 영어 description 과 한국어 주석을 혼용 (파일 전체에서 일관된 톤 유지)

  [OUTPUT FORMAT]
  - 실행 가능한 완전한 단일 Python 파일만 출력
  - 코드 외 설명·머리말·마크다운 금지
  - import → 캐시/경로 선언 → MCP 인스턴스 생성 → 6개 tool → 메인 실행부 순서 엄수
```

```text
[ROLE]
FastMCP 기반 MCP 서버를 설계하는 Python 데이터 엔지니어

[TASK]
CSV를 캐싱하고 pandas DataFrame을 대상으로 기본 점검·컬럼 분석·전처리·필터링·그룹 집계를 수행하는
"Analytics-MCP" 서버를 단일 Python 파일로 구현

[REQUIREMENTS]
- FastMCP, pandas 사용
- Annotated + Field로 파라미터 description 지정
- MCP 이름: "Analytics-MCP", dependencies=["pandas"]

[DATA CACHE]
- `_df_cache = {}`
- `csv_path = "C:\\claude\\mcp\\data.csv"`
- 로드시 `_df_cache["df"] = pd.read_csv(csv_path)`
- 모든 tool은 cache만 사용

[COMMON RULE]
- @mcp.tool(name, description)
- description: 영어 + supported operations 포함
- dict + lambda dispatch 패턴 사용
- unsupported operation → ValueError
- column 없으면 ValueError

[TOOLS]

1) load_df()
- return _df_cache["df"]

2) basic_data_check(operation)
- shape, dtypes, missing, columns, describe

3) column_data_check(operation, column)
- unique, value_counts

4) data_preprocess(operation)
- dropna, drop_duplicates → cache 업데이트

5) col_data_analysis(operation, column, condition_value)
- filter_gt, filter_eq, filter_lt

6) group_data_analysis(operation, group_column, target_column)
- mean, max, sum, count

[STYLE]
- tool 위 한국어 한 줄 주석
- docstring: Args / Returns 통일
- 간결, 중복 없음

[OUTPUT]
- 실행 가능한 단일 Python 파일만 출력
- 설명 금지
- 순서: import → cache → MCP → tools → main
```

```text
analytics-mcp 서버를 이용해 데이터프레임에서 중복값을 제거한 후, 결측치도 모두 제거해줘.
```

analytics_mcp.py가 적절한 위치에 있어야 함.

```bash
uv run --with fastmcp --with pandas fastmcp run analytics-mcp.py
```