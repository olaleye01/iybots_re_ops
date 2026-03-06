# Copyright (c) 2026, Iybots and contributors
# For license information, please see license.txt
#
# Dashboard API endpoints for all three admin dashboards.
# All methods are whitelisted and respect Frappe's permission model.
# Agents see only their own data; managers/admins see all.

import frappe
from frappe import _
from frappe.utils import nowdate, add_months, getdate, date_diff, flt, cint
from datetime import date, timedelta
import calendar


# ── Permission helpers ────────────────────────────────────────────────────────

def _is_agent(user=None):
    user = user or frappe.session.user
    return "RE Agent" in frappe.get_roles(user)


def _agent_filter(user=None):
    """Returns a dict filter to restrict results to a specific agent if needed."""
    user = user or frappe.session.user
    if _is_agent(user):
        return user
    return None


# ── Date range helpers ────────────────────────────────────────────────────────

def _get_date_range(period="this_month"):
    """Returns (from_date, to_date) for the given period string."""
    today = getdate(nowdate())

    if period == "this_month":
        from_date = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        to_date = today.replace(day=last_day)

    elif period == "last_month":
        first_of_this = today.replace(day=1)
        last_month_end = first_of_this - timedelta(days=1)
        from_date = last_month_end.replace(day=1)
        to_date = last_month_end

    elif period == "this_quarter":
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        from_date = today.replace(month=q_start_month, day=1)
        q_end_month = q_start_month + 2
        last_day = calendar.monthrange(today.year, q_end_month)[1]
        to_date = today.replace(month=q_end_month, day=last_day)

    elif period == "this_year":
        from_date = today.replace(month=1, day=1)
        to_date = today.replace(month=12, day=31)

    elif period == "last_year":
        from_date = today.replace(year=today.year - 1, month=1, day=1)
        to_date = today.replace(year=today.year - 1, month=12, day=31)

    elif period == "last_90_days":
        from_date = today - timedelta(days=90)
        to_date = today

    elif period == "last_30_days":
        from_date = today - timedelta(days=30)
        to_date = today

    else:
        # Default: this month
        from_date = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        to_date = today.replace(day=last_day)

    return str(from_date), str(to_date)


def _get_prev_date_range(period="this_month"):
    """Returns the previous period of equal length for trend comparison."""
    from_date, to_date = _get_date_range(period)
    from_dt = getdate(from_date)
    to_dt = getdate(to_date)
    delta = (to_dt - from_dt).days + 1
    prev_to = from_dt - timedelta(days=1)
    prev_from = prev_to - timedelta(days=delta - 1)
    return str(prev_from), str(prev_to)


def _trend(current, previous):
    """Returns a trend dict with direction and percentage."""
    if not previous:
        return {"direction": "neutral", "pct": 0}
    change = current - previous
    pct = float(round((change / previous) * 100, 1))
    if pct > 0:
        direction = "up"
    elif pct < 0:
        direction = "down"
    else:
        direction = "neutral"
    return {"direction": direction, "pct": abs(pct)}


