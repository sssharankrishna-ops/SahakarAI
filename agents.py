"""SahakarAI's modular, deterministic agents for the hackathon demo."""
from statistics import mean
from decimal import Decimal, ROUND_HALF_UP


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


class ForecastingAgent:
    def forecast(self, values, horizon=1, seasonal_adjustment=1.0):
        clean = [float(x) for x in values if x is not None]
        if not clean:
            return {"forecast": 0, "method": "No data", "warning": "Add historical demand before forecasting."}
        window = clean[-3:] if len(clean) >= 3 else clean
        base = mean(window)
        prediction = max(0, round(base * float(seasonal_adjustment) * max(1, int(horizon))))
        return {"forecast": prediction, "method": f"Mean of last {len(window)} periods × seasonal adjustment × horizon", "warning": "Illustrative baseline; not a validated market prediction." if len(clean) < 12 else "Baseline forecast; validate against held-out periods."}


class AggregationAgent:
    def allocate(self, weavers, product, quantity, quality=None):
        remaining = int(quantity)
        candidates = []
        for w in weavers:
            if w.get('product') != product or w.get('status', 'Active') != 'Active':
                continue
            if quality and quality != 'Any' and w.get('quality', 'Standard') != quality:
                continue
            available = max(0, int(w.get('capacity', 0)) - int(w.get('committed', 0)))
            if available:
                candidates.append({**w, 'available': available})
        # Fair-ish greedy: lower cost first, then lower current utilisation.
        candidates.sort(key=lambda w: (float(w['unit_cost']), int(w.get('committed', 0))))
        allocations, total_cost = [], 0.0
        for w in candidates:
            if remaining <= 0:
                break
            qty = min(remaining, w['available'])
            allocations.append({"weaver_id": w['id'], "name": w['name'], "quantity": qty,
                                "unit_cost": float(w['unit_cost']), "line_cost": money(qty * float(w['unit_cost'])),
                                "available": w['available'], "reason": f"Eligible for {product}; {w['available']} units available; selected by cost/capacity ordering."})
            total_cost += qty * float(w['unit_cost'])
            remaining -= qty
        return {"feasible": remaining == 0, "requested": int(quantity), "allocated": int(quantity)-remaining,
                "shortage": remaining, "allocations": allocations, "production_cost": money(total_cost)}


class PricingEngine:
    def calculate(self, allocations, shared_expenses=0, markup=0.10, min_compensation_markup=0.0):
        production = sum(float(a['line_cost']) for a in allocations)
        units = sum(int(a['quantity']) for a in allocations)
        shared = float(shared_expenses)
        total = production + shared
        floor = total / units if units else 0
        target = total * (1 + float(markup))
        rows = []
        for a in allocations:
            cost = float(a['unit_cost'])
            allocated_shared = shared * int(a['quantity']) / units if units else 0
            per_unit_cost = cost + allocated_shared / int(a['quantity']) if a['quantity'] else cost
            minimum = cost * (1 + float(min_compensation_markup))
            rows.append({**a, "shared_cost": money(allocated_shared), "effective_unit_cost": money(per_unit_cost),
                         "minimum_compensation_per_unit": money(minimum)})
        return {"production_cost": money(production), "shared_expenses": money(shared), "total_cost": money(total),
                "units": units, "break_even_unit": money(floor), "target_total": money(target),
                "target_unit": money(target/units if units else 0), "allocations": rows}


class NegotiationAgent:
    def evaluate(self, offer_per_unit, pricing, payment_days=30, delivery_feasible=True, policy_max_payment_days=45):
        offer = float(offer_per_unit)
        units = int(pricing.get('units', 0))
        total_offer = offer * units
        below_floor = offer + 1e-9 < float(pricing.get('break_even_unit', 0))
        below_target = offer + 1e-9 < float(pricing.get('target_unit', 0))
        long_payment = int(payment_days) > int(policy_max_payment_days)
        reasons = []
        if below_floor: reasons.append("Offer is below aggregate break-even price.")
        elif below_target: reasons.append("Offer covers estimated cost but is below the cooperative target price.")
        if long_payment: reasons.append(f"Payment delay ({payment_days} days) exceeds policy limit ({policy_max_payment_days} days).")
        if not delivery_feasible: reasons.append("Delivery feasibility has not been established.")
        escalate = long_payment or not delivery_feasible
        if below_floor:
            action = "COUNTEROFFER"
            message = f"Thank you for the offer. Our estimated break-even price is ₹{pricing['break_even_unit']:,.2f} per unit, before target markup. We propose ₹{pricing['target_unit']:,.2f} per unit, subject to final approval."
        elif escalate:
            action = "HUMAN_REVIEW"
            message = "The price may be viable, but payment or delivery terms require review by an authorised cooperative officer before any commitment."
        elif below_target:
            action = "COUNTEROFFER"
            message = f"Thank you. Based on verified order costs and the cooperative's target policy, we propose ₹{pricing['target_unit']:,.2f} per unit. We can discuss delivery and payment terms."
        else:
            action = "WITHIN_LIMITS"
            message = "The offer meets the configured cost and target checks. Submit it for the cooperative's authorised approval before confirming any agreement."
        return {"action": action, "offer_per_unit": money(offer), "total_offer": money(total_offer),
                "estimated_profit": money(total_offer - float(pricing.get('total_cost', 0))),
                "below_floor": below_floor, "below_target": below_target, "escalate": escalate,
                "reasons": reasons or ["No configured pricing or payment rule was breached."], "message": message}
