/**
 * RE Sales Dashboard — Frappe Custom Page
 * Renders KPI cards, pipeline funnel, lead source chart,
 * revenue trend, agent leaderboard, and recent deals.
 */

frappe.pages["re-sales-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "RE Sales",
		single_column: true,
	});

	// Store page reference for refresh
	wrapper._dashboard_page = page;

	$(wrapper).find(".page-content").addClass("iybots-dashboard");

	page.set_primary_action("New Lead", function () {
		frappe.new_doc("Lead");
	}, "plus");

	page.add_menu_item("New Opportunity", function () {
		frappe.new_doc("Opportunity");
	});

	page.add_menu_item("View All Deals", function () {
		frappe.set_route("List", "Opportunity");
	});

	_render_sales_dashboard(wrapper, page, "this_month");
};

frappe.pages["re-sales-dashboard"].on_page_show = function (wrapper) {
	// No auto-refresh on show to avoid flickering; user can use menu
};

function _render_sales_dashboard(wrapper, page, period) {
	var DB = window.IybotsDashboard;
	var $main = $(wrapper).find(".page-content");

	$main.html(`
		<div id="db-kpi-row" class="db-grid db-grid-5"></div>
		<div class="db-grid db-grid-2">
			<div id="db-funnel-card"></div>
			<div id="db-source-card"></div>
		</div>
		<div class="db-grid db-grid-2">
			<div id="db-revenue-card"></div>
			<div id="db-leaderboard-card"></div>
		</div>
		<div id="db-deals-card"></div>
	`);

	// ── Loading skeletons ─────────────────────────────────────────────────
	DB.renderSkeletonGrid(document.getElementById("db-kpi-row"), 5, "kpi");

	document.getElementById("db-funnel-card").innerHTML =
		`<div class="db-card db-skeleton db-skeleton-chart"></div>`;
	document.getElementById("db-source-card").innerHTML =
		`<div class="db-card db-skeleton db-skeleton-chart"></div>`;
	document.getElementById("db-revenue-card").innerHTML =
		`<div class="db-card db-skeleton db-skeleton-chart"></div>`;
	document.getElementById("db-leaderboard-card").innerHTML =
		`<div class="db-card db-skeleton db-skeleton-table"></div>`;
	document.getElementById("db-deals-card").innerHTML =
		`<div class="db-card db-skeleton db-skeleton-table"></div>`;

	// ── KPI Cards ─────────────────────────────────────────────────────────
	DB.call("get_sales_kpis", { period: period }, function (data) {
		var $row = document.getElementById("db-kpi-row");
		$row.innerHTML = [
			DB.renderKpiCard({
				icon: "user-plus", iconColor: "blue",
				label: "Open Leads",
				value: data.open_leads.toLocaleString(),
				trend: data.open_leads_trend,
				subtext: "vs. last period",
			}),
			DB.renderKpiCard({
				icon: "trending-up", iconColor: "purple",
				label: "Pipeline Value",
				value: DB.formatNaira(data.pipeline_value),
				trend: data.pipeline_value_trend,
				subtext: "open opportunities",
			}),
			DB.renderKpiCard({
				icon: "trophy", iconColor: "green",
				label: "Won This Period",
				value: data.won_this_period.toLocaleString(),
				trend: data.won_this_period_trend,
				subtext: "vs. last period",
			}),
			DB.renderKpiCard({
				icon: "target", iconColor: "orange",
				label: "Conversion Rate",
				value: data.conversion_rate + "%",
				trend: data.conversion_rate_trend,
				subtext: "trailing 90 days",
			}),
			DB.renderKpiCard({
				icon: "clock", iconColor: "blue",
				label: "Avg Deal Cycle",
				value: data.avg_deal_cycle + " days",
				trend: { direction: data.avg_deal_cycle_trend.direction === "down" ? "up" : data.avg_deal_cycle_trend.direction === "up" ? "down" : "neutral", pct: data.avg_deal_cycle_trend.pct },
				subtext: "trailing 90 days",
			}),
		].join("");
	}, function () {
		document.getElementById("db-kpi-row").innerHTML =
			`<div class="db-card" style="grid-column:1/-1;padding:20px;color:#DC2626">${DB.errorState("Failed to load KPIs")}</div>`;
	});

	// ── Pipeline Funnel ───────────────────────────────────────────────────
	DB.call("get_pipeline_stages", {}, function (data) {
		document.getElementById("db-funnel-card").innerHTML = DB.renderChartCard({
			title: "Sales Pipeline",
			chartId: "db-funnel-inner",
			action: "View All",
			actionLink: "/app/opportunity",
		});
		DB.renderFunnel(document.getElementById("db-funnel-inner"), data.stages);
	}, function () {
		document.getElementById("db-funnel-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load pipeline")}</div>`;
	});

	// ── Lead Sources Donut ────────────────────────────────────────────────
	DB.call("get_lead_sources", {}, function (data) {
		document.getElementById("db-source-card").innerHTML = DB.renderChartCard({
			title: "Lead Sources",
			chartId: "db-source-inner",
			action: "View All Leads",
			actionLink: "/app/lead",
		});
		if (data.sources && data.sources.length) {
			DB.renderDonut(
				"db-source-inner",
				data.sources.map(function (s) { return s.source; }),
				data.sources.map(function (s) { return s.count; })
			);
		} else {
			document.getElementById("db-source-inner").innerHTML = DB.emptyState("No lead source data");
		}
	}, function () {
		document.getElementById("db-source-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load lead sources")}</div>`;
	});

	// ── Revenue Trend ─────────────────────────────────────────────────────
	DB.call("get_revenue_trend", { months: 6 }, function (data) {
		document.getElementById("db-revenue-card").innerHTML = DB.renderChartCard({
			title: "Revenue Trend (Closed Won)",
			chartId: "db-revenue-inner",
			action: "View All",
			actionLink: "/app/opportunity?sales_stage=Closed Won",
		});
		if (data.data && data.data.length) {
			DB.renderBarChart(
				"db-revenue-inner",
				data.data.map(function (d) { return DB.monthLabel(d.month); }),
				data.data.map(function (d) { return parseFloat(d.revenue) || 0; }),
				{
					seriesName: "Revenue",
					formatY: function (v) { return DB.formatNaira(v); },
					height: 240,
				}
			);
		} else {
			document.getElementById("db-revenue-inner").innerHTML = DB.emptyState("No revenue data yet");
		}
	}, function () {
		document.getElementById("db-revenue-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load revenue trend")}</div>`;
	});

	// ── Agent Leaderboard ─────────────────────────────────────────────────
	DB.call("get_agent_leaderboard", { period: period, limit: 5 }, function (data) {
		document.getElementById("db-leaderboard-card").innerHTML = DB.renderTableCard({
			title: "Agent Leaderboard",
			tableId: "db-leaderboard-inner",
			action: "View All Agents",
			actionLink: "/app/commission-record",
		});
		DB.renderLeaderboard(document.getElementById("db-leaderboard-inner"), data.leaderboard);
	}, function () {
		document.getElementById("db-leaderboard-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load leaderboard")}</div>`;
	});

	// ── Recent Deals ──────────────────────────────────────────────────────
	DB.call("get_recent_deals", { limit: 10 }, function (data) {
		document.getElementById("db-deals-card").innerHTML = DB.renderTableCard({
			title: "Recent Deals",
			tableId: "db-deals-inner",
			action: "View All Deals",
			actionLink: "/app/opportunity",
		});
		DB.renderRecentDeals(document.getElementById("db-deals-inner"), data.deals);
	}, function () {
		document.getElementById("db-deals-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load recent deals")}</div>`;
	});
}
