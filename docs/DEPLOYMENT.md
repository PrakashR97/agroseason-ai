# Deployment (Hostinger VPS, existing Traefik)
Shared-host rules: the stack uses its own compose project (`agroseason`) and volumes; `docker-compose.prod.yml` only *joins* the existing Traefik network and adds labels. Never run `docker system prune`, never edit the existing Traefik config.
1. Inspect first: `docker ps`, `docker network ls`, Traefik static config (entrypoint name, cert resolver name, network name), free ports, DNS A record for your domain → VPS IP.
2. `git clone <repo> /opt/agroseason-ai`; create `/opt/agroseason-ai/.env` from `.env.example` (`chmod 600`): strong `POSTGRES_PASSWORD`/`REDIS_PASSWORD`, `DOMAIN`, `TRAEFIK_NETWORK`, `TRAEFIK_ENTRYPOINT`, `TRAEFIK_CERTRESOLVER`, `CORS_ORIGINS=https://<domain>`, API keys.
3. From your Mac: `scripts/deploy.sh user@host main` (asks for confirmation).
4. Verify: `scripts/health-check.sh https://<domain>`.
5. Backups: cron on VPS `COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml" scripts/backup.sh /opt/backups/agroseason` (daily). Restore: `scripts/restore.sh <dump>`.
6. Update: `scripts/deploy.sh user@host main`. Rollback: `scripts/rollback.sh user@host`.
Troubleshooting: `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs api worker`; certificate issues → check resolver name and that ports 80/443 reach Traefik.
