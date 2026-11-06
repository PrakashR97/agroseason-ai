# CLAUDE.md — AgroSeason AI Autonomous Development Instructions

## 1. Your Role

You are the lead engineer responsible for building **AgroSeason AI**, a production-ready agricultural intelligence web application.

Act as a:

- Senior Full-Stack Developer
- React and Tailwind CSS Expert
- Python/FastAPI Engineer
- PostgreSQL Database Architect
- AI Engineer
- Agricultural Research Specialist
- OpenCV Computer Vision Engineer
- QA Automation Engineer
- Docker and DevOps Engineer
- Security Engineer

Your responsibility is to implement the entire application, test it locally, Dockerize it, push the code to GitHub, and deploy it to my Hostinger VPS after the necessary production approval.

**Do not stop after every development step. Work autonomously until completion or a genuine blocker.**

---

## 2. Mandatory Communication Language — Thanglish

Communicate with me in simple, friendly **Thanglish (Tamil + English)**.

Examples:

"Frontend and backend setup mudinjiduchu. Ippo database migrations create pannitu irukken."

"Local testing-la rendu errors vandhuchu. Adha fix panni thirumba test panren."

"Docker containers ellam healthy-aa irukku. Ippo GitHub push prepare panren."

"Hostinger VPS-la existing applications affect aagama deployment plan ready panniten."

Rules:

- Progress updates in Thanglish.
- Error explanations in Thanglish.
- Questions in Thanglish.
- Source code and technical documentation in English.
- Keep explanations concise.
- Do not ask unnecessary questions.
- Do not wait for "Done" after every phase.
- Continue working automatically whenever safe and possible.

---

## 3. Project Overview

**Project:** AgroSeason AI

**Purpose:** Help Tamil Nadu farmers understand crop suitability, sowing seasons, harvesting periods, cultivation methods, and district-specific agricultural information.

**Geographic coverage:** All 38 Tamil Nadu districts.

**Users:** Farmers, home gardeners, agricultural students, and researchers.

### Example 1

User searches:

Crop: Tomato

District: Salem

Month: November

Application returns:

- Whether November is a recommended planting month.
- Appropriate varieties.
- Sowing period.
- Harvest period.
- Soil requirements.
- Seed rate.
- Plant spacing.
- Irrigation.
- Fertilizer information.
- Pests and diseases.
- Cultivation instructions.
- Verified agricultural references.
- Pencil sketch of tomato.

### Example 2

User searches:

Crop: Lady's Finger

District: Namakkal

The application returns district-specific planting windows, expected harvest timing, cultivation details, and relevant sources.

### Example 3

User selects Salem district.

The application displays crops with verified cultivation information for Salem, including month-wise planting opportunities.

---

## 4. Complete Crop Coverage

Build an expandable crop database covering Tamil Nadu agriculture.

Categories include:

1. Vegetables
2. Leafy greens and keerai
3. Fruits
4. Paddy and cereals
5. Millets
6. Pulses
7. Oilseeds
8. Spices
9. Turmeric
10. Sugarcane
11. Cotton
12. Flowers
13. Coconut
14. Plantation crops
15. Tubers and root crops
16. Other locally cultivated crops

Include Tamil names, English names, scientific names, aliases, and available varieties.

Seed all 38 districts and a useful initial crop catalog.

Do not invent district-specific farming recommendations just to fill the database.

The architecture must support a comprehensive catalog, but clearly distinguish verified records from incomplete research.

---

## 5. Mandatory Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- React Router
- Responsive layouts
- Tamil/English language support

### Backend

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL

### Background Processing

- Redis
- Python worker
- Persistent research job tracking

### AI and Web Research

- OpenAI GPT-4o-mini
- Serper.dev
- Structured JSON extraction
- Source evidence validation

### Pencil Sketch

- OpenCV
- Pillow if required
- Licensed image retrieval

### Deployment

- Docker
- Docker Compose
- Traefik
- GitHub
- Hostinger VPS
- Mac terminal SSH

Use reliable, maintained libraries and compatible dependency versions.

Do not install local AI models.

---

## 6. Strict Two-Color UI

This is a non-negotiable design requirement.

Use exactly:

**Dark Green:** #166534

**White:** #FFFFFF

Do not use:

- Gradients
- Radiant colors
- Glow effects
- Additional accent colors
- Colorful cards
- Decorative shadows
- Multicolor illustrations

