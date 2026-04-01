# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""
Tests for ScopeBlind protect-mcp AgentMesh adapter.

Covers:
- Cedar decision parsing and representation
- CedarPolicyBridge: Cedar deny is authoritative, trust layering, receipt requirements
- ReceiptVerifier: structure validation, type checking, AGT context conversion
- SpendingGate: amount limits, category blocks, utilization bands, trust floors
- scopeblind_context: AGT-compatible context shape
"""

import time

import pytest

from scopeblind_protect_mcp import (
    CedarDecision,
    CedarPolicyBridge,
    ReceiptVerifier,
    SpendingGate,
    scopeblind_context,
)


# ---- Fixtures ----


def make_receipt(
    effect="allow",
    tool="web_search",
    receipt_type="scopeblind:decision",
    **extra_payload,
):
    """Build a minimal valid receipt for testing."""
    payload = {"effect": effect, "tool": tool, "timestamp": time.time()}
    payload.update(extra_payload)
    return {
        "type": receipt_type,
        "payload": payload,
        "signature": "ed25519_test_sig_placeholder",
        "publicKey": "ed25519_test_pk_placeholder",
    }


def make_spending_receipt(amount=50.0, category="cloud_compute", band="low"):
    """Build a spending authority receipt."""
    return make_receipt(
        effect="allow",
        tool="purchase",
        receipt_type="scopeblind:spending_authority",
        amount=amount,
        currency="USD",
        utilization_band=band,
        category=category,
    )


# ---- CedarDecision ----


class TestCedarDecision:
    def test_allow_decision(self):
        d = CedarDecision(effect="allow", tool_name="web_search")
        assert d.allowed is True
        assert d.effect == "allow"

    def test_deny_decision(self):
        d = CedarDecision(effect="deny", tool_name="shell_exec", policy_ids=["sb-001"])
        assert d.allowed is False
        assert d.policy_ids == ["sb-001"]

    def test_to_dict_shape(self):
        d = CedarDecision(effect="allow", tool_name="read_file")
        result = d.to_dict()
        assert set(result.keys()) == {"effect", "tool", "policy_ids", "diagnostics", "evaluated_at"}

    def test_from_receipt(self):
        receipt = make_receipt(effect="deny", tool="shell_exec")
        d = CedarDecision.from_receipt(receipt)
        assert d.effect == "deny"
        assert d.tool_name == "shell_exec"
        assert d.allowed is False

    def test_from_receipt_with_policy_ids(self):
        receipt = make_receipt(effect="deny", tool="bash", policy_ids=["sb-clinejection-001"])
        d = CedarDecision.from_receipt(receipt)
        assert d.policy_ids == ["sb-clinejection-001"]


# ---- CedarPolicyBridge ----


class TestCedarPolicyBridge:
    def test_cedar_deny_is_authoritative(self):
        """Cedar deny must not be overridable by high trust score."""
        bridge = CedarPolicyBridge()
        decision = CedarDecision(effect="deny", tool_name="shell_exec", policy_ids=["sb-001"])
        result = bridge.evaluate(decision, agent_trust_score=999, agent_did="did:mesh:agent-1")
        assert result["allowed"] is False
        assert result["cedar_effect"] == "deny"

    def test_cedar_allow_passes(self):
        bridge = CedarPolicyBridge()
        decision = CedarDecision(effect="allow", tool_name="web_search")
        result = bridge.evaluate(decision, agent_trust_score=500, agent_did="did:mesh:agent-1")
        assert result["allowed"] is True

    def test_cedar_allow_with_trust_floor(self):
        """Cedar allow but trust too low should deny."""
        bridge = CedarPolicyBridge(trust_floor=600)
        decision = CedarDecision(effect="allow", tool_name="web_search")
        result = bridge.evaluate(decision, agent_trust_score=100, agent_did="did:mesh:agent-1")
        assert result["allowed"] is False
        assert "trust score" in result["reason"].lower()

    def test_trust_bonus_applied(self):
        bridge = CedarPolicyBridge(trust_bonus_per_allow=75)
        decision = CedarDecision(effect="allow", tool_name="read_file")
        result = bridge.evaluate(decision, agent_trust_score=400)
        assert result["adjusted_trust"] == 475

    def test_deny_penalty_applied(self):
        bridge = CedarPolicyBridge(deny_penalty=300)
        decision = CedarDecision(effect="deny", tool_name="shell_exec")
        result = bridge.evaluate(decision, agent_trust_score=200)
        assert result["adjusted_trust"] == 0  # clamped at 0

    def test_receipt_required_but_missing(self):
        bridge = CedarPolicyBridge(require_receipt=True)
        decision = CedarDecision(effect="allow", tool_name="web_search")
        result = bridge.evaluate(decision, agent_trust_score=500)
        assert result["allowed"] is False
        assert "receipt required" in result["reason"].lower()

    def test_receipt_provided_when_required(self):
        bridge = CedarPolicyBridge(require_receipt=True)
        decision = CedarDecision(effect="allow", tool_name="web_search")
        receipt = make_receipt()
        result = bridge.evaluate(decision, agent_trust_score=500, receipt=receipt)
        assert result["allowed"] is True
        assert "receipt_hash" in result

    def test_stats_tracking(self):
        bridge = CedarPolicyBridge()
        allow = CedarDecision(effect="allow", tool_name="read_file")
        deny = CedarDecision(effect="deny", tool_name="shell_exec")
        bridge.evaluate(allow, agent_trust_score=500)
        bridge.evaluate(deny, agent_trust_score=500)
        bridge.evaluate(allow, agent_trust_score=500)
        stats = bridge.get_stats()
        assert stats["total_evaluations"] == 3
        assert stats["allowed"] == 2
        assert stats["cedar_denies"] == 1

    def test_trust_capped_at_1000(self):
        bridge = CedarPolicyBridge(trust_bonus_per_allow=200)
        decision = CedarDecision(effect="allow", tool_name="read_file")
        result = bridge.evaluate(decision, agent_trust_score=900)
        assert result["adjusted_trust"] == 1000


# ---- ReceiptVerifier ----


class TestReceiptVerifier:
    def test_valid_receipt(self):
        verifier = ReceiptVerifier()
        receipt = make_receipt()
        result = verifier.validate_structure(receipt)
        assert result["valid"] is True
        assert result["receipt_type"] == "scopeblind:decision"

    def test_missing_fields(self):
        verifier = ReceiptVerifier()
        result = verifier.validate_structure({"type": "scopeblind:decision"})
        assert result["valid"] is False
        assert "Missing required fields" in result["reason"]

    def test_unknown_type_strict(self):
        verifier = ReceiptVerifier(strict=True)
        receipt = make_receipt()
        receipt["type"] = "unknown:type"
        result = verifier.validate_structure(receipt)
        assert result["valid"] is False

    def test_unknown_type_lenient(self):
        verifier = ReceiptVerifier(strict=False)
        receipt = make_receipt()
        receipt["type"] = "custom:type"
        result = verifier.validate_structure(receipt)
        assert result["valid"] is True

    def test_spending_authority_receipt(self):
        verifier = ReceiptVerifier()
        receipt = make_spending_receipt(amount=250.0, category="cloud_compute", band="medium")
        result = verifier.validate_structure(receipt)
        assert result["valid"] is True
        assert result["amount"] == 250.0
        assert result["utilization_band"] == "medium"

    def test_to_agt_context(self):
        verifier = ReceiptVerifier()
        receipt = make_receipt(effect="allow", tool="web_search")
        ctx = verifier.to_agt_context(receipt)
        assert ctx["receipt_valid"] is True
        assert ctx["issuer_blind"] is True
        assert ctx["cedar_effect"] == "allow"
        assert "receipt_hash" in ctx

    def test_invalid_receipt_agt_context(self):
        verifier = ReceiptVerifier()
        ctx = verifier.to_agt_context({"broken": True})
        assert ctx["receipt_valid"] is False


# ---- SpendingGate ----


class TestSpendingGate:
    def test_basic_spend_allowed(self):
        gate = SpendingGate()
        result = gate.evaluate_spend(amount=50.0, agent_trust_score=500)
        assert result["allowed"] is True

    def test_exceeds_single_limit(self):
        gate = SpendingGate(max_single_amount=100.0)
        result = gate.evaluate_spend(amount=150.0, agent_trust_score=500)
        assert result["allowed"] is False
        assert "exceeds" in result["reason"].lower()

    def test_negative_amount_rejected(self):
        gate = SpendingGate()
        result = gate.evaluate_spend(amount=-10.0)
        assert result["allowed"] is False

    def test_blocked_category(self):
        gate = SpendingGate(blocked_categories=["gambling", "weapons"])
        result = gate.evaluate_spend(amount=50.0, category="gambling", agent_trust_score=999)
        assert result["allowed"] is False
        assert "blocked" in result["reason"].lower()

    def test_exceeded_utilization_band(self):
        gate = SpendingGate()
        result = gate.evaluate_spend(amount=10.0, utilization_band="exceeded", agent_trust_score=999)
        assert result["allowed"] is False
        assert "exceeded" in result["reason"].lower()

    def test_high_utilization_needs_trust(self):
        gate = SpendingGate(high_util_trust_floor=500)
        result = gate.evaluate_spend(
            amount=50.0, utilization_band="high", agent_trust_score=200
        )
        assert result["allowed"] is False
        assert "trust score" in result["reason"].lower()

    def test_high_utilization_with_sufficient_trust(self):
        gate = SpendingGate(high_util_trust_floor=500)
        result = gate.evaluate_spend(
            amount=50.0, utilization_band="high", agent_trust_score=700
        )
        assert result["allowed"] is True

    def test_high_value_requires_receipt(self):
        gate = SpendingGate()
        result = gate.evaluate_spend(amount=2000.0, agent_trust_score=500)
        assert result["allowed"] is False
        assert "receipt" in result["reason"].lower()

    def test_high_value_with_receipt(self):
        gate = SpendingGate()
        receipt = make_spending_receipt(amount=2000.0)
        result = gate.evaluate_spend(amount=2000.0, agent_trust_score=500, receipt=receipt)
        assert result["allowed"] is True

    def test_stats(self):
        gate = SpendingGate()
        gate.evaluate_spend(amount=50.0, agent_trust_score=500)
        gate.evaluate_spend(amount=25.0, agent_trust_score=500)
        stats = gate.get_stats()
        assert stats["total_requests"] == 2
        assert stats["allowed"] == 2
        assert stats["total_authorized_amount"] == 75.0


# ---- scopeblind_context ----


class TestScopeblindContext:
    def test_minimal_context(self):
        ctx = scopeblind_context()
        assert ctx["source"] == "scopeblind:protect-mcp"
        assert ctx["receipt"]["present"] is False

    def test_with_cedar_decision(self):
        decision = CedarDecision(effect="allow", tool_name="read_file", policy_ids=["p1"])
        ctx = scopeblind_context(cedar_decision=decision)
        assert ctx["cedar"]["effect"] == "allow"
        assert ctx["cedar"]["tool"] == "read_file"
        assert ctx["cedar"]["policy_ids"] == ["p1"]

    def test_with_receipt(self):
        receipt = make_receipt(effect="allow", tool="web_search")
        ctx = scopeblind_context(receipt=receipt)
        assert ctx["receipt"]["present"] is True
        assert ctx["receipt"]["issuer_blind"] is True
        assert ctx["receipt"]["type"] == "scopeblind:decision"

    def test_with_spending(self):
        ctx = scopeblind_context(spend_amount=99.50, spend_category="cloud", utilization_band="low")
        assert ctx["spending"]["amount"] == 99.50
        assert ctx["spending"]["category"] == "cloud"
        assert ctx["spending"]["utilization_band"] == "low"

    def test_full_context_shape(self):
        """Full context should be a flat dict compatible with AGT evaluate()."""
        decision = CedarDecision(effect="allow", tool_name="purchase")
        receipt = make_spending_receipt(amount=99.50)
        ctx = scopeblind_context(
            cedar_decision=decision,
            receipt=receipt,
            spend_amount=99.50,
            spend_category="cloud_compute",
            utilization_band="low",
        )
        assert "source" in ctx
        assert "cedar" in ctx
        assert "receipt" in ctx
        assert "spending" in ctx
        assert ctx["receipt"]["present"] is True
