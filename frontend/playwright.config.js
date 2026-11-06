import { defineConfig, devices } from '@playwright/test'

const DB = 'postgresql+psycopg://agro:agro_local_dev@localhost:5432/agroseason_e2e'
const env = { DATABASE_URL: DB, ALEMBIC_DATABASE_URL: DB, REDIS_URL: '', MEDIA_DIR: '/tmp/agro-e2e-media',
  RATE_LIMIT_PER_MINUTE: '100000', CORS_ORIGINS: 'http://127.0.0.1:5199' }

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: { baseURL: 'http://127.0.0.1:5199', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] }, grep: /@mobile/ },
  ],
  webServer: [
    {
      command: '../backend/.venv/bin/python e2e_fixture.py && ../backend/.venv/bin/python -m uvicorn app.main:app --port 8199',
      cwd: '../backend', env, url: 'http://127.0.0.1:8199/health', reuseExistingServer: false, timeout: 60000,
    },
    {
      command: 'npx vite --port 5199 --strictPort --host 127.0.0.1',
      env: { VITE_API_PROXY: 'http://127.0.0.1:8199' }, url: 'http://127.0.0.1:5199', reuseExistingServer: false, timeout: 30000,
    },
  ],
})