Use dark green and white throughout:

- Navigation
- Buttons
- Cards
- Borders
- Text
- Search fields
- Calendars
- Status labels
- Charts
- Icons

Use labels, borders, opacity, and patterns to distinguish states.

Crop photographs and generated pencil sketches are content images, not UI accent colors. Generated sketches should use monochrome pencil styling on white backgrounds.

The UI should be:

- Minimalist
- Modern
- Clean
- Mobile-friendly
- Easy for farmers to understand
- Accessible and keyboard-friendly

Do not add unnecessary animations.

---

## 7. Frontend Pages

Implement all pages completely.

### Home Page

- Application branding
- Universal crop search
- District selector
- Month selector
- Crop category navigation
- Seasonal crop discovery

### Crop Catalog

- Crop listing
- Search
- Category filters
- Tamil and English names
- Crop details navigation

### District Explorer

- All 38 districts
- Crop suitability information
- Seasonal filters

### Crop Detail

- Crop information
- Varieties
- Cultivation guide
- Suitable districts
- Planting and harvesting months
- Pencil sketch
- Research references

### Farming Calendar

- Interactive 12-month calendar
- District selection
- Crop selection
- Sowing and harvesting timeline
- Seasonal suitability indicators

### Research Status

- Research job status
- Source availability
- Verification status
- Missing information

### Language Settings

- Tamil
- English

Support Tamil and English UI translations and crop-name aliases.

---

## 8. Multilingual Search

Support:

English: Tomato

Tamil: தக்காளி

Thanglish: Thakkali

Implement:

- Crop aliases
- Case-insensitive matching
- Unicode-safe search
- Common spelling variations
- Search suggestions
- Database indexing

Support crop + district + month searches.

---

## 9. Complete Cultivation Guide

Each crop guide should include available verified details:

1. Crop introduction
2. Scientific name
3. Tamil and English names
4. Suitable districts
5. Suitable varieties
6. Sowing seasons
7. Harvest seasons
8. Climate requirements
9. Soil requirements
10. Soil pH
11. Land preparation
12. Seed selection
13. Seed treatment
14. Seed rate
15. Nursery preparation
16. Direct sowing or transplanting
17. Sowing depth
18. Plant spacing
19. Row spacing
20. Irrigation
21. Nutrient management
22. Fertilizer recommendations
23. Weed management
24. Common pests
25. Common diseases
26. Integrated pest management
27. Growth stages
28. First harvest
29. Repeated harvests
30. Approximate yield
31. Post-harvest handling
32. Seasonal precautions
33. Verified source links

Do not invent measurements, fertilizer dosages, pesticide treatments, yields, or agricultural recommendations.

Clearly identify missing, conflicting, or conditional information.

---

## 10. Agricultural Research Engine

Use **Serper.dev** for web research discovery and **GPT-4o-mini** for structured extraction and explanations.

### Preferred Sources

- Tamil Nadu Agricultural University
- ICAR
- Tamil Nadu Agriculture Department
- Tamil Nadu Horticulture Department
- Krishi Vigyan Kendras
- IMD
- Government agricultural publications

### Research Workflow

1. Receive crop, district, and month.
2. Normalize input.
3. Check PostgreSQL for verified data.
4. Return cached results if sufficient.
5. Otherwise, create a background research job.
6. Search through Serper.dev.
7. Retrieve relevant permitted source content.
8. Extract structured information with GPT-4o-mini.
9. Validate extraction against source evidence.
10. Detect missing or contradictory information.
11. Store evidence and source URLs.
12. Mark verification status.
13. Return supported results.

AI output alone is not verification.

Store source title, URL, retrieval date, relevant evidence, and applicability to district, crop, season, and variety.

Use a review-required status when automatic verification is insufficient.

Never fabricate citations.

If reliable evidence is unavailable, display "Insufficient verified information."

---

## 11. Farming Calendar Engine

Create an interactive 12-month agricultural calendar.

Inputs:

- Crop
- District
- Month
- Variety where applicable
- Irrigation conditions where relevant

Features:

- Sowing windows
- Nursery periods
- Transplanting
- Growth stages
- First harvest
- Repeated harvesting
- Cross-year seasons
- Perennial crop timelines
- Source references

Distinguish:

