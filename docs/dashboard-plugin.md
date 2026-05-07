# Hermes Dashboard Plugin

Hermes Threshold includes a dashboard plugin that lets the Hermes dashboard review draft wake suggestions and view controlled-trial counters.

Install the `dashboard-plugin/hermes-threshold` directory into the Hermes plugin path:

```bash
mkdir -p ~/.hermes/plugins/hermes-threshold
cp -R dashboard-plugin/hermes-threshold/dashboard ~/.hermes/plugins/hermes-threshold/
```

Restart the Hermes dashboard after installation. Hermes mounts plugin API routers during dashboard startup; a plugin rescan can discover assets, but it does not mount a newly added `plugin_api.py`.

The plugin API reads `~/.config/hermes-threshold/service.env` by default and proxies the local Threshold service at `http://127.0.0.1:8789`. Set `HERMES_THRESHOLD_ENV_FILE`, `HERMES_THRESHOLD_URL`, or `HERMES_THRESHOLD_API_TOKEN` in the dashboard process environment to override those values.
