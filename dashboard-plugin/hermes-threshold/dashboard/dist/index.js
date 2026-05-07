(function () {
  const SDK = window.__HERMES_PLUGIN_SDK__;
  const Registry = window.__HERMES_PLUGINS__;
  if (!SDK || !Registry) return;

  const React = SDK.React;
  const hooks = SDK.hooks;
  const ui = SDK.components;
  const fetchJSON = SDK.fetchJSON;

  const e = React.createElement;

  function api(path, options) {
    return fetchJSON(`/api/plugins/hermes-threshold${path}`, options || {});
  }

  function count(summary, key) {
    if (!summary) return 0;
    if (Object.prototype.hasOwnProperty.call(summary, key)) return summary[key] || 0;
    return (summary.counts && summary.counts[key]) || 0;
  }

  function shortText(value, fallback) {
    if (!value) return fallback;
    return String(value).length > 180 ? `${String(value).slice(0, 177)}...` : String(value);
  }

  function formatTime(value) {
    if (!value) return "unknown time";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function groupKey(suggestion) {
    const payload = suggestion.payload || {};
    return [
      suggestion.title || "",
      suggestion.description || "",
      payload.surface || "",
      payload.risk_score || "",
    ].join("\n");
  }

  function groupSuggestions(suggestions) {
    const groups = new Map();
    for (const suggestion of suggestions) {
      const key = groupKey(suggestion);
      const current = groups.get(key) || {
        key,
        title: suggestion.title || suggestion.suggestion_id,
        description: suggestion.description || "",
        surface: (suggestion.payload && suggestion.payload.surface) || "draft",
        riskScore: suggestion.payload && suggestion.payload.risk_score,
        valueScore: suggestion.payload && suggestion.payload.value_score,
        noveltyScore: suggestion.payload && suggestion.payload.novelty_score,
        suggestions: [],
      };
      current.suggestions.push(suggestion);
      groups.set(key, current);
    }
    return Array.from(groups.values()).map((group) => {
      group.suggestions.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
      group.latest = group.suggestions[0];
      group.oldest = group.suggestions[group.suggestions.length - 1];
      return group;
    });
  }

  function Stat({ label, value }) {
    return e(
      "div",
      { className: "rounded-md border bg-background px-3 py-2" },
      e("div", { className: "text-xs text-muted-foreground" }, label),
      e("div", { className: "mt-1 text-2xl font-semibold tabular-nums" }, value),
    );
  }

  function ReviewGroup({ group, onApprove, onDismissGroup, busy }) {
    const latest = group.latest;
    const copyCount = group.suggestions.length;
    const title = group.title || latest.suggestion_id;
    const rationale = group.description || latest.description || "";
    const copyLabel = copyCount === 1 ? "1 draft" : `${copyCount} duplicate drafts`;
    return e(
      "div",
      { className: "rounded-md border bg-background p-4" },
      e(
        "div",
        { className: "flex flex-wrap items-start justify-between gap-4" },
        e(
          "div",
          { className: "min-w-0 flex-1 space-y-2" },
          e(
            "div",
            { className: "flex flex-wrap items-center gap-2" },
            e("div", { className: "text-sm font-medium" }, title),
            e(ui.Badge, { variant: "secondary" }, copyLabel),
            e(ui.Badge, { variant: "outline" }, group.surface),
          ),
          e(
            "p",
            { className: "text-sm text-muted-foreground" },
            shortText(rationale, latest.suggestion_id),
          ),
          e(
            "div",
            { className: "grid gap-2 text-xs text-muted-foreground md:grid-cols-3" },
            e("div", null, `Newest: ${formatTime(latest.created_at)}`),
            e("div", null, `Oldest: ${formatTime(group.oldest.created_at)}`),
            e("div", null, `Value ${group.valueScore || "?"} / Novelty ${group.noveltyScore || "?"} / Risk ${group.riskScore || "?"}`),
          ),
        ),
        e(
          "div",
          { className: "flex shrink-0 flex-wrap items-center gap-2" },
          e(
            ui.Button,
            {
              size: "sm",
              disabled: busy,
              onClick: () => onApprove(latest.suggestion_id),
            },
            "Approve newest",
          ),
          e(
            ui.Button,
            {
              size: "sm",
              variant: "outline",
              disabled: busy,
              onClick: () => onDismissGroup(group.suggestions.map((item) => item.suggestion_id)),
            },
            copyCount === 1 ? "Dismiss" : "Dismiss group",
          ),
        ),
      ),
    );
  }

  function ThresholdPage() {
    const [summary, setSummary] = hooks.useState(null);
    const [suggestions, setSuggestions] = hooks.useState([]);
    const [loading, setLoading] = hooks.useState(true);
    const [busyId, setBusyId] = hooks.useState(null);
    const [error, setError] = hooks.useState("");

    const load = hooks.useCallback(async () => {
      setError("");
      setLoading(true);
      try {
        const nextSummary = await api("/summary");
        const nextSuggestions = await api("/suggestions?status=drafted&limit=25");
        setSummary(nextSummary);
        setSuggestions(nextSuggestions.suggestions || []);
      } catch (err) {
        setError(err && err.message ? err.message : "Unable to load Threshold data");
      } finally {
        setLoading(false);
      }
    }, []);

    hooks.useEffect(() => {
      load();
    }, [load]);

    async function review(id, action) {
      setBusyId(id);
      setError("");
      try {
        await api(`/suggestions/${encodeURIComponent(id)}/${action}`, { method: "POST" });
        await load();
      } catch (err) {
        setError(err && err.message ? err.message : `Unable to ${action} suggestion`);
      } finally {
        setBusyId(null);
      }
    }

    async function dismissGroup(ids) {
      setBusyId(ids.join(","));
      setError("");
      try {
        await api("/suggestions/batch-dismiss", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ suggestion_ids: ids }),
        });
        await load();
      } catch (err) {
        setError(err && err.message ? err.message : "Unable to dismiss suggestion group");
      } finally {
        setBusyId(null);
      }
    }

    const groups = groupSuggestions(suggestions);
    const duplicateCopies = suggestions.length - groups.length;

    return e(
      "div",
      { className: "space-y-4 p-1" },
      e(
        "div",
        { className: "flex flex-wrap items-center justify-between gap-3" },
        e(
          "div",
          null,
          e("h2", { className: "text-xl font-semibold tracking-normal" }, "Hermes Threshold"),
          e(
            "p",
            { className: "text-sm text-muted-foreground" },
            "Controlled-trial wake drafts. Nothing here has been sent or executed.",
          ),
        ),
        e(ui.Button, { variant: "outline", onClick: load, disabled: loading }, loading ? "Refreshing" : "Refresh"),
      ),
      e(
        "div",
        { className: "rounded-md border bg-muted/40 p-3 text-sm text-muted-foreground" },
        "Approve the newest copy when the idea is useful enough to keep for Hermes behavior work. Dismiss a group when it is repeated trial noise or not worth preserving.",
      ),
      error ? e("div", { className: "rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm" }, error) : null,
      e(
        "div",
        { className: "grid gap-3 md:grid-cols-5" },
        e(Stat, { label: "Wake cycles", value: count(summary, "wake_cycles") }),
        e(Stat, { label: "Drafts", value: count(summary, "drafted_suggestions") }),
        e(Stat, { label: "Approved", value: count(summary, "approved_suggestions") }),
        e(Stat, { label: "Dismissed", value: count(summary, "dismissed_suggestions") }),
        e(Stat, { label: "Useful", value: count(summary, "useful_feedback") }),
      ),
      e(
        ui.Card,
        null,
        e(
          ui.CardHeader,
          { className: "pb-3" },
          e(
            "div",
            { className: "flex items-center justify-between gap-3" },
            e(ui.CardTitle, { className: "text-base" }, "Review Queue"),
            e(
              "div",
              { className: "flex flex-wrap items-center justify-end gap-2" },
              duplicateCopies > 0 ? e(ui.Badge, { variant: "secondary" }, `${duplicateCopies} duplicate copies grouped`) : null,
              e(ui.Badge, { variant: "outline" }, `${groups.length} decisions`),
            ),
          ),
        ),
        e(
          ui.CardContent,
          { className: "space-y-3" },
          loading
            ? e("div", { className: "text-sm text-muted-foreground" }, "Loading suggestions...")
            : groups.length === 0
              ? e("div", { className: "text-sm text-muted-foreground" }, "No draft suggestions are waiting for review.")
              : groups.map((group) =>
                  e(ReviewGroup, {
                    key: group.key,
                    group,
                    busy: group.suggestions.some((item) => busyId && busyId.includes(item.suggestion_id)),
                    onApprove: (id) => review(id, "approve"),
                    onDismissGroup: dismissGroup,
                  }),
                ),
        ),
      ),
    );
  }

  Registry.register("hermes-threshold", ThresholdPage);
})();
