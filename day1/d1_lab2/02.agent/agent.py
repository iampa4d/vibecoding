"""
LangGraph 기반 고객 문의 분석 에이전트

SSE(Server-Sent Events)로 게시판 서버에서 새 문의 이벤트를 수신하고,
LangGraph 그래프를 통해 분석한 뒤 결과를 REST API로 저장한다.

구조:
  [SSE 수신] → LangGraph 그래프 실행
                ├── analyze_content   (감정 분석 + 요약)
                ├── classify_category (카테고리 분류)
                ├── assess_urgency   (긴급도 평가)
                └── extract_keywords (키워드 추출)
              → [REST API로 결과 저장]
"""

import json
import logging
import time
import signal
import sys
from typing import TypedDict

import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------

SERVER_URL = "http://localhost:3030"
SSE_URL = f"{SERVER_URL}/api/events"
ANALYSIS_URL = f"{SERVER_URL}/api/inquiries"

# ---------------------------------------------------------------------------
# 로깅
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("inquiry-agent")

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=1024,
)

CATEGORIES = [
    "제품문의", "배송문의", "교환/반품", "결제/환불",
    "기술지원", "불만/컴플레인", "칭찬/감사", "일반문의",
]

# ---------------------------------------------------------------------------
# State 정의
# ---------------------------------------------------------------------------

class InquiryState(TypedDict):
    inquiry_id: int
    title: str
    content: str
    ai_category: str
    sentiment: str
    urgency: str
    keywords: list[str]
    summary: str


# ---------------------------------------------------------------------------
# 노드 함수들
# ---------------------------------------------------------------------------

def analyze_content(state: InquiryState) -> dict:
    """글의 감정과 요약을 분석한다."""
    logger.info(f"  [1/4] 감정 분석 + 요약 (문의 #{state['inquiry_id']})")
    response = llm.invoke([
        SystemMessage(content=(
            "당신은 고객 문의를 분석하는 전문가입니다. "
            "주어진 문의 글의 감정(긍정/부정/중립)과 핵심 요약(1~2문장)을 JSON으로 반환하세요.\n"
            '반드시 {"sentiment": "긍정|부정|중립", "summary": "요약 내용"} 형식으로만 답하세요.'
        )),
        HumanMessage(content=f"제목: {state['title']}\n내용: {state['content']}"),
    ])
    data = json.loads(response.content)
    return {"sentiment": data["sentiment"], "summary": data["summary"]}


def classify_category(state: InquiryState) -> dict:
    """문의를 카테고리로 분류한다."""
    logger.info(f"  [2/4] 카테고리 분류 (문의 #{state['inquiry_id']})")
    response = llm.invoke([
        SystemMessage(content=(
            "당신은 고객 문의 분류 전문가입니다. "
            f"다음 카테고리 중 가장 적합한 것 하나를 골라 JSON으로 반환하세요: {CATEGORIES}\n"
            '반드시 {"category": "카테고리명"} 형식으로만 답하세요.'
        )),
        HumanMessage(content=f"제목: {state['title']}\n내용: {state['content']}"),
    ])
    data = json.loads(response.content)
    return {"ai_category": data["category"]}


def assess_urgency(state: InquiryState) -> dict:
    """긴급도를 평가한다."""
    logger.info(f"  [3/4] 긴급도 평가 (문의 #{state['inquiry_id']})")
    response = llm.invoke([
        SystemMessage(content=(
            "당신은 고객 문의의 긴급도를 평가하는 전문가입니다. "
            "긴급도를 판단하세요.\n"
            "- 높음: 즉시 대응 필요 (불만, 결제 오류, 긴급 배송 등)\n"
            "- 보통: 일반적인 시간 내 처리 가능\n"
            "- 낮음: 단순 문의, 감사 인사 등\n"
            '반드시 {"urgency": "높음|보통|낮음"} 형식으로만 답하세요.'
        )),
        HumanMessage(content=(
            f"제목: {state['title']}\n내용: {state['content']}\n"
            f"감정: {state.get('sentiment', '알 수 없음')}"
        )),
    ])
    data = json.loads(response.content)
    return {"urgency": data["urgency"]}


def extract_keywords(state: InquiryState) -> dict:
    """핵심 키워드를 추출한다."""
    logger.info(f"  [4/4] 키워드 추출 (문의 #{state['inquiry_id']})")
    response = llm.invoke([
        SystemMessage(content=(
            "당신은 텍스트에서 핵심 키워드를 추출하는 전문가입니다. "
            "주어진 문의 글에서 중요한 키워드를 3~5개 추출하세요.\n"
            '반드시 {"keywords": ["키워드1", "키워드2", ...]} 형식으로만 답하세요.'
        )),
        HumanMessage(content=f"제목: {state['title']}\n내용: {state['content']}"),
    ])
    data = json.loads(response.content)
    return {"keywords": data["keywords"]}


# ---------------------------------------------------------------------------
# 그래프 빌드
# ---------------------------------------------------------------------------