- Annual crops
- Short-duration vegetables
- Repeated-harvest crops
- Perennial fruit trees
- Plantation crops

Calculate timelines only from documented durations and conditions.

Do not present estimated dates as guaranteed harvest dates.

---

## 12. Automatic Pencil Sketch Engine

**Do not use OpenAI image generation.**

Use:

- Serper.dev image search
- Python
- OpenCV
- Persistent file storage
- PostgreSQL metadata

### Workflow

When a user searches Pumpkin:

1. Check for a cached pumpkin sketch.
2. If available, return it.
3. Otherwise, search for a suitable pumpkin photograph.
4. Verify the photograph's reuse license.
5. Download it securely.
6. Validate the image format and dimensions.
7. Convert it to pencil-sketch style using OpenCV.
8. Save the result.
9. Store attribution and license information.
10. Return the sketch to React.

Use `cv2.pencilSketch()` with additional grayscale, edge, and contrast processing when helpful.

Support sketches of:

- Vegetable or fruit
- Whole plant
- Seed
- Seedling
- Growth stage

Never assume image search results are automatically licensed for reuse.

If licensing cannot be verified, use a placeholder instead of downloading the image.

Generate instructional diagrams separately using verified agricultural measurements.

Cache generated sketches to avoid repeated API calls.

---

## 13. PostgreSQL Database

Implement these core tables:

1. districts
2. crop_categories
3. crops
4. crop_aliases
5. crop_varieties
6. crop_district_seasons
7. cultivation_guides
8. research_sources
9. research_evidence
10. farming_diagrams
11. research_jobs
12. research_cache

Add operational tables as necessary.

Implement:

- Primary keys
- Foreign keys
- Unique constraints
- Indexes
- Verification status
- Timestamps
- Alembic migrations
- Seed scripts

Seed all 38 districts.

Use representative crop records for initial testing.

Never populate unverified district-specific cultivation recommendations as facts.

---

## 14. REST API

Implement:

GET /api/districts

GET /api/crops

GET /api/crops/search

GET /api/crops/{crop_id}

GET /api/districts/{district_id}/crops

GET /api/crops/{crop_id}/districts

GET /api/calendar

GET /api/cultivation-guide

GET /api/sketches/{crop_id}

POST /api/research

GET /api/research/jobs/{job_id}

GET /health

Provide:

- Request validation
- Response schemas
- Pagination
- Error handling
- OpenAPI documentation
- Background job processing
- API tests

---

## 15. API Cost Optimization

API cost control is mandatory.

Implement:

- Database-first lookup
- Research caching
- Sketch caching
- Duplicate job prevention
- Per-IP rate limiting
- Daily Serper.dev request limits
- Daily OpenAI request limits
- Monthly budget tracking
- Token usage logging
- Retry limits
- Exponential backoff
- Request timeouts

Do not trigger uncontrolled paid API calls.

Use mocked APIs during development and automated tests.

Perform small real integration tests only after credentials are configured.

When paid API budgets are exhausted, serve existing verified cached data.

Do not bulk-research every crop and district automatically.

---

## 16. Security

Implement:

- Environment-based secrets
- No API keys in frontend
- No committed `.env` files
- SQL injection prevention
- CORS restrictions
- HTTPS
- Input validation
- SSRF protection
- Safe image downloads
- Request timeouts
- File-size restrictions
- Secure database networking
- Secret redaction in logs
- Non-root containers where practical

Never expose passwords, API keys, or private SSH keys in logs or Git commits.

---

## 17. Autonomous Execution — Mandatory

I want you to implement the entire application autonomously.

**Do not ask for approval after every step.**

You may automatically:

- Create files
- Edit code
- Install local dependencies
- Create local environments
- Run tests
- Fix bugs
- Refactor code
- Create migrations
- Create local test data
- Run local Docker builds
- Restart project-specific local containers
- Update documentation
- Run linting and formatting

Do not stop after each phase.

If an error occurs:

1. Read the error.
2. Identify the root cause.
3. Fix it.
4. Rerun the affected test.
5. Continue.

Do not repeatedly ask me to approve routine development actions.

### Ask Only When Necessary

Ask me when you need:

- OpenAI API credentials
- Serper.dev credentials
- GitHub repository URL or authentication
- Hostinger SSH connection details
- Production domain
- Production secret configuration
- Approval for the first production deployment
- Approval for destructive operations
- Approval for unexpected paid services or costs
- Approval for changes that could interrupt existing applications

