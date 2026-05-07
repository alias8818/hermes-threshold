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

  function Stat({ label, value }) {
    return e(
      "div",
      { className: "rounded-md border bg-background px-3 py-2" },
      e("div", { className: "text-xs text-muted-foreground" }, label),
      e("div", { className: "mt-1 text-2xl font-semibold tabular-nums" }, value),
    );
  }

  function SuggestionRow({ suggestion, onApprove, onDismiss, busy }) {
    const title = suggestion.title || suggestion.suggestion_id;
    const rationale = suggestion.rationale || suggestion.description || suggestion.reason || "";
    return e(
      "div",
      { className: "rounded-md border bg-background p-3" },
      e(
        "div",
        { className: "flex flex-wrap items-start justify-between gap-3" },
        e(
          "div",
          { className: "min-w-0 flex-1" },
          e("div", { className: "truncate text-sm font-medium" }, title),
          e(
            "div",
            { className: "mt-1 text-xs text-muted-foreground" },
            shortText(rationale, suggestion.suggestion_id),
          ),
        ),
        e(
          "div",
          { className: "flex shrink-0 items-center gap-2" },
          e(ui.Badge, { variant: "secondary" }, suggestion.status || "drafted"),
          e(
            ui.Button,
            {
              size: "sm",
              disabled: busy,
              onClick: () => onApprove(suggestion.suggestion_id),
            },
            "Approve",
          ),
          e(
            ui.Button,
            {
              size: "sm",
              variant: "outline",
              disabled: busy,
              onClick: () => onDismiss(suggestion.suggestion_id),
            },
            "Dismiss",
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
            "Draft wake suggestions and controlled-trial counters.",
          ),
        ),
        e(ui.Button, { variant: "outline", onClick: load, disabled: loading }, loading ? "Refreshing" : "Refresh"),
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
            e(ui.CardTitle, { className: "text-base" }, "Draft Suggestions"),
            e(ui.Badge, { variant: "outline" }, `${suggestions.length} pending`),
          ),
        ),
        e(
          ui.CardContent,
          { className: "space-y-3" },
          loading
            ? e("div", { className: "text-sm text-muted-foreground" }, "Loading suggestions...")
            : suggestions.length === 0
              ? e("div", { className: "text-sm text-muted-foreground" }, "No draft suggestions are waiting for review.")
              : suggestions.map((suggestion) =>
                  e(SuggestionRow, {
                    key: suggestion.suggestion_id,
                    suggestion,
                    busy: busyId === suggestion.suggestion_id,
                    onApprove: (id) => review(id, "approve"),
                    onDismiss: (id) => review(id, "dismiss"),
                  }),
                ),
        ),
      ),
    );
  }

  Registry.register("hermes-threshold", ThresholdPage);
})();
