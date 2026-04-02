1. Openclaw를 실행할 수 있는 격리된 머신 준비

  - AWS EC2
  - Oracle virtualbox

2. Claude code 설치

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

```bash
mkdir openclaw
cd openclaw
claude
```

3. openclaw를 실행할 수 있도록 claude code에서 게시판 생성

```text
현재 이 시스템 상태를 파악하고 mysql, nodejs, pm2 설치하고 간단한 웹 CRUD게시판을 생성해줘.
웹 게시판에는 기본적으로 글쓰기 기능, 글에 댓글달기 기능을 만들어줘.
또한 API로도 게시판을 이용할 수 있도록 인터페이스를 설계하고 API문서도 함께 만들어줘.
프로덕션 레벨로 만들어서 서버를 띄우고 서버는 3000번 포트로 열어줘.
작업 후 모든 것이 완전하게 작동하는지 자율적인 테스트를 통해 완전하게 검증해줘.
```

```
다시 실행해줘.
```