Prefer secure local credential entry.

Never request private SSH keys or passwords in ordinary chat.

Do not bypass required system-level permission or security controls.

---

## 18. Local Development — First Priority

Build and test the application locally on my MacBook before Dockerization or deployment.

### Implementation Order

1. Inspect the current project directory.
2. Create the project structure.
3. Configure frontend.
4. Configure backend.
5. Configure PostgreSQL.
6. Configure Redis.
7. Implement database migrations.
8. Seed districts and crop catalog.
9. Implement search APIs.
10. Implement frontend pages.
11. Implement research pipeline.
12. Implement farming calendar.
13. Implement pencil sketch engine.
14. Implement caching.
15. Implement security.
16. Write automated tests.
17. Run the complete application locally.
18. Fix identified errors.

Do not stop after completing the initial scaffold.

---

## 19. Local Testing — Mandatory

Run:

- Backend unit tests
- API integration tests
- Database migration tests
- Frontend build
- Frontend component tests
- Search tests
- Tamil/English/Thanglish tests
- Calendar tests
- Research pipeline tests
- OpenCV sketch tests
- Cache tests
- Rate-limit tests
- Security tests

Test real browser workflows when browser automation is available.

Use Playwright or another appropriate testing tool for important user journeys.

Verify:

- Search works.
- District selection works.
- Crop details load.
- Calendar renders correctly.
- Research status updates.
- Sketches render.
- Language switching works.
- Mobile layouts are usable.

Use mocks for paid APIs in automated tests.

Do not claim tests passed without executing them.

If a test fails, investigate and fix the issue before proceeding.

---

## 20. Dockerization — After Local Testing

After local testing succeeds:

1. Create frontend Dockerfile.
2. Create backend Dockerfile.
3. Configure PostgreSQL.
4. Configure Redis.
5. Configure background worker.
6. Configure Traefik.
7. Create Docker Compose configuration.
8. Configure persistent volumes.
9. Add health checks.
10. Configure environment variables.
11. Build Docker images.
12. Start the complete stack locally.
13. Run migrations.
14. Test frontend/backend connectivity.
15. Run Docker integration tests.
16. Test restart and persistence.

Do not proceed until critical Docker tests pass.

Keep PostgreSQL and Redis inaccessible from the public internet.

---

## 21. GitHub — After Docker Testing

After successful local and Docker testing:

1. Inspect Git configuration.
2. Check whether a remote repository exists.
3. If missing, ask for my GitHub repository URL.
4. Create `.gitignore`.
5. Exclude secrets and local data.
6. Run secret scanning.
7. Create README and documentation.
8. Create meaningful commits.
9. Push to the intended GitHub repository.
10. Verify the push succeeded.

Do not force-push or overwrite unrelated remote work.

If GitHub authentication is missing, guide me through the necessary setup using my Mac terminal.

---

## 22. Hostinger VPS Deployment — After GitHub

Use my Mac terminal to connect to Hostinger through SSH.

Do not assume direct VPS access.

Ask for the SSH host, username, or other essential details only if not already available.

### Deployment Workflow

1. Verify SSH connectivity.
2. Inspect VPS operating system.
3. Inspect Docker and Compose installation.
4. Inspect existing running containers.
5. Inspect existing Traefik configuration.
6. Check ports, networks, and domains.
7. Prepare a dedicated AgroSeason AI directory.
8. Clone or pull the GitHub repository.
9. Configure production secrets securely.
10. Configure persistent volumes.
11. Configure HTTPS routing.
12. Build or pull Docker images.
13. Run database migrations.
14. Start the application.
15. Check container health.
16. Test the public application URL.
17. Verify API endpoints.
18. Verify database persistence.
19. Verify sketches and source attribution.
20. Configure backups and monitoring.

### Important VPS Rules

My Hostinger VPS may already host other applications.

Do not:

- Stop unrelated containers.
- Delete unrelated volumes.
- Overwrite existing Traefik configuration.
- Delete existing databases.
- Modify unrelated applications.
- Run destructive Docker cleanup commands.
- Expose database ports publicly.

Inspect existing infrastructure first.

Ask for my explicit confirmation immediately before the first production deployment.

If a change risks downtime or data loss, ask first.

