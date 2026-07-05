#!/usr/bin/env python3
"""
Enterprise RAG Assistant — Evaluation Script
Usage:
    python scripts/run_rag_eval.py --backend-url http://localhost:8000/api/v1
    python scripts/run_rag_eval.py --backend-url http://localhost:8000/api/v1 --dataset evals/golden_dataset.json
    python scripts/run_rag_eval.py --backend-url http://localhost:8000/api/v1 --session-prefix eval-run-01

Requires: requests (pip install requests)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path


def load_dataset(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    return [item for item in data if not item.get("id", "").startswith("_")]


def ask_question(backend_url: str, question: str, session_id: str) -> dict:
    import urllib.request
    import urllib.error

    payload = json.dumps({"question": question, "session_id": session_id}).encode()
    req = urllib.request.Request(
        f"{backend_url}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def keyword_match(answer: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in the answer (case-insensitive)."""
    if not keywords:
        return True  # No keywords to check — treat as pass
    answer_lower = answer.lower()
    return any(kw.lower() in answer_lower for kw in keywords)


def citation_match(citations: list[dict], expected_doc: str | None) -> bool:
    """Check if expected document appears in citations."""
    if not expected_doc:
        return True  # No expectation — skip check
    return any(expected_doc.lower() in c.get("document_name", "").lower() for c in citations)


def run_evaluation(backend_url: str, dataset_path: str, session_prefix: str) -> None:
    print(f"\n{'=' * 60}")
    print("  Enterprise RAG Assistant — Evaluation Run")
    print(f"  Backend: {backend_url}")
    print(f"  Dataset: {dataset_path}")
    print(f"{'=' * 60}\n")

    dataset = load_dataset(dataset_path)
    if not dataset:
        print("ERROR: Dataset is empty or could not be parsed.")
        sys.exit(1)

    results = []
    total = len(dataset)

    for i, item in enumerate(dataset, 1):
        q_id = item.get("id", f"q{i:03d}")
        question = item["question"]
        expected_keywords = item.get("expected_answer_keywords", [])
        expected_doc = item.get("expected_document")
        q_type = item.get("type", "answerable")
        session_id = f"{session_prefix}-{q_id}"

        print(f"[{i}/{total}] {q_id}: {question[:80]}...")
        t0 = time.perf_counter()

        try:
            response = ask_question(backend_url, question, session_id)
            latency = round((time.perf_counter() - t0) * 1000)
            answer = response.get("answer", "")
            citations = response.get("citations", [])
            confidence = response.get("confidence", "unknown")

            # Keyword correctness check
            kw_correct = keyword_match(answer, expected_keywords)

            # Citation check
            citation_correct = citation_match(citations, expected_doc)

            # For unanswerable questions, check that confidence is not_found OR answer contains no-answer phrase
            if q_type == "unanswerable":
                no_answer_correct = (
                    confidence == "not_found"
                    or "could not find" in answer.lower()
                    or "not in" in answer.lower()
                )
                kw_correct = no_answer_correct

            results.append({
                "id": q_id,
                "type": q_type,
                "question": question,
                "answer": answer[:200],
                "confidence": confidence,
                "latency_ms": latency,
                "keyword_match": kw_correct,
                "citation_match": citation_correct,
                "sources": len(citations),
                "error": None,
            })

            status_icon = "✓" if kw_correct else "✗"
            print(f"   {status_icon} confidence={confidence} | latency={latency}ms | sources={len(citations)}")

        except Exception as exc:
            latency = round((time.perf_counter() - t0) * 1000)
            print(f"   ✗ ERROR: {exc}")
            results.append({
                "id": q_id,
                "type": q_type,
                "question": question,
                "answer": "",
                "confidence": "error",
                "latency_ms": latency,
                "keyword_match": False,
                "citation_match": False,
                "sources": 0,
                "error": str(exc),
            })

    # ── Report ──
    answerable = [r for r in results if r["type"] == "answerable"]
    unanswerable = [r for r in results if r["type"] == "unanswerable"]
    errors = [r for r in results if r["error"]]
    kw_pass = [r for r in results if r["keyword_match"]]
    cit_pass = [r for r in results if r["citation_match"]]
    avg_latency = sum(r["latency_ms"] for r in results) / total

    print(f"\n{'=' * 60}")
    print("  EVALUATION RESULTS")
    print(f"{'=' * 60}")
    print(f"  Total questions    : {total}")
    print(f"  Answerable         : {len(answerable)}")
    print(f"  Unanswerable       : {len(unanswerable)}")
    print(f"  Errors             : {len(errors)}")
    print(f"  Answer correctness : {len(kw_pass)}/{total} ({100*len(kw_pass)//total}%)")
    print(f"  Citation accuracy  : {len(cit_pass)}/{total} ({100*len(cit_pass)//total}%)")
    print(f"  Avg latency        : {avg_latency:.0f}ms")
    print(f"{'=' * 60}\n")

    # Write JSON report
    report_path = Path("evals") / f"eval_report_{int(time.time())}.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "backend_url": backend_url,
                "summary": {
                    "total": total,
                    "answerable": len(answerable),
                    "unanswerable": len(unanswerable),
                    "errors": len(errors),
                    "keyword_match_pct": 100 * len(kw_pass) // total if total else 0,
                    "citation_match_pct": 100 * len(cit_pass) // total if total else 0,
                    "avg_latency_ms": round(avg_latency),
                },
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"  Report saved: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG evaluation against the backend API")
    parser.add_argument("--backend-url", default="http://localhost:8000/api/v1", help="API base URL")
    parser.add_argument("--dataset", default="evals/golden_dataset.json", help="Path to golden dataset JSON")
    parser.add_argument("--session-prefix", default=f"eval-{uuid.uuid4().hex[:8]}", help="Session ID prefix")
    args = parser.parse_args()

    run_evaluation(args.backend_url, args.dataset, args.session_prefix)