graph_builder = StateGraph(InquiryState)

graph_builder.add_node("analyze_content", analyze_content)
graph_builder.add_node("classify_category", classify_category)
graph_builder.add_node("assess_urgency", assess_urgency)
graph_builder.add_node("extract_keywords", extract_keywords)

graph_builder.add_edge(START, "analyze_content")
graph_builder.add_edge("analyze_content", "classify_category")
graph_builder.add_edge("classify_category", "assess_urgency")
graph_builder.add_edge("assess_urgency", "extract_keywords")
graph_builder.add_edge("extract_keywords", END)

graph = graph_builder.compile()


# ---------------------------------------------------------------------------
# 분석 결과 저장
# ---------------------------------------------------------------------------

def save_analysis(inquiry_id: int, result: dict):
    """분석 결과를 서버 REST API로 전송하여 저장한다."""
    payload = {
        "ai_category": result["ai_category"],
        "ai_sentiment": result["sentiment"],
        "ai_urgency": result["urgency"],
        "ai_keywords": json.dumps(result["keywords"], ensure_ascii=False),
        "ai_summary": result["summary"],
    }

    resp = httpx.patch(
        f"{ANALYSIS_URL}/{inquiry_id}/analysis",
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    logger.info(f"  분석 결과 저장 완료 (문의 #{inquiry_id})")


# ---------------------------------------------------------------------------
# 이벤트 처리
# ---------------------------------------------------------------------------

def handle_inquiry_event(event_data: dict):
    """새 문의 이벤트를 받아 LangGraph 그래프로 분석한다."""
    inquiry_id = event_data["id"]
    title = event_data["title"]
    content = event_data["content"]

    logger.info(f"[분석 시작] 문의 #{inquiry_id}: {title}")

    initial_state: InquiryState = {
        "inquiry_id": inquiry_id,
        "title": title,
        "content": content,
        "ai_category": "",
        "sentiment": "",
        "urgency": "",
        "keywords": [],
        "summary": "",
    }

    try:
        result = graph.invoke(initial_state)

        save_analysis(inquiry_id, result)

        logger.info(
            f"[분석 완료] 문의 #{inquiry_id}: "
            f"분류={result['ai_category']} / 감정={result['sentiment']} / "
            f"긴급도={result['urgency']} / 키워드={result['keywords']}"
        )
    except Exception as e:
        logger.error(f"[분석 실패] 문의 #{inquiry_id}: {e}")


# ---------------------------------------------------------------------------
# SSE 클라이언트
# ---------------------------------------------------------------------------

def parse_sse_stream(lines: list[str]):
    """SSE 텍스트 라인들을 파싱하여 (event_type, data) 를 반환한다."""
    event_type = None
    data_lines = []

    for line in lines:
        if line.startswith("event: "):
            event_type = line[7:].strip()
        elif line.startswith("data: "):
            data_lines.append(line[6:])
        elif line == "":
            if data_lines:
                yield event_type, "\n".join(data_lines)
            event_type = None
            data_lines = []

    # 남은 데이터 처리
    if data_lines:
        yield event_type, "\n".join(data_lines)


def listen_sse():
    """SSE 스트림에 연결하여 이벤트를 수신한다."""
    logger.info(f"SSE 연결 시도: {SSE_URL}")

    with httpx.stream("GET", SSE_URL, timeout=None) as response:
        logger.info("SSE 연결 성공. 이벤트 대기 중...")

        buffer = ""
        for chunk in response.iter_text():
            buffer += chunk
            # 빈 줄(\n\n)로 이벤트 구분
            while "\n\n" in buffer:
                event_block, buffer = buffer.split("\n\n", 1)
                lines = event_block.strip().split("\n")

                for event_type, data_str in parse_sse_stream(lines):
                    if event_type == "connected":
                        logger.info("서버로부터 연결 확인 수신")
                    elif event_type == "new_inquiry":
                        try:
                            event_data = json.loads(data_str)
                            handle_inquiry_event(event_data)
                        except json.JSONDecodeError as e:
                            logger.error(f"이벤트 데이터 파싱 실패: {e}")
                    # heartbeat (': heartbeat') 은 자동 무시


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

shutdown = False

def handle_signal(signum, frame):
    global shutdown
    shutdown = True
    logger.info("종료 신호 수신. 종료합니다.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def main():
    logger.info("=" * 60)
    logger.info("고객 문의 분석 에이전트 시작")
    logger.info(f"서버 주소: {SERVER_URL}")
    logger.info("=" * 60)

    retry_delay = 2

    while not shutdown:
        try:
            listen_sse()
        except httpx.ConnectError:
            logger.warning(f"서버 연결 실패. {retry_delay}초 후 재시도...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except Exception as e:
            logger.error(f"예상치 못한 에러: {e}")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        else:
            retry_delay = 2  # 정상 연결 후 재연결 시 초기화


if __name__ == "__main__":
    main()