# ── RE Sales KPIs ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_sales_kpis(period="this_month"):
    """Returns KPI metrics for the RE Sales dashboard."""
    user = frappe.session.user
    agent = _agent_filter(user)
    from_date, to_date = _get_date_range(period)
    prev_from, prev_to = _get_prev_date_range(period)

    agent_cond = f"AND lead_owner = {frappe.db.escape(agent)}" if agent else ""
    opp_cond = f"AND opportunity_owner = {frappe.db.escape(agent)}" if agent else ""

    # Open leads (not Converted or Do Not Contact)
    open_leads = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabLead`
        WHERE status NOT IN ('Converted', 'Do Not Contact') {agent_cond}
    """)[0][0]

    prev_open_leads = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabLead`
        WHERE status NOT IN ('Converted', 'Do Not Contact')
        AND creation <= {frappe.db.escape(prev_to)} {agent_cond}
    """)[0][0]

    # Pipeline value (open opportunities)
    pipeline_value = frappe.db.sql(f"""
        SELECT COALESCE(SUM(opportunity_amount), 0) FROM `tabOpportunity`
        WHERE sales_stage NOT IN ('Closed Won', 'Closed Lost') {opp_cond}
    """)[0][0]

    prev_pipeline_value = frappe.db.sql(f"""
        SELECT COALESCE(SUM(opportunity_amount), 0) FROM `tabOpportunity`
        WHERE sales_stage NOT IN ('Closed Won', 'Closed Lost')
        AND creation <= {frappe.db.escape(prev_to)} {opp_cond}
    """)[0][0]

    # Won this period
    won_this = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(from_date)} AND {frappe.db.escape(to_date)} {opp_cond}
    """)[0][0]

    prev_won = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(prev_from)} AND {frappe.db.escape(prev_to)} {opp_cond}
    """)[0][0]

    # Conversion rate (trailing 90 days)
    t90_from = str(getdate(nowdate()) - timedelta(days=90))
    closed_data = frappe.db.sql(f"""
        SELECT
            SUM(CASE WHEN sales_stage = 'Closed Won' THEN 1 ELSE 0 END) as won,
            SUM(CASE WHEN sales_stage IN ('Closed Won', 'Closed Lost') THEN 1 ELSE 0 END) as total_closed
        FROM `tabOpportunity`
        WHERE sales_stage IN ('Closed Won', 'Closed Lost')
        AND modified >= {frappe.db.escape(t90_from)} {opp_cond}
    """, as_dict=True)[0]

    won_90 = cint(closed_data.won or 0)
    total_closed_90 = cint(closed_data.total_closed or 0)
    conversion_rate = round((won_90 / total_closed_90) * 100, 1) if total_closed_90 else 0

    prev_t90_from = str(getdate(t90_from) - timedelta(days=90))
    prev_closed = frappe.db.sql(f"""
        SELECT
            SUM(CASE WHEN sales_stage = 'Closed Won' THEN 1 ELSE 0 END) as won,
            SUM(CASE WHEN sales_stage IN ('Closed Won', 'Closed Lost') THEN 1 ELSE 0 END) as total_closed
        FROM `tabOpportunity`
        WHERE sales_stage IN ('Closed Won', 'Closed Lost')
        AND modified BETWEEN {frappe.db.escape(prev_t90_from)} AND {frappe.db.escape(t90_from)} {opp_cond}
    """, as_dict=True)[0]
    prev_won_90 = cint(prev_closed.won or 0)
    prev_total_90 = cint(prev_closed.total_closed or 0)
    prev_conversion = round((prev_won_90 / prev_total_90) * 100, 1) if prev_total_90 else 0

    # Average deal cycle (days from creation to Closed Won, trailing 90 days)
    avg_cycle_data = frappe.db.sql(f"""
        SELECT AVG(DATEDIFF(modified, creation)) as avg_days
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified >= {frappe.db.escape(t90_from)} {opp_cond}
    """, as_dict=True)[0]
    avg_deal_cycle = round(flt(avg_cycle_data.avg_days or 0))

    prev_avg_data = frappe.db.sql(f"""
        SELECT AVG(DATEDIFF(modified, creation)) as avg_days
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(prev_t90_from)} AND {frappe.db.escape(t90_from)} {opp_cond}
    """, as_dict=True)[0]
    prev_avg_cycle = round(flt(prev_avg_data.avg_days or 0))

    return {
        "open_leads": cint(open_leads),
        "open_leads_trend": _trend(cint(open_leads), cint(prev_open_leads)),
        "pipeline_value": flt(pipeline_value),
        "pipeline_value_trend": _trend(flt(pipeline_value), flt(prev_pipeline_value)),
        "won_this_period": cint(won_this),
        "won_this_period_trend": _trend(cint(won_this), cint(prev_won)),
        "conversion_rate": conversion_rate,
        "conversion_rate_trend": _trend(conversion_rate, prev_conversion),
        "avg_deal_cycle": avg_deal_cycle,
        "avg_deal_cycle_trend": _trend(avg_deal_cycle, prev_avg_cycle),
        "period": period,
    }


@frappe.whitelist()
def get_pipeline_stages(period="all"):
    """Returns opportunity counts and values per pipeline stage."""
    user = frappe.session.user
    agent = _agent_filter(user)
    opp_cond = f"WHERE opportunity_owner = {frappe.db.escape(agent)}" if agent else ""

    stages = ["Inquiry", "Site Visit", "Offer", "Payment Plan", "Closed Won"]
    results = frappe.db.sql(f"""
        SELECT sales_stage,
               COUNT(*) as count,
               COALESCE(SUM(opportunity_amount), 0) as value
        FROM `tabOpportunity`
        {opp_cond}
        GROUP BY sales_stage
    """, as_dict=True)

    stage_map = {r.sales_stage: r for r in results}
    output = []
    for stage in stages:
        d = stage_map.get(stage, {})
        output.append({
            "stage": stage,
            "count": cint(d.get("count", 0)),
            "value": flt(d.get("value", 0)),
        })

    closed_lost = stage_map.get("Closed Lost", {})
    return {
        "stages": output,
        "closed_lost_count": cint(closed_lost.get("count", 0)),
        "closed_lost_value": flt(closed_lost.get("value", 0)),
    }


@frappe.whitelist()
def get_lead_sources(period="all"):
    """Returns lead count grouped by source."""
    user = frappe.session.user
    agent = _agent_filter(user)
    cond = f"WHERE lead_owner = {frappe.db.escape(agent)}" if agent else ""

    results = frappe.db.sql(f"""
        SELECT COALESCE(NULLIF(source, ''), 'Unknown') as source,
               COUNT(*) as count
        FROM `tabLead`
        {cond}
        GROUP BY source
        ORDER BY count DESC
    """, as_dict=True)

    # Cap at 6 slices + Other
    top = results[:6]
    other_count = sum(r.count for r in results[6:])
    if other_count:
        top.append({"source": "Other", "count": other_count})

    total = sum(r.count for r in results)
    return {"sources": top, "total": total}


@frappe.whitelist()
def get_revenue_trend(months=12):
    """Returns monthly revenue from Closed Won opportunities."""
    user = frappe.session.user
    agent = _agent_filter(user)
    months = cint(months) or 12
    from_date = str(getdate(nowdate()).replace(day=1) - timedelta(days=30 * (months - 1)))
    opp_cond = f"AND opportunity_owner = {frappe.db.escape(agent)}" if agent else ""

    results = frappe.db.sql(f"""
        SELECT DATE_FORMAT(modified, '%Y-%m') as month,
               COALESCE(SUM(opportunity_amount), 0) as revenue
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified >= {frappe.db.escape(from_date)}
        {opp_cond}
        GROUP BY month
        ORDER BY month
    """, as_dict=True)

    return {"data": results}


@frappe.whitelist()
def get_agent_leaderboard(period="this_month", limit=5):
    """Returns agent performance ranked by deals won."""
    from_date, to_date = _get_date_range(period)
    limit = cint(limit) or 5

    won = frappe.db.sql(f"""
        SELECT opportunity_owner,
               COUNT(*) as deals_won,
               COALESCE(SUM(opportunity_amount), 0) as won_value
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(from_date)} AND {frappe.db.escape(to_date)}
        GROUP BY opportunity_owner
        ORDER BY deals_won DESC
        LIMIT {limit}
    """, as_dict=True)

    pipeline = frappe.db.sql("""
        SELECT opportunity_owner,
               COALESCE(SUM(opportunity_amount), 0) as pipeline_value
        FROM `tabOpportunity`
        WHERE sales_stage NOT IN ('Closed Won', 'Closed Lost')
        GROUP BY opportunity_owner
    """, as_dict=True)
    pipeline_map = {r.opportunity_owner: flt(r.pipeline_value) for r in pipeline}

    lost = frappe.db.sql(f"""
        SELECT opportunity_owner, COUNT(*) as deals_lost
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Lost'
        AND modified BETWEEN {frappe.db.escape(from_date)} AND {frappe.db.escape(to_date)}
        GROUP BY opportunity_owner
    """, as_dict=True)
    lost_map = {r.opportunity_owner: cint(r.deals_lost) for r in lost}

    output = []
    for i, r in enumerate(won, 1):
        agent_name = frappe.db.get_value("User", r.opportunity_owner, "full_name") or r.opportunity_owner
        deals_won = cint(r.deals_won)
        deals_lost = lost_map.get(r.opportunity_owner, 0)
        total_closed = deals_won + deals_lost
        conv = round((deals_won / total_closed) * 100, 1) if total_closed else 0
        output.append({
            "rank": i,
            "agent": r.opportunity_owner,
            "agent_name": agent_name,
            "deals_won": deals_won,
            "pipeline_value": pipeline_map.get(r.opportunity_owner, 0),
            "conversion_rate": conv,
        })

    return {"leaderboard": output}


@frappe.whitelist()
def get_recent_deals(limit=10):
    """Returns the most recently modified opportunities."""
    user = frappe.session.user
    agent = _agent_filter(user)
    limit = cint(limit) or 10
    opp_cond = f"WHERE opportunity_owner = {frappe.db.escape(agent)}" if agent else ""

    results = frappe.db.sql(f"""
        SELECT name, customer_name, opportunity_from, party_name,
               opportunity_amount, sales_stage, opportunity_owner, modified,
               property_link
        FROM `tabOpportunity`
        {opp_cond}
        ORDER BY modified DESC
        LIMIT {limit}
    """, as_dict=True)

    output = []
    for r in results:
        client = r.get("customer_name") or r.get("party_name") or ""
        agent_name = frappe.db.get_value("User", r.opportunity_owner, "full_name") or r.opportunity_owner
        output.append({
            "name": r.name,
            "client": client,
            "property": r.get("property_link") or "",
            "stage": r.get("sales_stage") or "",
            "value": flt(r.get("opportunity_amount") or 0),
            "agent": agent_name,
            "modified": str(r.modified) if r.modified else "",
        })

    return {"deals": output}


# ── CEO Dashboard KPIs ────────────────────────────────────────────────────────

@frappe.whitelist()
def get_executive_kpis(period="this_month"):
    """Returns executive-level KPIs for the CEO Dashboard."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    from_date, to_date = _get_date_range(period)
    prev_from, prev_to = _get_prev_date_range(period)
    today = nowdate()

    # Total revenue (all time)
    total_revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(opportunity_amount), 0) FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
    """)[0][0]

    # Monthly revenue (current period)
    monthly_revenue = frappe.db.sql(f"""
        SELECT COALESCE(SUM(opportunity_amount), 0) FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(from_date)} AND {frappe.db.escape(to_date)}
    """)[0][0]

    prev_monthly = frappe.db.sql(f"""
        SELECT COALESCE(SUM(opportunity_amount), 0) FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified BETWEEN {frappe.db.escape(prev_from)} AND {frappe.db.escape(prev_to)}
    """)[0][0]

    # Active deals
    active_deals = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabOpportunity`
        WHERE sales_stage NOT IN ('Closed Won', 'Closed Lost')
    """)[0][0]

    prev_active = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabOpportunity`
        WHERE sales_stage NOT IN ('Closed Won', 'Closed Lost')
        AND creation <= {frappe.db.escape(prev_to)}
    """)[0][0]

    # Overdue payments
    overdue_count = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabPayment Milestone`
        WHERE status = 'Overdue'
    """)[0][0]

    # Total properties
    total_props = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabProperty`
    """)[0][0]

    avail_props = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabProperty` WHERE status = 'Available'
    """)[0][0]

    sold_props = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabProperty` WHERE status = 'Sold'
    """)[0][0]

    # Active agents (with activity in last 30 days)
    thirty_days_ago = str(getdate(today) - timedelta(days=30))
    active_agents = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT opportunity_owner) FROM `tabOpportunity`
        WHERE modified >= {frappe.db.escape(thirty_days_ago)}
    """)[0][0]

    total_agents = frappe.db.sql("""
        SELECT COUNT(DISTINCT parent) FROM `tabHas Role`
        WHERE role = 'RE Agent' AND parenttype = 'User'
    """)[0][0]

    return {
        "total_revenue": flt(total_revenue),
        "monthly_revenue": flt(monthly_revenue),
        "monthly_revenue_trend": _trend(flt(monthly_revenue), flt(prev_monthly)),
        "active_deals": cint(active_deals),
        "active_deals_trend": _trend(cint(active_deals), cint(prev_active)),
        "overdue_payments": cint(overdue_count),
        "total_properties": cint(total_props),
        "available_properties": cint(avail_props),
        "sold_properties": cint(sold_props),
        "active_agents": cint(active_agents),
        "total_agents": cint(total_agents),
        "period": period,
    }


