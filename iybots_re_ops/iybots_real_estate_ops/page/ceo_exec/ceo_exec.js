/**
 * CEO Dashboard — Frappe Custom Page
 * Route: /app/ceo-exec
 */

frappe.pages["ceo-exec"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Business Overview",
		single_column: true,
	});

	$(wrapper).find(".page-content").addClass("iybots-dashboard");

	page.add_menu_item("RE Sales Dashboard", function () {
		frappe.set_route("re-sales-dashboard");
	});

	page.add_menu_item("RE Operations Dashboard", function () {
		frappe.set_route("re-operations-dashboard");
	});

	page.add_menu_item("View Commission Records", function () {
		frappe.set_route("List", "Commission Record");
	});

	_render_ceo_dashboard(wrapper, page, "this_month");
};

function _render_ceo_dashboard(wrapper, page, period) {
	var DB = window.IybotsDashboard;
	var $main = $(wrapper).find(".page-content");

	$main.html(`
		<div id="ceo-kpi-row" class="db-grid db-grid-6"></div>
		<div class="db-grid db-grid-2">
			<div id="ceo-revenue-card"></div>
			<div id="ceo-collection-card"></div>
		</div>
		<div class="db-grid db-grid-3">
			<div id="ceo-property-card"></div>
			<div id="ceo-pipeline-card"></div>
			<div id="ceo-commission-card"></div>
		</div>
		<div class="db-grid db-grid-2">
			<div id="ceo-leaderboard-card"></div>
			<div id="ceo-alerts-card"></div>
		</div>
	`);

	// ── Loading skeletons ─────────────────────────────────────────────────
	DB.renderSkeletonGrid(document.getElementById("ceo-kpi-row"), 6, "kpi");
	["ceo-revenue-card", "ceo-collection-card"].forEach(function (id) {
		document.getElementById(id).innerHTML =
			`<div class="db-card db-skeleton db-skeleton-chart"></div>`;
	});
	["ceo-property-card", "ceo-pipeline-card", "ceo-commission-card",
	 "ceo-leaderboard-card", "ceo-alerts-card"].forEach(function (id) {
		document.getElementById(id).innerHTML =
			`<div class="db-card db-skeleton db-skeleton-table"></div>`;
	});

	// ── Executive KPI Cards ───────────────────────────────────────────────
	DB.call("get_executive_kpis", { period: period }, function (data) {
		var $row = document.getElementById("ceo-kpi-row");
		$row.innerHTML = [
			DB.renderKpiCard({
				icon: "banknote", iconColor: "green",
				label: "Total Revenue",
				value: DB.formatNaira(data.total_revenue),
				subtext: "all time",
			}),
			DB.renderKpiCard({
				icon: "calendar-check", iconColor: "blue",
				label: "Monthly Revenue",
				value: DB.formatNaira(data.monthly_revenue),
				trend: data.monthly_revenue_trend,
				subtext: "vs. last period",
			}),
			DB.renderKpiCard({
				icon: "handshake", iconColor: "purple",
				label: "Active Deals",
				value: data.active_deals.toLocaleString(),
				trend: data.active_deals_trend,
				subtext: "in pipeline",
			}),
			DB.renderKpiCard({
				icon: "alert-circle", iconColor: data.overdue_payments > 0 ? "red" : "green",
				label: "Overdue Payments",
				value: data.overdue_payments.toLocaleString(),
				isDanger: data.overdue_payments > 0,
				subtext: "require action",
			}),
			DB.renderKpiCard({
				icon: "building-2", iconColor: "blue",
				label: "Total Properties",
				value: data.total_properties.toLocaleString(),
				subtext: data.available_properties + " available · " + data.sold_properties + " sold",
			}),
			DB.renderKpiCard({
				icon: "users", iconColor: "purple",
				label: "Active Agents",
				value: data.active_agents.toLocaleString(),
				subtext: "of " + data.total_agents + " total",
			}),
		].join("");
	}, function () {
		document.getElementById("ceo-kpi-row").innerHTML =
			`<div class="db-card" style="grid-column:1/-1;padding:20px">${DB.errorState("Failed to load KPIs")}</div>`;
	});

	// ── Revenue Over Time ─────────────────────────────────────────────────
	DB.call("get_revenue_over_time", { months: 12 }, function (data) {
		document.getElementById("ceo-revenue-card").innerHTML = DB.renderChartCard({
			title: "Revenue Over Time",
			chartId: "ceo-revenue-inner",
			action: "View Deals",
			actionLink: "/app/opportunity?sales_stage=Closed Won",
		});
		if (data.data && data.data.length) {
			DB.renderBarChart(
				"ceo-revenue-inner",
				data.data.map(function (d) { return DB.monthLabel(d.month); }),
				data.data.map(function (d) { return parseFloat(d.revenue) || 0; }),
				{
					seriesName: "Revenue",
					type: "line",
					formatY: function (v) { return DB.formatNaira(v); },
					height: 240,
				}
			);
		} else {
			document.getElementById("ceo-revenue-inner").innerHTML = DB.emptyState("No revenue data yet");
		}
	}, function () {
		document.getElementById("ceo-revenue-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load revenue chart")}</div>`;
	});

	// ── Payment Collection Health ─────────────────────────────────────────
	DB.call("get_collection_health", { months: 6 }, function (data) {
		var footer = data.collection_rate_this_month !== undefined
			? "Collection rate this month: <strong>" + data.collection_rate_this_month + "%</strong>"
			: "";
		document.getElementById("ceo-collection-card").innerHTML = DB.renderChartCard({
			title: "Payment Collection Health",
			chartId: "ceo-collection-inner",
			action: "View Payment Plans",
			actionLink: "/app/payment-plan",
			footer: footer,
		});
		if (data.data && data.data.length) {
			DB.renderStackedBar(
				"ceo-collection-inner",
				data.data.map(function (d) { return DB.monthLabel(d.month); }),
				[
					{
						name: "Collected",
						chartType: "bar",
						values: data.data.map(function (d) { return parseFloat(d.collected) || 0; }),
					},
					{
						name: "Outstanding",
						chartType: "bar",
						values: data.data.map(function (d) { return parseFloat(d.outstanding) || 0; }),
					},
				],
				{ colors: ["#059669", "#FCA5A5"], height: 220 }
			);
		} else {
			document.getElementById("ceo-collection-inner").innerHTML = DB.emptyState("No payment data");
		}
	}, function () {
		document.getElementById("ceo-collection-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load collection data")}</div>`;
	});

	// ── Property Portfolio Breakdown ──────────────────────────────────────
	DB.call("get_property_breakdown", {}, function (data) {
		document.getElementById("ceo-property-card").innerHTML = DB.renderChartCard({
			title: "Property Portfolio",
			chartId: "ceo-property-inner",
			action: "View All",
			actionLink: "/app/property",
		});
		if (data.total > 0) {
			DB.renderDonut(
				"ceo-property-inner",
				["Available", "Reserved", "Sold"],
				[data.available, data.reserved, data.sold],
				["#059669", "#D97706", "#6366F1"]
			);
		} else {
			document.getElementById("ceo-property-inner").innerHTML = DB.emptyState("No properties found");
		}
	}, function () {
		document.getElementById("ceo-property-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load property data")}</div>`;
	});

	// ── Pipeline Summary (Mini Funnel) ────────────────────────────────────
	DB.call("get_pipeline_summary", {}, function (data) {
		var footer = "Total pipeline: <strong>" + DB.formatNaira(data.total_pipeline_value) + "</strong>";
		document.getElementById("ceo-pipeline-card").innerHTML = DB.renderChartCard({
			title: "Sales Pipeline",
			chartId: "ceo-pipeline-inner",
			action: "Full Pipeline →",
			actionLink: "/app/re-sales-dashboard",
			footer: footer,
		});
		DB.renderFunnel(document.getElementById("ceo-pipeline-inner"), data.stages);
	}, function () {
		document.getElementById("ceo-pipeline-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load pipeline")}</div>`;
	});

	// ── Commission Summary ────────────────────────────────────────────────
	DB.call("get_commission_summary", {}, function (data) {
		document.getElementById("ceo-commission-card").innerHTML = `
			<div class="db-card db-animate">
				<div class="db-chart-card__header" style="padding:20px 20px 12px">
					<div class="db-chart-card__title">Commission Exposure</div>
				</div>
				<div id="ceo-commission-inner"></div>
			</div>
		`;
		DB.renderCommissionCard(document.getElementById("ceo-commission-inner"), data);
	}, function () {
		document.getElementById("ceo-commission-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load commissions")}</div>`;
	});

	// ── Agent Leaderboard ─────────────────────────────────────────────────
	DB.call("get_agent_leaderboard", { period: period, limit: 5 }, function (data) {
		document.getElementById("ceo-leaderboard-card").innerHTML = DB.renderTableCard({
			title: "Top Agents",
			tableId: "ceo-leaderboard-inner",
			action: "View All",
			actionLink: "/app/commission-record",
		});
		DB.renderLeaderboard(document.getElementById("ceo-leaderboard-inner"), data.leaderboard);
	}, function () {
		document.getElementById("ceo-leaderboard-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load leaderboard")}</div>`;
	});

	// ── Alerts Panel ──────────────────────────────────────────────────────
	DB.call("get_alerts", {}, function (data) {
		document.getElementById("ceo-alerts-card").innerHTML = DB.renderTableCard({
			title: "Alerts & Action Items",
			tableId: "ceo-alerts-inner",
		});
		DB.renderAlerts(document.getElementById("ceo-alerts-inner"), data.alerts);
	}, function () {
		document.getElementById("ceo-alerts-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load alerts")}</div>`;
	});
}
