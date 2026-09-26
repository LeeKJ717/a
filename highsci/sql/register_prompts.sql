-- highsci 문제은행 생성용 gemma 프롬프트 (soul3 prompt_db 표준)
-- 실행(soul3에서):
--   mysql -u prompt_user -p'prompt2026!' --socket=/home/mysql/mysql.sock prompt_db < register_prompts.sql
-- 코드는 prompt_text.format(text=...)로 치환하므로 JSON 예시의 중괄호는 {{ }}로 이중 표기한다.
-- model은 holymind GPU 여건에 맞게 UPDATE로 바꿔도 된다 (예: gemma4:27b).

INSERT INTO prompts (prompt_key, category, keywords, model, lang, prompt_text, options_json, description) VALUES
('highsci_item_gen', 'content_gen', '통합과학,문제은행,문항생성,highsci,IRT,고등과학', 'gemma4:e4b', 'ko',
'You are an expert Korean high-school science item writer for the 2022 revised national curriculum subject Integrated Science (통합과학1, 통합과학2).
WRITE new multiple-choice test items that follow the SPEC below exactly.

RULES:
1. Write every item in natural KOREAN, in the formal style of Korean school exams and the CSAT (수능).
2. Each item has exactly 5 choices and exactly ONE correct answer. Distractors must be plausible and reflect common student misconceptions.
3. Stay strictly inside the given achievement standard and concepts. Do NOT use content outside the high-school Integrated Science level.
4. Match the requested difficulty (1 = very easy recall, 3 = application, 5 = hard multi-step analysis) and the requested cognitive level.
5. For calculation items, use clean numbers, include units, and make sure the answer is mathematically correct.
6. Items with <보기> statements (ㄱ, ㄴ, ㄷ) are allowed; put the statements inside the stem.
7. Do NOT reference figures or images that are not given. If data is needed, write it as a text table inside the stem.
8. Every item must be clearly different from the items listed in avoid_stems.
9. concepts must be chosen ONLY from the concept list in the SPEC.
10. Output ONLY valid JSON, no markdown, no comments.

OUTPUT FORMAT:
{{"items": [{{"stem": "문제 본문", "choices": ["①의 내용", "②의 내용", "③의 내용", "④의 내용", "⑤의 내용"], "answer": 3, "explanation": "정답 해설과 오답 이유", "concepts": ["개념명"], "difficulty": 3, "cognitive": "적용"}}]}}
answer is the 1-based index of the correct choice. Do NOT put circled numbers inside choices.

SPEC:
{text}
',
'{"think": false, "stream": false, "format": "json", "temperature": 0.8, "top_p": 0.95, "num_ctx": 16384, "num_predict": 6000}',
'통합과학1·2 단원별 5지선다 문항 일괄 생성 (SPEC JSON을 {text}로 전달)'),

('highsci_item_verify', 'content_gen', '통합과학,문제은행,문항검증,highsci,품질관리', 'gemma4:e4b', 'ko',
'You are a strict Korean high-school science teacher reviewing an Integrated Science (통합과학) exam item.
SOLVE the item below independently, step by step in your head, WITHOUT looking for hints in the explanation.
Then CHECK: exactly one choice is correct, the science is accurate, the stem is unambiguous, and the item fits high-school level.
Output ONLY valid JSON, no markdown:
{{"answer": 1, "valid": true, "reason": "짧은 한국어 사유"}}
answer is the 1-based index of the choice you believe is correct. valid is false if the item has an error, ambiguity, no correct choice, or more than one correct choice.

ITEM:
{text}
',
'{"think": false, "stream": false, "format": "json", "temperature": 0.0, "num_ctx": 8192, "num_predict": 800}',
'통합과학 생성 문항 독립 풀이 검증 (정답 일치·오류 판정)')
ON DUPLICATE KEY UPDATE
  prompt_text = VALUES(prompt_text),
  options_json = VALUES(options_json),
  keywords = VALUES(keywords),
  description = VALUES(description);