@frappe.whitelist()
def get_revenue_over_time(months=12):
    """Returns monthly closed-won revenue for the CEO chart."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    months = cint(months) or 12
    from_date = str(getdate(nowdate()).replace(day=1) - timedelta(days=30 * (months - 1)))

    results = frappe.db.sql(f"""
        SELECT DATE_FORMAT(modified, '%Y-%m') as month,
               COALESCE(SUM(opportunity_amount), 0) as revenue
        FROM `tabOpportunity`
        WHERE sales_stage = 'Closed Won'
        AND modified >= {frappe.db.escape(from_date)}
        GROUP BY month
        ORDER BY month
    """, as_dict=True)

    return {"data": results}


@frappe.whitelist()
def get_collection_health(months=6):
    """Returns monthly collected vs outstanding payment amounts."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    months = cint(months) or 6
    from_date = str(getdate(nowdate()).replace(day=1) - timedelta(days=30 * (months - 1)))

    results = frappe.db.sql(f"""
        SELECT DATE_FORMAT(due_date, '%Y-%m') as month,
               COALESCE(SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 0) as collected,
               COALESCE(SUM(CASE WHEN status != 'Paid' THEN amount ELSE 0 END), 0) as outstanding,
               COALESCE(SUM(amount), 0) as total
        FROM `tabPayment Milestone`
        WHERE due_date >= {frappe.db.escape(from_date)}
        GROUP BY month
        ORDER BY month
    """, as_dict=True)

    # Current month collection rate
    this_month_from, this_month_to = _get_date_range("this_month")
    cm = frappe.db.sql(f"""
        SELECT COALESCE(SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 0) as collected,
               COALESCE(SUM(amount), 0) as total
        FROM `tabPayment Milestone`
        WHERE due_date BETWEEN {frappe.db.escape(this_month_from)} AND {frappe.db.escape(this_month_to)}
    """, as_dict=True)[0]

    cm_collected = flt(cm.collected)
    cm_total = flt(cm.total)
    collection_rate = round((cm_collected / cm_total) * 100, 1) if cm_total else 0

    return {"data": results, "collection_rate_this_month": collection_rate}


