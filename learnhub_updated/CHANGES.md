# LearnHub changes

Implemented from the requested learning-platform flow:

- Logged-out visitors can open only Linux Chapter 1 as a preview.
- Server-side checks prevent direct URL access to later chapters without signup/login.
- Enrollment is required before full course progression and practical terminals are available.
- Signup page is clearer and preserves a requested `next` URL.
- Course page has explicit signup/login/enrollment messaging.
- Linux curriculum expanded to 4 modules / 13 practical chapters.
- Each chapter contains notes plus practical objective, commands, tasks, and verification steps.
- Sandbox image now includes common Linux/DevOps troubleshooting tools.
- Practice terminal has visible retry/error handling.
- Terminal WebSocket requires a short-lived HMAC token before creating a Docker sandbox.
- Added automated gating tests in `apps/skills/tests/test_gating.py`.
- README updated with VS Code + Docker setup and verification steps.

## Validation performed here

Python source files were syntax-checked with `compileall`. A full Django test run and Docker integration test could not be executed in this environment because Docker is unavailable and external package downloads are blocked.
