class RiskEngine:
    def __init__(
        self,
        max_daily_loss: float = 5000.0,
        max_drawdown: float = 10000.0,
        max_lots_per_order: float = 100.0,
        leverage: float = 100.0
    ):
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_lots_per_order = max_lots_per_order
        self.leverage = leverage
        self._emergency_halt = False

    def trigger_emergency_halt(self):
        self._emergency_halt = True

    def reset_emergency_halt(self):
        self._emergency_halt = False

    def is_emergency_halted(self) -> bool:
        return self._emergency_halt

    def validate_order(
        self,
        account_equity: float,
        current_daily_loss: float,
        order_lot_size: float
    ) -> dict:
        if self._emergency_halt:
            return {"approved": False, "reason": "EMERGENCY_HALT_ACTIVE"}

        if current_daily_loss >= self.max_daily_loss:
            return {"approved": False, "reason": "MAX_DAILY_LOSS_EXCEEDED"}

        if order_lot_size > self.max_lots_per_order:
            return {"approved": False, "reason": f"EXCEEDS_MAX_LOT_SIZE_{self.max_lots_per_order}"}

        # Check required margin
        required_margin = (order_lot_size * 100000.0) / self.leverage
        if required_margin > account_equity:
            return {"approved": False, "reason": "INSUFFICIENT_MARGIN"}

        return {"approved": True, "reason": "APPROVED", "required_margin": required_margin}
