# LearnHub — Skills Learning Platform

A Django-based practice-first learning platform. The starter course is **Linux Fundamentals** with guided command-line exercises and disposable Ubuntu labs.

## What is included now

- **Public preview:** unauthenticated visitors can open only the first Linux chapter.
- **Clear signup gate:** the course page shows exactly what is locked and provides **Create free account** / **Log in** actions.
- **Enrollment gate:** after signup, click **Enroll free & start practicing** to unlock the full course.
- **Sequential progression:** each next chapter unlocks only after the previous enrolled chapter is completed.
- **Practical instructions:** every Linux lesson contains a practical objective, commands to try, step-by-step tasks, and a verification check.
- **Real terminal:** enrolled users can launch an ephemeral Ubuntu terminal for the practical.
- **Terminal authentication:** the WebSocket requires a short-lived token from the signed-in/enrolled lesson page before any Docker sandbox is created.
- **Better terminal failure message:** if Docker or the terminal service is not running, the UI tells you what to start instead of silently failing.

## Linux curriculum

The seed command rebuilds 4 modules / 13 practical chapters:

1. Linux Foundations
2. Text, Pipes & Search
3. Linux Administration Essentials
4. Networking & Bash Automation

## Local testing in VS Code (Windows / macOS / Linux)

### Option A — Docker Compose (recommended because the practice terminal is Docker-based)

1. Install **Docker Desktop** and make sure it is running.
2. Open the `learnhub` folder in VS Code.
3. Copy `.env.example` to `.env`.
4. Open the VS Code terminal and build the disposable learner image:

```bash
docker compose build sandbox
```

5. Start the application and terminal service:

```bash
docker compose up --build
```

Leave this terminal running.

6. Open a second VS Code terminal and run:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_linux_course
```

7. Create an admin user only if you want to inspect/edit content through Django Admin:

```bash
docker compose exec web python manage.py createsuperuser
```

8. Open:

`http://localhost:8000/`

### Verify the signup/content gate

- Open the Linux course while logged out.
- Chapter 1 should be clickable.
- Chapters 2 onward should show **Sign up to unlock**.
- Open Chapter 1: the notes are visible, but the practical terminal is locked.
- Click **Sign up free**.
- After signup, click **Enroll free & start practicing**.
- Chapter 1 can now be completed and Chapter 2 should unlock.
- Continue chapter by chapter.

### Verify the real practical terminal

After enrollment:

1. Open a lesson.
2. Read **Practical objective**, **Commands to try**, and **Tasks**.
3. Click **Start practice**.
4. A browser terminal should open on port `8765`.
5. Try the listed commands inside the disposable Ubuntu environment.

If the terminal does not open, confirm both:

```bash
docker compose ps
docker compose logs terminal
```

The `terminal` service must be running, and the `learnhub-sandbox` image must exist. Build it once with `docker compose build sandbox` and rebuild it whenever you change `sandbox/Dockerfile`.

## Important security note

This local terminal architecture mounts the host Docker socket into the terminal service. That gives the service powerful control over the local Docker daemon. **Use this only on your development machine. Do not expose it to the public internet as-is.** A real deployment needs isolated worker nodes/VMs, stronger sandboxing, authenticated WebSocket sessions, resource/concurrency limits, and restricted network egress.
