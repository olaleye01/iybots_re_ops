/**
 * RE Operations Dashboard — Frappe Custom Page
 * Renders operations KPIs, estate project cards, overdue payments table,
 * payment collection trend, property status breakdown, and agent check-ins.
 */

frappe.pages["re-operations-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "RE Operations",
		single_column: true,
	});

	$(wrapper).find(".page-content").addClass("iybots-dashboard");

	page.set_primary_action("New Property", function () {
		frappe.new_doc("Property");
	}, "plus");

	page.add_menu_item("New Estate Project", function () {
		frappe.new_doc("Estate Project");
	});

	page.add_menu_item("View Overdue Payments Report", function () {
		frappe.set_route("query-report", "Overdue Payments");
	});

	page.add_menu_item("View Payment Plans", function () {
		frappe.set_route("List", "Payment Plan");
	});

	_render_operations_dashboard(wrapper, page);
};

function _render_operations_dashboard(wrapper, page) {
	var DB = window.IybotsDashboard;
	var $main = $(wrapper).find(".page-content");

	$main.html(`
		<div id="ops-kpi-row" class="db-grid db-grid-4"></div>
		<div class="db-grid db-grid-2">
			<div id="ops-projects-card"></div>
			<div id="ops-collection-card"></div>
		</div>
		<div class="db-grid db-grid-2">
			<div id="ops-overdue-card"></div>
			<div id="ops-property-card"></div>
		</div>
		<div id="ops-checkins-card"></div>
	`);

	// ── Loading skeletons ─────────────────────────────────────────────────
	DB.renderSkeletonGrid(document.getElementById("ops-kpi-row"), 4, "kpi");
	["ops-projects-card", "ops-collection-card"].forEach(function (id) {
		document.getElementById(id).innerHTML =
			`<div class="db-card db-skeleton db-skeleton-chart"></div>`;
	});
	["ops-overdue-card", "ops-property-card", "ops-checkins-card"].forEach(function (id) {
		document.getElementById(id).innerHTML =
			`<div class="db-card db-skeleton db-skeleton-table"></div>`;
	});

	// ── Operations KPI Cards ──────────────────────────────────────────────
	DB.call("get_operations_kpis", {}, function (data) {
		var $row = document.getElementById("ops-kpi-row");

		var collectionColor = data.collection_rate >= 80 ? "green"
			: data.collection_rate >= 50 ? "orange" : "red";

		$row.innerHTML = [
			DB.renderKpiCard({
				icon: "building-2", iconColor: "blue",
				label: "Total Properties",
				value: data.total_properties.toLocaleString(),
				subtext: "in portfolio",
			}),
			DB.renderKpiCard({
				icon: "home", iconColor: "green",
				label: "Available Units",
				value: data.available_units.toLocaleString(),
				subtext: "ready to sell",
			}),
			DB.renderKpiCard({
				icon: "alert-triangle", iconColor: data.overdue_payments > 0 ? "red" : "green",
				label: "Overdue Payments",
				value: data.overdue_payments.toLocaleString(),
				isDanger: data.overdue_payments > 0,
				subtext: data.overdue_payments > 0 ? "require follow-up" : "all clear",
			}),
			DB.renderKpiCard({
				icon: "percent", iconColor: collectionColor,
				label: "Collection Rate",
				value: data.collection_rate + "%",
				subtext: "this month",
			}),
		].join("");
	}, function () {
		document.getElementById("ops-kpi-row").innerHTML =
			`<div class="db-card" style="grid-column:1/-1;padding:20px">${DB.errorState("Failed to load KPIs")}</div>`;
	});

	// ── Estate Projects Grid ──────────────────────────────────────────────
	DB.call("get_estate_projects", {}, function (data) {
		document.getElementById("ops-projects-card").innerHTML = DB.renderTableCard({
			title: "Estate Projects",
			tableId: "ops-projects-inner",
			action: "View All Projects",
			actionLink: "/app/estate-project",
		});
		DB.renderProjectCards(document.getElementById("ops-projects-inner"), data.projects);
	}, function () {
		document.getElementById("ops-projects-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load projects")}</div>`;
	});

	// ── Payment Collection Trend ──────────────────────────────────────────
	DB.call("get_collection_trend", { months: 6 }, function (data) {
		document.getElementById("ops-collection-card").innerHTML = DB.renderChartCard({
			title: "Collection Trend",
			chartId: "ops-collection-inner",
			action: "View Payment Plans",
			actionLink: "/app/payment-plan",
		});
		if (data.data && data.data.length) {
			DB.renderStackedBar(
				"ops-collection-inner",
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
						values: data.data.map(function (d) {
							return Math.max(0, parseFloat(d.total) - parseFloat(d.collected));
						}),
					},
				],
				{ colors: ["#059669", "#FCA5A5"], height: 240 }
			);
		} else {
			document.getElementById("ops-collection-inner").innerHTML = DB.emptyState("No payment data yet");
		}
	}, function () {
		document.getElementById("ops-collection-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load collection trend")}</div>`;
	});

	// ── Overdue Payments Table ────────────────────────────────────────────
	DB.call("get_overdue_payments", { limit: 10 }, function (data) {
		var totalStr = data.total_overdue > 10
			? ` (showing 10 of ${data.total_overdue})`
			: "";
		document.getElementById("ops-overdue-card").innerHTML = DB.renderTableCard({
			title: "Overdue Payments" + totalStr,
			tableId: "ops-overdue-inner",
			action: "View All Overdue →",
			actionLink: "/app/query-report/Overdue Payments",
		});
		DB.renderOverdueTable(document.getElementById("ops-overdue-inner"), data.payments);
	}, function () {
		document.getElementById("ops-overdue-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load overdue payments")}</div>`;
	});

	// ── Property Status Breakdown ─────────────────────────────────────────
	DB.call("get_property_breakdown", {}, function (data) {
		document.getElementById("ops-property-card").innerHTML = DB.renderChartCard({
			title: "Property Status",
			chartId: "ops-property-inner",
			action: "View Properties",
			actionLink: "/app/property",
		});
		if (data.total > 0) {
			DB.renderDonut(
				"ops-property-inner",
				["Available", "Reserved", "Sold"],
				[data.available, data.reserved, data.sold],
				["#059669", "#D97706", "#6366F1"]
			);
		} else {
			document.getElementById("ops-property-inner").innerHTML = DB.emptyState("No properties found");
		}
	}, function () {
		document.getElementById("ops-property-card").innerHTML =
			`<div class="db-card db-chart-card">${DB.errorState("Failed to load property data")}</div>`;
	});

	// ── Recent Agent Check-ins ────────────────────────────────────────────
	DB.call("get_recent_checkins", { limit: 10 }, function (data) {
		document.getElementById("ops-checkins-card").innerHTML = DB.renderTableCard({
			title: "Recent Agent Check-ins",
			tableId: "ops-checkins-inner",
			action: "View All Check-ins",
			actionLink: "/app/agent-check-in",
		});
		DB.renderCheckinsTable(document.getElementById("ops-checkins-inner"), data.checkins);
	}, function () {
		document.getElementById("ops-checkins-card").innerHTML =
			`<div class="db-card db-table-card">${DB.errorState("Failed to load check-ins")}</div>`;
	});
}
