# Railway Deployment Checklist

The repository contains `railway.toml` and a root `Dockerfile`. Railway should detect the Dockerfile automatically; the config sets one replica, `/health/live` health checking and restart-on-failure.

## CLI deployment

Run these commands from the repository root. Use `railway init` only when a new Railway project is needed; otherwise link the existing project and service.

```bash
railway login
railway link --project <PROJECT_ID> --environment production --service <SERVICE_NAME>
railway status
railway up
```

For a detached deploy, use `railway up -d`. For CI, use a project-scoped `RAILWAY_TOKEN` and `railway up --ci`. The source-code deploy command is `railway up`; `railway deploy` is for Railway templates.

Set variables from the CLI with `railway variable set KEY=value`. Send secret values through stdin instead of placing them in shell history:

```bash
printf '%s' '<ADMIN_API_KEY>' | railway variable set ADMIN_API_KEY --stdin
```

The persistent Volume still needs to be created and mounted at `/data` in the Railway service; `railway.toml` does not create storage.

## Service setup

1. Create or select one Railway project and one service for this repository.
2. Attach one persistent Volume to the service with mount path `/data`.
3. Keep replicas at `1`; the scheduler and SQLite writer are single-instance by design.
4. Deploy from the repository root. Do not set a separate start command unless overriding the Dockerfile command intentionally.
5. Confirm the deployment healthcheck is `/health/live` and the generated service URL responds with `{"status":"ok"}`.

## Required service variables

Set these in Railway Variables. Do not commit their values:

```text
APP_ENV=production
DATABASE_URL=sqlite:////data/hunter.db
TELEGRAM_BOT_TOKEN=<BotFather token>
TELEGRAM_WEBHOOK_SECRET=<long random secret>
TELEGRAM_ALLOWED_USER_ID=<numeric Telegram user id>
TELEGRAM_ALLOWED_CHAT_ID=<numeric Telegram chat id>
ADMIN_API_KEY=<long random admin key>
APP_TIMEZONE=Europe/Istanbul
COLLECTION_ENABLED=false
INSTANT_ALERTS_ENABLED=false
DAILY_REPORT_HOUR=18
```

`PORT` is supplied by Railway and is consumed by the Docker start command. Do not hard-code a different production port.

## Safe activation order

1. Deploy with collection and immediate alerts disabled.
2. Verify `/health/live`, `/health/ready`, migration logs and the persistent `/data` path.
3. Verify the authenticated admin endpoints with `ADMIN_API_KEY`.
4. Register the Telegram webhook using the generated HTTPS URL and `TELEGRAM_WEBHOOK_SECRET`.
5. Confirm a controlled Telegram delivery test.
6. Enable `COLLECTION_ENABLED=true` only after the `jobicy` and/or `himalayas` source rows are explicitly enabled and policy-approved.
7. Enable `INSTANT_ALERTS_ENABLED=true` only after Telegram delivery is verified.

## Verification after restart

- `/health/live` remains 200.
- `/health/ready` remains ready.
- Existing jobs remain present.
- Queued tasks and pending outbox events remain in SQLite.
- The service still has exactly one active replica.

Deployment, Telegram delivery, resource usage and cost are not claimed until verified in the Railway project.
