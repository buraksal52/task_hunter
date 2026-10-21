# Security, Deployment & Operations

## Secrets
Railway variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_ALLOWED_USER_ID`, `TELEGRAM_ALLOWED_CHAT_ID`, `ADMIN_API_KEY`. No credentials in repo or logs. Provide `.env.example` with placeholders only.

## Telegram setup
1. Create bot via BotFather and keep token private.
2. Deploy HTTPS FastAPI webhook endpoint.
3. Register webhook via Telegram Bot API `setWebhook` with `secret_token` and allowed update types.
4. Verify `X-Telegram-Bot-Api-Secret-Token`, and authorize `from.id` plus `chat.id`.
5. Persist `update_id` to ignore duplicate deliveries.
6. Respond quickly; queue long-running collection tasks.

## Railway
Single service/replica, one Uvicorn worker, persistent volume `/data`, `DATABASE_URL=sqlite:////data/hunter.db`. Check runtime filesystem ownership, DB WAL file placement and migrations. Set usage alert and a budget hard limit only after accounting for other Railway workloads; hard limit may suspend service. Monitor real usage before choosing polling frequency.

## Backups and recovery
Use consistent SQLite backup procedure; store backups outside the same volume when feasible. Test restore at least once. On restart recover expired task leases and pending outbox messages. Document retention rules before ingesting source content.

## Operational commands
`/health` status, `/sources` source freshness and errors, `/hunt` manual enqueue, `/stats` aggregate summary. Ensure rate limiting for commands and authenticated admin routes.

## Cost controls
No always-on Chromium or loaded Transformer model. Cap HTTP requests, response bytes, concurrency and job counts per run. Log runtime duration, memory and source calls. A $5 included-usage target is not a spend guarantee.
