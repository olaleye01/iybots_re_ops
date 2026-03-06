/**
 * IYBOTS Admin Dashboard — Shared Component Library
 * Reusable render functions for KPI cards, charts, tables, and alerts.
 * Used by all three admin dashboard pages.
 */

window.IybotsDashboard = window.IybotsDashboard || {};

(function (DB) {
	"use strict";

	// ── Lucide SVG Icons ──────────────────────────────────────────────────────

	const ICONS = {
		"user-plus": `<svg viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>`,
		"trending-up": `<svg viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
		"trophy": `<svg viewBox="0 0 24 24"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>`,
		"target": `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
		"clock": `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
		"banknote": `<svg viewBox="0 0 24 24"><rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>`,
		"calendar-check": `<svg viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><polyline points="9 16 11 18 15 14"/></svg>`,
		"handshake": `<svg viewBox="0 0 24 24"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/></svg>`,
		"alert-circle": `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
		"alert-triangle": `<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
		"building-2": `<svg viewBox="0 0 24 24"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>`,
		"home": `<svg viewBox="0 0 24 24"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
		"percent": `<svg viewBox="0 0 24 24"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
		"users": `<svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
		"layout-dashboard": `<svg viewBox="0 0 24 24"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>`,
		"bar-chart-3": `<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>`,
		"settings": `<svg viewBox="0 0 24 24"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`,
		"coins": `<svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="m16.71 13.88.7.71-2.82 2.82"/></svg>`,
		"calendar": `<svg viewBox="0 0 24 24"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
		"map-pin-off": `<svg viewBox="0 0 24 24"><path d="M12.75 7.09a3 3 0 0 1 2.16 2.16"/><path d="M17.072 17.072c-1.634 2.17-3.527 3.912-4.471 4.727a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 1.432-4.568"/><path d="m2 2 20 20"/><path d="M8.475 2.818A8 8 0 0 1 20 10c0 1.734-.469 3.357-1.28 4.75"/></svg>`,
		"external-link": `<svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`,
		"send": `<svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`,
		"plus": `<svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
		"arrow-up": `<svg viewBox="0 0 24 24"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>`,
		"arrow-down": `<svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>`,
		"minus": `<svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
		"inbox": `<svg viewBox="0 0 24 24"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>`,
	};

	DB.icon = function (name, size) {
		size = size || 18;
		const svg = ICONS[name] || ICONS["inbox"];
		return svg.replace("<svg ", `<svg width="${size}" height="${size}" `);
	};

	// ── Formatting ────────────────────────────────────────────────────────────

	DB.formatNaira = function (value) {
		value = parseFloat(value) || 0;
		if (value >= 1e9) return "₦" + (value / 1e9).toFixed(1) + "B";
		if (value >= 1e6) return "₦" + (value / 1e6).toFixed(1) + "M";
		if (value >= 1e3) return "₦" + (value / 1e3).toFixed(0) + "K";
		return "₦" + value.toLocaleString("en-NG", { minimumFractionDigits: 0 });
	};

	DB.formatNairaFull = function (value) {
		value = parseFloat(value) || 0;
		return "₦" + value.toLocaleString("en-NG", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	DB.relativeTime = function (dateStr) {
		if (!dateStr) return "";
		const d = new Date(dateStr);
		const now = new Date();
		const diff = Math.floor((now - d) / 1000);
		if (diff < 60) return "just now";
		if (diff < 3600) return Math.floor(diff / 60) + "m ago";
		if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
		if (diff < 604800) return Math.floor(diff / 86400) + "d ago";
		return d.toLocaleDateString("en-NG", { day: "numeric", month: "short" });
	};

	DB.formatDate = function (dateStr) {
		if (!dateStr) return "";
		const d = new Date(dateStr);
		return d.toLocaleDateString("en-NG", { day: "numeric", month: "short", year: "numeric" });
	};

	DB.initials = function (name) {
		if (!name) return "??";
		const parts = name.trim().split(/\s+/);
		if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
		return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
	};

	DB.stageBadgeClass = function (stage) {
		const map = {
			"Inquiry": "inquiry",
			"Site Visit": "site-visit",
			"Offer": "offer",
			"Payment Plan": "payment-plan",
			"Closed Won": "closed-won",
			"Closed Lost": "closed-lost",
			"Available": "available",
			"Sold": "sold",
			"Reserved": "reserved",
			"Active": "active",
			"Pending": "pending",
			"Overdue": "overdue",
			"Paid": "paid",
		};
		return map[stage] || "pending";
	};

	// ── Skeleton Loaders ──────────────────────────────────────────────────────

	DB.renderSkeletonGrid = function (container, count, type) {
		type = type || "kpi";
		let html = "";
		for (let i = 0; i < count; i++) {
			html += `<div class="db-card db-skeleton db-skeleton-${type} db-animate"></div>`;
		}
		container.innerHTML = html;
	};

	// ── KPI Card ──────────────────────────────────────────────────────────────

	DB.renderKpiCard = function (opts) {
		// opts: { icon, iconColor, label, value, trend, subtext, isDanger }
		const trend = opts.trend || { direction: "neutral", pct: 0 };
		let trendHtml = "";
		if (trend.direction === "up") {
			trendHtml = `<span class="kpi-trend up">${DB.icon("arrow-up", 12)} ${trend.pct}%</span>`;
		} else if (trend.direction === "down") {
			trendHtml = `<span class="kpi-trend down">${DB.icon("arrow-down", 12)} ${trend.pct}%</span>`;
		} else {
			trendHtml = `<span class="kpi-trend neutral">${DB.icon("minus", 12)} N/A</span>`;
		}

		return `
			<div class="db-card kpi-card db-animate">
				<div class="kpi-card__icon-wrap ${opts.iconColor || "blue"}">${DB.icon(opts.icon, 20)}</div>
				<div>
					<div class="kpi-card__label">${opts.label}</div>
					<div class="kpi-card__value${opts.isDanger ? " danger" : ""}">${opts.value}</div>
				</div>
				<div class="kpi-card__footer">
					${trendHtml}
					<span class="kpi-subtext">${opts.subtext || "vs. last period"}</span>
				</div>
			</div>
		`;
	};

	// ── Chart Card Wrapper ────────────────────────────────────────────────────

	DB.renderChartCard = function (opts) {
		// opts: { title, chartId, action, actionLink, footer }
		const action = opts.action
			? `<a href="${opts.actionLink || "#"}" class="db-chart-card__action">${opts.action} ${DB.icon("external-link", 12)}</a>`
			: "";
		return `
			<div class="db-card db-chart-card db-animate">
				<div class="db-chart-card__header">
					<div class="db-chart-card__title">${opts.title}</div>
					${action}
				</div>
				<div class="db-chart-area" id="${opts.chartId}"></div>
				${opts.footer ? `<div class="db-chart-footer">${opts.footer}</div>` : ""}
			</div>
		`;
	};

	// ── Table Card Wrapper ────────────────────────────────────────────────────

	DB.renderTableCard = function (opts) {
		// opts: { title, tableId, action, actionLink }
		const action = opts.action
			? `<a href="${opts.actionLink || "#"}" class="db-chart-card__action">${opts.action} ${DB.icon("external-link", 12)}</a>`
			: "";
		return `
			<div class="db-card db-table-card db-animate">
				<div class="db-table-card__header">
					<div class="db-table-card__title">${opts.title}</div>
					${action}
				</div>
				<div id="${opts.tableId}"></div>
			</div>
		`;
	};

	// ── Funnel Chart (CSS-based horizontal bars) ──────────────────────────────

	DB.renderFunnel = function (container, stages) {
		if (!stages || !stages.length) {
			container.innerHTML = DB.emptyState("No pipeline data");
			return;
		}
		const maxCount = Math.max(...stages.map(s => s.count), 1);
		let html = '<div class="db-funnel">';
		stages.forEach(function (s, i) {
			const widthPct = maxCount > 0 ? Math.max(20, Math.round((s.count / maxCount) * 100)) : 20;
			const encoded = encodeURIComponent(s.stage);
			html += `
				<div class="db-funnel-row" onclick="frappe.set_route('List', 'Opportunity', {sales_stage: '${s.stage}'})">
					<div class="db-funnel-label">${s.stage}</div>
					<div class="db-funnel-bar">
						<div class="db-funnel-bar-fill stage-${i}" style="width:${widthPct}%">
							${s.count > 0 ? DB.formatNaira(s.value) : ""}
						</div>
					</div>
					<div class="db-funnel-count">${s.count}</div>
				</div>
			`;
		});
		html += "</div>";
		container.innerHTML = html;
	};

	// ── Donut Chart (using frappe-charts) ────────────────────────────────────

	DB.renderDonut = function (containerId, labels, values, colors) {
		const container = document.getElementById(containerId);
		if (!container) return;

		colors = colors || ["#1A56DB", "#059669", "#D97706", "#6366F1", "#DC2626", "#9CA3AF"];

		try {
			new frappe.Chart("#" + containerId, {
				type: "donut",
				data: {
					labels: labels,
					datasets: [{ values: values }],
				},
				height: 240,
				colors: colors,
				tooltipOptions: {
					formatTooltipX: d => d,
					formatTooltipY: d => d.toLocaleString(),
				},
			});
		} catch (e) {
			container.innerHTML = DB.emptyState("Chart unavailable");
		}
	};

	// ── Bar Chart (using frappe-charts) ──────────────────────────────────────

	DB.renderBarChart = function (containerId, labels, values, opts) {
		const container = document.getElementById(containerId);
		if (!container) return;
		opts = opts || {};

		try {
			new frappe.Chart("#" + containerId, {
				type: opts.type || "bar",
				data: {
					labels: labels,
					datasets: [{
						name: opts.seriesName || "Value",
						values: values,
						chartType: opts.type || "bar",
					}],
				},
				height: opts.height || 240,
				colors: opts.colors || ["#1A56DB"],
				axisOptions: { xIsSeries: 1 },
				tooltipOptions: {
					formatTooltipY: opts.formatY || (d => d.toLocaleString()),
				},
			});
		} catch (e) {
			container.innerHTML = DB.emptyState("Chart unavailable");
		}
	};

	// ── Stacked Bar Chart ─────────────────────────────────────────────────────

	DB.renderStackedBar = function (containerId, labels, datasets, opts) {
		const container = document.getElementById(containerId);
		if (!container) return;
		opts = opts || {};

		try {
			new frappe.Chart("#" + containerId, {
				type: "bar",
				data: {
					labels: labels,
					datasets: datasets,
				},
				height: opts.height || 240,
				colors: opts.colors || ["#059669", "#DC2626"],
				stacked: 1,
				axisOptions: { xIsSeries: 1 },
			});
		} catch (e) {
			container.innerHTML = DB.emptyState("Chart unavailable");
		}
	};

	// ── Agent Leaderboard Table ───────────────────────────────────────────────

	DB.renderLeaderboard = function (container, data) {
		if (!data || !data.length) {
			container.innerHTML = DB.emptyState("No agent data for this period");
			return;
		}
		let html = `
			<table class="db-table">
				<thead>
					<tr>
						<th>#</th>
						<th>Agent</th>
						<th class="right">Deals Won</th>
						<th class="right">Pipeline</th>
						<th class="right">Conv. Rate</th>
					</tr>
				</thead>
				<tbody>
		`;
		data.forEach(function (r) {
			const rankClass = r.rank <= 3 ? "r" + r.rank : "rn";
			html += `
				<tr>
					<td><span class="db-rank ${rankClass}">${r.rank}</span></td>
					<td>
						<div class="db-agent-cell">
							<span class="db-avatar">${DB.initials(r.agent_name)}</span>
							${r.agent_name}
						</div>
					</td>
					<td class="right" style="font-weight:600">${r.deals_won}</td>
					<td class="right">${DB.formatNaira(r.pipeline_value)}</td>
					<td class="right">${r.conversion_rate}%</td>
				</tr>
			`;
		});
		html += "</tbody></table>";
		container.innerHTML = html;
	};

	// ── Recent Deals Table ────────────────────────────────────────────────────

	DB.renderRecentDeals = function (container, deals) {
		if (!deals || !deals.length) {
			container.innerHTML = DB.emptyState("No recent deals");
			return;
		}
		let html = `
			<table class="db-table">
				<thead>
					<tr>
						<th>Deal</th>
						<th>Client</th>
						<th>Stage</th>
						<th class="right">Value</th>
						<th>Agent</th>
						<th>Updated</th>
					</tr>
				</thead>
				<tbody>
		`;
		deals.forEach(function (d) {
			html += `
				<tr onclick="frappe.set_route('Form', 'Opportunity', '${d.name}')" style="cursor:pointer">
					<td style="font-weight:500">${d.name}</td>
					<td>${d.client || "—"}</td>
					<td><span class="db-badge ${DB.stageBadgeClass(d.stage)}">${d.stage || "—"}</span></td>
					<td class="right" style="font-weight:600">${DB.formatNaira(d.value)}</td>
					<td>${d.agent || "—"}</td>
					<td style="color:#6B7280">${DB.relativeTime(d.modified)}</td>
				</tr>
			`;
		});
		html += "</tbody></table>";
		container.innerHTML = html;
	};

	// ── Overdue Payments Table ────────────────────────────────────────────────

	DB.renderOverdueTable = function (container, payments) {
		if (!payments || !payments.length) {
			container.innerHTML = `<div class="db-empty" style="color:#059669">
				${DB.icon("check-circle", 36)}
				<div class="db-empty-text">No overdue payments</div>
			</div>`;
			return;
		}
		let html = `
			<table class="db-table">
				<thead>
					<tr>
						<th>Client</th>
						<th>Property</th>
						<th class="right">Amount Due</th>
						<th>Due Date</th>
						<th class="right">Days Overdue</th>
						<th></th>
					</tr>
				</thead>
				<tbody>
		`;
		payments.forEach(function (p) {
			let rowClass = "";
			if (p.days_overdue > 30) rowClass = "db-overdue-critical";
			else if (p.days_overdue > 7) rowClass = "db-overdue-warning";

			html += `
				<tr class="${rowClass}">
					<td style="font-weight:500">${p.client || "—"}</td>
					<td>${p.property || "—"}</td>
					<td class="right" style="font-weight:600;color:#DC2626">${DB.formatNaira(p.amount)}</td>
					<td>${DB.formatDate(p.due_date)}</td>
					<td class="right">
						<span class="db-badge overdue">${p.days_overdue}d</span>
					</td>
					<td>
						<a href="/app/payment-plan/${p.plan_name}" class="db-chart-card__action" style="font-size:11px">
							View ${DB.icon("external-link", 11)}
						</a>
					</td>
				</tr>
			`;
		});
		html += "</tbody></table>";
		container.innerHTML = html;
	};

	// ── Agent Check-ins Table ─────────────────────────────────────────────────

	DB.renderCheckinsTable = function (container, checkins) {
		if (!checkins || !checkins.length) {
			container.innerHTML = DB.emptyState("No recent check-ins");
			return;
		}
		let html = `
			<table class="db-table">
				<thead>
					<tr>
						<th>Agent</th>
						<th>Time</th>
						<th>Location</th>
						<th>Notes</th>
					</tr>
				</thead>
				<tbody>
		`;
		checkins.forEach(function (c) {
			html += `
				<tr>
					<td>
						<div class="db-agent-cell">
							<span class="db-avatar">${DB.initials(c.agent_name)}</span>
							${c.agent_name}
						</div>
					</td>
					<td style="color:#6B7280">${DB.relativeTime(c.check_in_time)}</td>
					<td>${c.location_name || "—"}</td>
					<td style="color:#6B7280;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.notes || "—"}</td>
				</tr>
			`;
		});
		html += "</tbody></table>";
		container.innerHTML = html;
	};

	// ── Alerts Panel ─────────────────────────────────────────────────────────

	DB.renderAlerts = function (container, alerts) {
		if (!alerts || !alerts.length) {
			container.innerHTML = `<div class="db-empty" style="color:#059669;padding:24px">
				${DB.icon("check-circle", 32)}
				<div class="db-empty-text">All clear — no alerts</div>
			</div>`;
			return;
		}
		let html = '<div class="db-alert-list">';
		alerts.forEach(function (a) {
			html += `
				<a href="${a.link || "#"}" class="db-alert-item">
					<div class="db-alert-border ${a.severity}"></div>
					<div class="db-alert-icon ${a.severity}">${DB.icon(a.icon || "alert-circle", 16)}</div>
					<div class="db-alert-body">
						<div class="db-alert-label">${a.label}</div>
					</div>
					<span class="db-alert-count ${a.severity}">${a.count}</span>
				</a>
			`;
		});
		html += "</div>";
		container.innerHTML = html;
	};

	// ── Estate Projects Grid ──────────────────────────────────────────────────

	DB.renderProjectCards = function (container, projects) {
		if (!projects || !projects.length) {
			container.innerHTML = DB.emptyState("No estate projects found");
			return;
		}
		let html = '<div class="db-project-grid">';
		projects.forEach(function (p) {
			const pctClass = p.sold_pct >= 70 ? "high" : p.sold_pct >= 30 ? "medium" : "low";
			html += `
				<div class="db-project-card" onclick="frappe.set_route('Form', 'Estate Project', '${p.name}')">
					<div class="db-project-name">${p.project_name}</div>
					<div class="db-project-location">${p.location || "—"}</div>
					<div class="db-project-progress">
						<div class="db-project-progress-fill ${pctClass}" style="width:${p.sold_pct}%"></div>
					</div>
					<div class="db-project-stats">
						<span>${p.sold_units} / ${p.total_units} sold</span>
						<span>${p.available_units} available</span>
						<span>${p.sold_pct}%</span>
					</div>
				</div>
			`;
		});
		html += "</div>";
		container.innerHTML = html;
	};

	// ── Commission Summary ────────────────────────────────────────────────────

	DB.renderCommissionCard = function (container, data) {
		container.innerHTML = `
			<div class="db-commission-card">
				<div class="db-commission-row">
					<span class="db-commission-label">Total Paid</span>
					<span class="db-commission-value">${DB.formatNaira(data.total_paid)}</span>
				</div>
				<div class="db-section-divider"></div>
				<div class="db-commission-row">
					<span class="db-commission-label">Pending Approval</span>
					<span class="db-commission-value warning">${DB.formatNaira(data.pending_amount)}</span>
				</div>
				<div class="db-commission-row">
					<span class="db-commission-label">Pending Records</span>
					<span class="db-commission-value" style="font-size:13px">${data.pending_count} records</span>
				</div>
				<a href="/app/commission-record?status=Draft" class="db-chart-card__action" style="font-size:12px;margin-top:4px">
					View Commission Records ${DB.icon("external-link", 12)}
				</a>
			</div>
		`;
	};

	// ── Empty & Error States ──────────────────────────────────────────────────

	DB.emptyState = function (message) {
		return `
			<div class="db-empty">
				${DB.icon("inbox", 40)}
				<div class="db-empty-text">${message || "No data available"}</div>
			</div>
		`;
	};

	DB.errorState = function (message) {
		return `
			<div class="db-empty" style="color:#DC2626">
				${DB.icon("alert-circle", 36)}
				<div class="db-empty-text">${message || "Failed to load data"}</div>
			</div>
		`;
	};

	// ── API Helper ────────────────────────────────────────────────────────────

	DB.call = function (method, args, callback, errCallback) {
		frappe.call({
			method: "iybots_re_ops.iybots_real_estate_ops.api.dashboard." + method,
			args: args || {},
			callback: function (r) {
				if (r && r.message) {
					callback(r.message);
				} else {
					if (errCallback) errCallback("No data returned");
				}
			},
			error: function (err) {
				console.error("Dashboard API error:", method, err);
				if (errCallback) errCallback(err);
			},
		});
	};

	// ── Month label helper ────────────────────────────────────────────────────

	DB.monthLabel = function (ym) {
		if (!ym) return "";
		const [year, month] = ym.split("-");
		const d = new Date(year, parseInt(month) - 1, 1);
		return d.toLocaleDateString("en-NG", { month: "short", year: "2-digit" });
	};

})(window.IybotsDashboard);
