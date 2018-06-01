ts = [
    "null",
    "base",
    "account",
    "asset",
    "force_settlement",
    "committee_member",
    "witness",
    "limit_order",
    "call_order",
    "custom",
    "proposal",
    "operation_history",
    "withdraw_permission",
    "vesting_balance",
    "worker",
    "balance"
]

object_type = {k: ts.index(k) for k in ts}