@frappe.whitelist()
def get_property_breakdown():
    """Returns property count by status."""
    frappe.only_for(["MD", "RE Admin", "System Manager", "RE Agent"])

    results = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabProperty`
        GROUP BY status
    """, as_dict=True)

    breakdown = {r.status: cint(r.count) for r in results}
    total = sum(breakdown.values())

    return {
        "available": breakdown.get("Available", 0),
        "reserved": breakdown.get("Reserved", 0),
        "sold": breakdown.get("Sold", 0),
        "total": total,
    }


@frappe.whitelist()
def get_pipeline_summary():
    """Returns compact pipeline stage counts for the CEO mini-funnel."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])

    stages = ["Inquiry", "Site Visit", "Offer", "Payment Plan", "Closed Won"]
    results = frappe.db.sql("""
        SELECT sales_stage,
               COUNT(*) as count,
               COALESCE(SUM(opportunity_amount), 0) as value
        FROM `tabOpportunity`
        GROUP BY sales_stage
    """, as_dict=True)

    stage_map = {r.sales_stage: r for r in results}
    output = []
    for stage in stages:
        d = stage_map.get(stage, {})
        output.append({
            "stage": stage,
            "count": cint(d.get("count", 0)),
            "value": flt(d.get("value", 0)),
        })

    open_value = sum(
        flt(stage_map.get(s, {}).get("value", 0))
        for s in stages if s not in ("Closed Won", "Closed Lost")
    )

    return {"stages": output, "total_pipeline_value": open_value}


@frappe.whitelist()
def get_commission_summary():
    """Returns commission totals for the CEO dashboard."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])

    data = frappe.db.sql("""
        SELECT
            COALESCE(SUM(CASE WHEN status = 'Paid' THEN commission_amount ELSE 0 END), 0) as total_paid,
            COALESCE(SUM(CASE WHEN status IN ('Draft', 'Approved') THEN commission_amount ELSE 0 END), 0) as pending_amount,
            SUM(CASE WHEN status IN ('Draft', 'Approved') THEN 1 ELSE 0 END) as pending_count
        FROM `tabCommission Record`
    """, as_dict=True)[0]

    return {
        "total_paid": flt(data.total_paid),
        "pending_amount": flt(data.pending_amount),
        "pending_count": cint(data.pending_count),
    }


@frappe.whitelist()
def get_alerts():
    """Returns alert items for the CEO dashboard alerts panel."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])

    alerts = []
    today = getdate(nowdate())

    # 1. Overdue payments
    overdue_count = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabPayment Milestone` WHERE status = 'Overdue'
    """)[0][0]
    if cint(overdue_count):
        alerts.append({
            "type": "overdue_payments",
            "severity": "critical",
            "label": "Overdue Payments",
            "count": cint(overdue_count),
            "link": "/app/query-report/Overdue Payments",
            "icon": "alert-triangle",
        })

    # 2. Stale leads (no activity in 14+ days)
    stale_cutoff = str(today - timedelta(days=14))
    stale_count = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabLead`
        WHERE status NOT IN ('Converted', 'Do Not Contact')
        AND modified < {frappe.db.escape(stale_cutoff)}
    """)[0][0]
    if cint(stale_count):
        alerts.append({
            "type": "stale_leads",
            "severity": "warning",
            "label": "Stale Leads (14+ days inactive)",
            "count": cint(stale_count),
            "link": "/app/lead?status=Open",
            "icon": "clock",
        })

    # 3. Pending commissions
    pending_comm = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabCommission Record` WHERE status = 'Draft'
    """)[0][0]
    if cint(pending_comm):
        alerts.append({
            "type": "pending_commissions",
            "severity": "caution",
            "label": "Commissions Awaiting Approval",
            "count": cint(pending_comm),
            "link": "/app/commission-record?status=Draft",
            "icon": "coins",
        })

    # 4. Upcoming milestones (due in next 7 days)
    next_7 = str(today + timedelta(days=7))
    upcoming = frappe.db.sql(f"""
        SELECT COUNT(*) FROM `tabPayment Milestone`
        WHERE status = 'Pending'
        AND due_date BETWEEN {frappe.db.escape(str(today))} AND {frappe.db.escape(next_7)}
    """)[0][0]
    if cint(upcoming):
        alerts.append({
            "type": "upcoming_milestones",
            "severity": "info",
            "label": "Payment Milestones Due This Week",
            "count": cint(upcoming),
            "link": "/app/payment-plan",
            "icon": "calendar",
        })

    # 5. Agent check-in gaps (no check-in in 3+ days)
    checkin_cutoff = str(today - timedelta(days=3))
    all_agents = frappe.db.sql("""
        SELECT COUNT(DISTINCT parent) FROM `tabHas Role`
        WHERE role = 'RE Agent' AND parenttype = 'User'
    """)[0][0]
    active_checkin = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT agent) FROM `tabAgent Check-in`
        WHERE check_in_time >= {frappe.db.escape(checkin_cutoff)}
    """)[0][0]
    gap_count = max(0, cint(all_agents) - cint(active_checkin))
    if gap_count:
        alerts.append({
            "type": "checkin_gaps",
            "severity": "neutral",
            "label": "Agents with No Check-in (3+ days)",
            "count": gap_count,
            "link": "/app/agent-check-in",
            "icon": "map-pin-off",
        })

    return {"alerts": alerts}


# ── RE Operations KPIs ────────────────────────────────────────────────────────

@frappe.whitelist()
def get_operations_kpis():
    """Returns KPI metrics for RE Operations dashboard."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])

    total_props = frappe.db.sql("SELECT COUNT(*) FROM `tabProperty`")[0][0]
    avail_units = frappe.db.sql("SELECT COUNT(*) FROM `tabProperty` WHERE status = 'Available'")[0][0]
    overdue_count = frappe.db.sql("SELECT COUNT(*) FROM `tabPayment Milestone` WHERE status = 'Overdue'")[0][0]

    # Collection rate this month
    from_date, to_date = _get_date_range("this_month")
    cm = frappe.db.sql(f"""
        SELECT COALESCE(SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 0) as collected,
               COALESCE(SUM(amount), 0) as total
        FROM `tabPayment Milestone`
        WHERE due_date BETWEEN {frappe.db.escape(from_date)} AND {frappe.db.escape(to_date)}
    """, as_dict=True)[0]

    cm_collected = flt(cm.collected)
    cm_total = flt(cm.total)
    collection_rate = round((cm_collected / cm_total) * 100, 1) if cm_total else 0

    return {
        "total_properties": cint(total_props),
        "available_units": cint(avail_units),
        "overdue_payments": cint(overdue_count),
        "collection_rate": collection_rate,
    }


@frappe.whitelist()
def get_estate_projects():
    """Returns estate project summaries with unit counts."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])

    projects = frappe.db.sql("""
        SELECT name, project_name, location, status
        FROM `tabEstate Project`
        ORDER BY creation DESC
    """, as_dict=True)

    output = []
    for p in projects:
        counts = frappe.db.sql(f"""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) as available,
                SUM(CASE WHEN status = 'Sold' THEN 1 ELSE 0 END) as sold,
                SUM(CASE WHEN status = 'Reserved' THEN 1 ELSE 0 END) as reserved
            FROM `tabProperty`
            WHERE project = {frappe.db.escape(p.name)}
        """, as_dict=True)[0]

        total = cint(counts.total)
        sold = cint(counts.sold)
        available = cint(counts.available)
        reserved = cint(counts.reserved)
        sold_pct = round((sold / total) * 100) if total else 0

        output.append({
            "name": p.name,
            "project_name": p.project_name,
            "location": p.location or "",
            "status": p.status,
            "total_units": total,
            "sold_units": sold,
            "available_units": available,
            "reserved_units": reserved,
            "sold_pct": sold_pct,
        })

    return {"projects": output}


@frappe.whitelist()
def get_overdue_payments(limit=10):
    """Returns the most critical overdue payment milestones."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    limit = cint(limit) or 10

    results = frappe.db.sql(f"""
        SELECT pm.name, pm.due_date, pm.amount,
               DATEDIFF(CURDATE(), pm.due_date) as days_overdue,
               pp.name as plan_name, pp.customer, pp.property
        FROM `tabPayment Milestone` pm
        JOIN `tabPayment Plan` pp ON pm.parent = pp.name
        WHERE pm.status = 'Overdue'
        ORDER BY days_overdue DESC
        LIMIT {limit}
    """, as_dict=True)

    output = []
    for r in results:
        client_name = ""
        if r.customer:
            client_name = frappe.db.get_value("Customer", r.customer, "customer_name") or r.customer

        prop_name = ""
        if r.property:
            prop_name = frappe.db.get_value("Property", r.property, "property_name") or r.property

        output.append({
            "milestone": r.name,
            "plan_name": r.plan_name,
            "client": client_name or r.customer or "",
            "property": prop_name or r.property or "",
            "amount": flt(r.amount),
            "due_date": str(r.due_date) if r.due_date else "",
            "days_overdue": cint(r.days_overdue),
        })

    total_overdue = frappe.db.sql("SELECT COUNT(*) FROM `tabPayment Milestone` WHERE status = 'Overdue'")[0][0]
    return {"payments": output, "total_overdue": cint(total_overdue)}


@frappe.whitelist()
def get_collection_trend(months=6):
    """Returns monthly collection trend for RE Operations."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    months = cint(months) or 6
    from_date = str(getdate(nowdate()).replace(day=1) - timedelta(days=30 * (months - 1)))

    results = frappe.db.sql(f"""
        SELECT DATE_FORMAT(due_date, '%Y-%m') as month,
               COALESCE(SUM(CASE WHEN status = 'Paid' THEN amount ELSE 0 END), 0) as collected,
               COALESCE(SUM(amount), 0) as total
        FROM `tabPayment Milestone`
        WHERE due_date >= {frappe.db.escape(from_date)}
        GROUP BY month
        ORDER BY month
    """, as_dict=True)

    return {"data": results}


@frappe.whitelist()
def get_recent_checkins(limit=10):
    """Returns the most recent agent check-ins."""
    frappe.only_for(["MD", "RE Admin", "System Manager"])
    limit = cint(limit) or 10

    results = frappe.db.sql(f"""
        SELECT name, agent, check_in_time, location_name, latitude, longitude, notes
        FROM `tabAgent Check-in`
        ORDER BY check_in_time DESC
        LIMIT {limit}
    """, as_dict=True)

    output = []
    for r in results:
        agent_name = frappe.db.get_value("User", r.agent, "full_name") or r.agent
        output.append({
            "name": r.name,
            "agent": r.agent,
            "agent_name": agent_name,
            "check_in_time": str(r.check_in_time) if r.check_in_time else "",
            "location_name": r.location_name or "",
            "latitude": flt(r.latitude or 0),
            "longitude": flt(r.longitude or 0),
            "notes": r.notes or "",
        })

    return {"checkins": output}