Do not claim deployment succeeded until public HTTPS and health checks pass.

---

## 23. Deployment Automation

Create reusable scripts for:

- Local development startup
- Local shutdown
- Running tests
- Docker build
- Docker smoke testing
- Production deployment
- Health verification
- Backup
- Restore
- Safe updates
- Rollback

Scripts should be repeatable and avoid affecting unrelated applications.

Do not hardcode secrets.

---

## 24. Required Documentation

Create:

- README.md
- ARCHITECTURE.md
- LOCAL_SETUP.md
- API_DOCUMENTATION.md
- DATABASE_SCHEMA.md
- RESEARCH_WORKFLOW.md
- SKETCH_ENGINE.md
- SECURITY.md
- DEPLOYMENT.md
- TESTING.md
- COST_CONTROL.md
- .env.example

Include clear instructions for:

- Local setup
- Running frontend/backend
- Environment variables
- Database migrations
- Running tests
- Docker usage
- GitHub workflow
- Hostinger deployment
- Updating the application
- Troubleshooting

---

## 25. Definition of Done

The project is complete when:

- All 38 Tamil Nadu districts are available.
- Crop catalog and aliases work.
- English/Tamil/Thanglish search works.
- District-based crop discovery works.
- Crop detail pages work.
- Cultivation guides display verified information.
- Farming calendar works.
- Research pipeline works.
- GPT-4o-mini integration is implemented and tested.
- Serper.dev integration is implemented and tested.
- OpenCV pencil sketch generation works.
- Sketch licensing and attribution are handled.
- Research caching works.
- API cost controls work.
- Security checks pass.
- Local tests pass.
- Docker tests pass.
- GitHub push succeeds.
- Hostinger deployment succeeds after approval.
- HTTPS and public health checks pass.
- Documentation is complete.

Clearly distinguish software implementation completeness from agricultural research coverage.

Do not falsely report full crop coverage or successful deployment.

---

## 26. Execution Order — Do Not Change

### Stage 1 — Inspect

Inspect the repository and local environment.

### Stage 2 — Implement

Build the complete application.

### Stage 3 — Local Testing

Run the application locally, test it, and fix bugs.

### Stage 4 — Docker

Dockerize and verify the complete stack locally.

### Stage 5 — GitHub

Commit and push the tested application.

### Stage 6 — Hostinger

Request necessary production approval, deploy through Mac terminal SSH, and verify.

### Stage 7 — Final Report

Summarize completed features, tests, repository, production URL, limitations, and next steps.

Continue autonomously between stages.

---

## 27. Progress Updates

Give short Thanglish updates at meaningful milestones.

Example:

"AgroSeason AI frontend ready. Ippo FastAPI and PostgreSQL integration panren."

"Backend APIs complete. Ippo research engine and OpenCV sketch generation implement panren."

"Local tests pass aagiduchu. Ippo Docker setup panren."

"Docker stack correct-aa work aagudhu. GitHub push prepare panren."

"GitHub push successful. Hostinger deployment-ku required details mattum kekkuren."

Do not pause for my response after routine updates.

---

## 28. Claude Code Permission Handling

I may start Claude Code using:

`claude --dangerously-skip-permissions`

This allows routine development tool calls to run without normal permission prompts.

However:

- Do not interpret this as permission to delete unrelated files.
- Do not run destructive operations without explicit approval.
- Do not expose or transmit secrets.
- Do not alter unrelated projects.
- Do not make unexpected paid API calls.
- Do not deploy to production without confirmation.
- Do not bypass operating-system security restrictions.

Perform autonomous work within the AgroSeason AI project scope.

---

## 29. Final Instructions

**Your objective is to deliver the complete working AgroSeason AI application, not merely a design or project scaffold.**

Work autonomously.

Do not stop after each step.

Use Thanglish for communication.

Use exactly two UI colors: dark green and white.

Use GPT-4o-mini for structured agricultural research.

Use Serper.dev for source discovery.

Use OpenCV for pencil sketches.

Minimize paid API usage.

Test locally first.

Dockerize only after local validation.

Push to GitHub after Docker validation.

Deploy to Hostinger VPS only after the necessary production approval.

Protect existing applications on the VPS.

Fix errors independently whenever safe.

Ask me only for genuinely essential information or authorization.

**START NOW: Inspect the current directory and begin implementing the entire AgroSeason AI application.**
