# MitAiStudio Crew

A small multi-agent project powered by crewAI with two task types:
- Coffee brewing advice (outputs `brew_advice.txt`)
- First-person self-introduction (outputs `intro.md`, grounded in `knowledge/user_preference.txt`)

## How to Run

Prerequisites:
- Python >= 3.10 and < 3.14
- [UV](https://docs.astral.sh/uv/) installed for dependency management
- `OPENAI_API_KEY` set in a `.env` file at the project root

Install dependencies:
```bash
pip install uv
uv sync
```

Run the interactive flow:
```bash
uv run run_crew
```
When prompted, enter:
- For brewing advice: `brewing: <your requirement>`
- For self introduction: `self introduction`

Outputs:
- Self introduction: `intro.md`
- Brewing advice: `brew_advice.txt`

## Deploy via NANDA (EC2)

Expose this Crew as an internet-facing agent using the NANDA adapter.

Prereqs on EC2 (Amazon Linux/AL2023):
- `sudo dnf update -y && sudo dnf install -y python3.11 python3.11-pip certbot`
- Point your domain `A` record to the EC2 public IP.

Install deps with UV (includes `nanda-adapter` via `pyproject.toml`):
```bash
uv sync
```

Generate SSL certs (replace `your.domain.com`):
```bash
sudo certbot certonly --standalone -d your.domain.com
sudo cp -L /etc/letsencrypt/live/your.domain.com/fullchain.pem .
sudo cp -L /etc/letsencrypt/live/your.domain.com/privkey.pem .
sudo chown $USER:$USER fullchain.pem privkey.pem
chmod 600 fullchain.pem privkey.pem
```

Export environment variables:
```bash
export OPENAI_API_KEY=xxx              # CrewAI models
export ANTHROPIC_API_KEY=xxx           # NANDA registry/bridge
export DOMAIN_NAME=your.domain.com     # SSL + public URL
```

Start the NANDA bridge:
```bash
uv run nanda_mit_ai_studio
# or run in background
nohup uv run nanda_mit_ai_studio > out.log 2>&1 &
```

Check health and enrollment link:
```bash
curl -k https://$DOMAIN_NAME/api/health
cat out.log  # enrollment link appears here
```

Message routing:
- `self introduction` → runs `intro_task` (uses `knowledge/user_preference.txt`)
- `brewing: <your requirement>` → runs `research_task` then `brew_task`
- other text → runs `research_task` only

## Configuration

- Agents: `src/mit_ai_studio/config/agents.yaml`
- Tasks: `src/mit_ai_studio/config/tasks.yaml`
- Crew assembly: `src/mit_ai_studio/crew.py`
- Entry logic and inputs: `src/mit_ai_studio/main.py`
- User preferences and bio: `knowledge/user_preference.txt`

## What worked

- Added `intro_task` in `tasks.yaml` with `description` and `expected_output`, referencing `{user_preference}` as context.
- In `crew.py`:
  - Switched `intro_task` to use `self.tasks_config['intro_task']` and set `output_file='intro.md'`.
  - Updated `crew()` to accept an optional `tasks` parameter to filter tasks by method name, enabling the one-task "self introduction" path.
- After running interactively, successfully produced:
  - `intro.md` (first-person intro grounded by `knowledge/user_preference.txt`)
  - `brew_advice.txt` (reproducible pour-over recipe based on requirements)

## What didn’t

- Initially creating a `Task` inline in `crew.py` without `expected_output` caused a Pydantic validation error.
- Running via `crewai run` failed because the global CLI wasn’t available on PATH; using `uv run run_crew` works.
- `MitAiStudio().crew(tasks=tasks)` first failed with `unexpected keyword argument 'tasks'` because `@crew` method didn’t accept parameters; now `crew()` supports an optional `tasks` argument and applies filtering.

## What we learned

- Defining `Task` via YAML is more robust in crewAI; ensure required fields like `description` and `expected_output` are present.
- When using the `@crew` decorator for auto-assembled tasks, dynamic selection can be supported by adding an optional parameter in `crew()` to build a filtered task list.
- Prefer running with UV (`uv run run_crew`) to avoid relying on a global `crewai` CLI.
