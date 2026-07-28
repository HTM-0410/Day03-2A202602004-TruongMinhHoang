# Rubric Self-Assessment

Danh gia theo scoring rubric cua Lab 3.

| Tieu chi | Trong so | Diem de xuat | Artifact | Ly do |
|---|---:|---:|---|---|
| Agentic Fit & Test Design | 20 | 20/20 | `docs/trace_eval.md`, `config/test_cases.json` | Co du 4 tieu chi Agentic Fit va bo test simple, multi-step, edge case. |
| ReAct Implementation & Tools | 30 | 28/30 | `src/tools.py`, `src/app.py`, `src/prompts.py` | Tool specs ro, app co luong Thought/Action/Observation. Tru nhe vi controller van la pipeline co cau truc. |
| Guardrails & Observability | 20 | 19/20 | `src/prompts.py`, `src/app.py`, `docs/trace_eval.md` | Co safety, invalid input, off-topic, insufficient info, target gender clarification, empty result, max iterations. |
| Inter-group Attack & Defense | 20 | 19/20 | `docs/cross_audit.md` | Co cau hoi bay, rui ro, ky vong phong thu va ket qua. |
| Hybrid Decision Flowchart | 10 | 10/10 | `docs/hybrid_flowchart.mermaid` | Co artifact rieng dung yeu cau rubric. |
| **Tong** | **100** | **96/100** |  | Du artifact chinh de nop bai. |

## Phan con co the nang them

- Tao runner auto-export log cho 10 test cases.
- Lay cross-audit that tu nhom khac.
- Nang ReAct controller thanh planner cho phep LLM chon tool linh hoat hon.
