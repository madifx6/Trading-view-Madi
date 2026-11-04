# Execution Safety & Risk Audit

## Non-Bypassable Risk Controls
All paper order submission routes enforce `RiskEngine.validate_order()`:
1. **Idempotency Protection:** Re-submitting an identical `idempotency_key` is rejected with `DUPLICATE_IDEMPOTENCY_KEY`.
2. **Margin Verification:** Orders requiring more margin than available equity are rejected with `INSUFFICIENT_MARGIN`.
3. **Daily Loss Ceiling:** Orders submitted after daily drawdown hits the threshold are rejected with `MAX_DAILY_LOSS_EXCEEDED`.
4. **Emergency Kill-Switch:** When `is_emergency_halted()` is True, all trading actions are blocked with `EMERGENCY_HALT_ACTIVE`.
