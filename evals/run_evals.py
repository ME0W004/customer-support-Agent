import sys
import logging
from evals.golden_dataset import GOLDEN_EMAILS
from app.ai.classifier import classify_email
from app.ai.agent import answer_customer_email

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.WARNING)


def run_evals():
    print("=" * 70)
    print("RUNNING AI CUSTOMER SUPPORT EVALUATION BENCHMARK")
    print(f"Total benchmark cases: {len(GOLDEN_EMAILS)}")
    print("=" * 70)

    section_correct = 0
    support_check_correct = 0
    action_correct = 0

    for idx, case in enumerate(GOLDEN_EMAILS, start=1):
        print(f"\n[{idx}/{len(GOLDEN_EMAILS)}] Testing: {case.id} ...")
        
        # 1. Evaluate Classifier
        classification = classify_email(case.subject, case.body)
        is_sec_match = classification.section == case.expected_section
        is_sup_match = classification.is_support_request == case.expected_is_support
        
        if is_sec_match:
            section_correct += 1
        if is_sup_match:
            support_check_correct += 1

        print(f"  Classifier: section='{classification.section}' (expected '{case.expected_section}') -> {'OK' if is_sec_match else 'MISMATCH'}")
        print(f"  Is Support: {classification.is_support_request} (expected {case.expected_is_support}) -> {'OK' if is_sup_match else 'MISMATCH'}")

        # Determine simulated pipeline action
        if not classification.is_support_request or classification.section == "irrelevant":
            actual_action = "skip"
        else:
            # 2. Evaluate Support Agent
            reply = answer_customer_email(
                customer_email="test_user@example.com",
                subject=case.subject,
                body=case.body,
                category=classification.section
            )
            if reply.escalate_to_human or reply.confidence < 0.70 or not reply.is_resolved:
                actual_action = "escalate"
            else:
                actual_action = "reply"

        is_act_match = actual_action == case.expected_action
        if is_act_match:
            action_correct += 1

        print(f"  Action Decision: '{actual_action}' (expected '{case.expected_action}') -> {'OK' if is_act_match else 'MISMATCH'}")

    total = len(GOLDEN_EMAILS)
    sec_acc = (section_correct / total) * 100
    sup_acc = (support_check_correct / total) * 100
    act_acc = (action_correct / total) * 100

    print("\n" + "=" * 70)
    print("EVALUATION RESULTS SUMMARY")
    print("=" * 70)
    print(f"Category Classification Accuracy: {section_correct}/{total} ({sec_acc:.1f}%)")
    print(f"Support Detection Accuracy:       {support_check_correct}/{total} ({sup_acc:.1f}%)")
    print(f"Pipeline Action Decision Accuracy:{action_correct}/{total} ({act_acc:.1f}%)")
    print("=" * 70)

    if act_acc >= 80.0:
        print("ALL QUALITY BENCHMARKS PASSED (Target >= 80%)!")
        return 0
    else:
        print("BENCHMARK FAILED TO MEET ACCURACY THRESHOLD.")
        return 1


if __name__ == "__main__":
    exit_code = run_evals()
    sys.exit(exit_code)
