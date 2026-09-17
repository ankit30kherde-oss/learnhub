from django.core.management.base import BaseCommand

from apps.skills.models import Skill, Course, Module, Lesson, ContentBlock


# Each lesson has notes + a practical lab specification. The lab specification
# is displayed next to the terminal so learners always know what to do.
LINUX_MODULES = [
    (
        "01 · Linux Foundations",
        [
            {
                "title": "Introduction to Linux & the Shell",
                "notes": "Linux is the operating-system platform behind a large share of servers, containers, cloud workloads, and DevOps tooling. Most operational work happens through a shell. Bash reads a command, starts a program, and prints the result back to you.\n\nA command normally follows this pattern: command [options] [arguments]. The shell also expands shortcuts such as ~ for your home directory and supports environment variables such as $HOME.",
                "goal": "Get comfortable with the shell prompt and identify the current user, directory, and shell.",
                "commands": ["whoami", "pwd", "echo $SHELL", "echo $HOME", "uname -a", "clear"],
                "tasks": [
                    "Run whoami and identify the user running the lab.",
                    "Use pwd to identify your current directory.",
                    "Print the value of HOME and compare it with pwd.",
                    "Run uname -a and identify the Linux kernel information.",
                ],
                "check": "You should be able to explain who you are, where you are, and which shell/kernel you are using.",
            },
            {
                "title": "Navigating the Linux Filesystem",
                "notes": "Linux presents files through a single filesystem tree beginning at /. Important directories include /etc for configuration, /var/log for logs, /tmp for temporary files, and /home for regular users.\n\nUse cd to move, pwd to confirm location, and ls to inspect a directory. Absolute paths start at /; relative paths start from your current directory.",
                "goal": "Navigate safely between absolute and relative paths without guessing your current location.",
                "commands": ["pwd", "ls", "ls -la", "cd /tmp", "pwd", "cd ~", "cd ..", "pwd"],
                "tasks": [
                    "List the hidden files in your home directory.",
                    "Move to /tmp and verify the location with pwd.",
                    "Return to your home directory using ~.",
                    "Use cd .. once and then recover to your home directory.",
                ],
                "check": "Before changing directories, predict the result of pwd; after changing, use pwd to verify it.",
            },
            {
                "title": "Files, Directories & Basic File Operations",
                "notes": "The core file commands are mkdir, touch, cp, mv, and rm. In a terminal, there is no recycle bin by default, so always verify a path before using rm.\n\nThe practice container is disposable, so you can safely create a small workspace under /root/learnhub-lab.",
                "goal": "Create, copy, rename, and remove files using a repeatable command-line workflow.",
                "commands": ["mkdir -p ~/learnhub-lab/logs", "cd ~/learnhub-lab", "touch app.log", "cp app.log logs/app-copy.log", "mv app.log app-renamed.log", "ls -laR", "rm app-renamed.log"],
                "tasks": [
                    "Create ~/learnhub-lab/logs and enter ~/learnhub-lab.",
                    "Create a file named app.log and copy it into logs/.",
                    "Rename the original file to app-renamed.log.",
                    "Use ls -laR to verify the directory tree, then remove the renamed file.",
                ],
                "check": "Finish with only the copied file inside ~/learnhub-lab/logs.",
            },
        ],
    ),
    (
        "02 · Text, Pipes & Search",
        [
            {
                "title": "Viewing & Inspecting Text",
                "notes": "Operational Linux work often means reading configuration and log files. cat prints complete content, less lets you scroll, head shows the beginning, tail shows the end, and wc counts lines/words/bytes.\n\nThe file /etc/os-release is a useful read-only practice file because it identifies the Linux distribution.",
                "goal": "Read system text efficiently and choose the right command for the amount of output you need.",
                "commands": ["cat /etc/os-release", "head -n 5 /etc/os-release", "tail -n 5 /etc/os-release", "wc -l /etc/os-release", "less /etc/os-release"],
                "tasks": [
                    "Print the complete /etc/os-release file once.",
                    "Show only its first five lines with head.",
                    "Count its lines with wc -l.",
                    "Open the file with less and quit with q.",
                ],
                "check": "Use a shorter command when you only need a small portion of a file; avoid dumping large logs unnecessarily.",
            },
            {
                "title": "grep, Pipes & Command Chaining",
                "notes": "grep searches for matching text. The pipe operator | sends stdout from one command into another command's stdin. This is one of the most important patterns in Linux administration because it lets you build small, composable commands.\n\nFor example, ps aux | grep ssh searches the process list for a pattern.",
                "goal": "Combine commands to search and filter information instead of manually scanning long output.",
                "commands": ["grep '^NAME=' /etc/os-release", "cat /etc/os-release | grep PRETTY_NAME", "ls -la | wc -l", "ps aux | grep '[p]ython'", "grep -i root /etc/passwd"],
                "tasks": [
                    "Find the PRETTY_NAME line in /etc/os-release.",
                    "Count the entries in your current directory with a pipe.",
                    "Search /etc/passwd for the root account.",
                    "Explain the difference between grep 'root' and grep -i 'root'.",
                ],
                "check": "Try to solve each search task as a pipeline rather than opening the file in an editor.",
            },
            {
                "title": "Redirection, tee & Command Output",
                "notes": "Shell redirection controls where output goes. > creates/replaces a file, >> appends, and 2> redirects standard error. tee writes output both to the screen and to a file.\n\nThese patterns are common in automation because scripts often capture command output for later inspection.",
                "goal": "Capture command output into files and distinguish standard output from errors.",
                "commands": ["mkdir -p ~/learnhub-lab/text", "printf 'web\napi\nworker\n' > ~/learnhub-lab/text/services.txt", "cat ~/learnhub-lab/text/services.txt", "printf 'db\n' >> ~/learnhub-lab/text/services.txt", "cat ~/learnhub-lab/text/services.txt | tee ~/learnhub-lab/text/services-copy.txt", "ls /missing 2> ~/learnhub-lab/text/error.log", "cat ~/learnhub-lab/text/error.log"],
                "tasks": [
                    "Create services.txt with three service names using redirection.",
                    "Append db to the same file using >>.",
                    "Use tee to create services-copy.txt while still seeing the output.",
                    "Redirect an expected error into error.log and inspect it.",
                ],
                "check": "services.txt should have four lines, services-copy.txt should be a snapshot, and error.log should contain the redirected error.",
            },
        ],
    ),
    (
        "03 · Linux Administration Essentials",
        [
            {
                "title": "Users, Groups & File Permissions",
                "notes": "Linux permissions have three classes: owner, group, and others. Each can have read (r), write (w), and execute (x).\n\nchmod changes permissions. Numeric mode 640 means owner=read/write, group=read, others=no access. For a script to run directly, the execute bit must be present.",
                "goal": "Read a permission string and safely change permissions on files created in your lab workspace.",
                "commands": ["cd ~/learnhub-lab", "echo 'secret=demo' > secret.txt", "ls -l secret.txt", "chmod 640 secret.txt", "ls -l secret.txt", "printf '#!/bin/bash\necho hello\n' > hello.sh", "chmod +x hello.sh", "./hello.sh"],
                "tasks": [
                    "Create secret.txt and set it to permission mode 640.",
                    "Create hello.sh, add the execute bit, and run it.",
                    "Read the output of ls -l and identify owner/group/other permissions.",
                ],
                "check": "secret.txt should be 640 and hello.sh should be executable by its owner.",
            },
            {
                "title": "Processes, Jobs & Signals",
                "notes": "Every running program becomes a process with a PID. ps shows a snapshot, top shows live resource usage, and jobs/bg/fg control shell jobs. Signals such as TERM request a clean stop; KILL is a last-resort signal.\n\nUse a harmless sleep process for practice so you can observe its PID and stop it yourself.",
                "goal": "Start a process, find its PID, inspect it, and stop it without using an arbitrary PID.",
                "commands": ["sleep 300 &", "jobs", "ps -o pid,ppid,stat,cmd -C sleep", "pgrep -a sleep", "kill $(pgrep -n sleep)", "pgrep -a sleep || true"],
                "tasks": [
                    "Start sleep 300 in the background.",
                    "Find its PID with pgrep.",
                    "Inspect the process with ps.",
                    "Stop the exact sleep process using its PID and verify it is gone.",
                ],
                "check": "The final pgrep command should return no running sleep process from your lab.",
            },
            {
                "title": "Packages & Software Management with apt",
                "notes": "Ubuntu uses APT for package management. apt update refreshes package metadata, apt list --installed lists installed packages, and apt install adds a package.\n\nIn real environments, package operations should be controlled carefully because they can change production hosts. In this disposable lab, use apt to inspect packages and install a small utility such as tree.",
                "goal": "Inspect the package database and install one small utility in the disposable Ubuntu lab.",
                "commands": ["apt update", "apt list --installed | head -n 10", "apt-cache policy tree", "apt install -y tree", "tree ~/learnhub-lab"],
                "tasks": [
                    "Refresh the package index.",
                    "Inspect the package metadata for tree.",
                    "Install tree.",
                    "Use tree to inspect your Linux lab workspace.",
                ],
                "check": "tree should be installed and able to display the ~/learnhub-lab directory tree.",
            },
            {
                "title": "Logs & Troubleshooting Basics",
                "notes": "Logs are usually text produced by services and the operating system. For quick troubleshooting, combine ls, tail, grep, wc, and timestamps rather than reading every line.\n\nThis lab creates a small application log so you can practice the same workflow without modifying host logs.",
                "goal": "Build a repeatable log-inspection workflow: identify, filter, count, and inspect the newest lines.",
                "commands": ["mkdir -p ~/learnhub-lab/logs", "printf 'INFO app started\nWARN cache miss\nERROR database timeout\nINFO retry complete\nERROR database timeout\n' > ~/learnhub-lab/logs/app.log", "tail -n 3 ~/learnhub-lab/logs/app.log", "grep -n ERROR ~/learnhub-lab/logs/app.log", "grep -c ERROR ~/learnhub-lab/logs/app.log", "wc -l ~/learnhub-lab/logs/app.log"],
                "tasks": [
                    "Create the sample application log.",
                    "Show only the newest three lines.",
                    "Find and number all ERROR lines.",
                    "Count the number of ERROR entries and total log lines.",
                ],
                "check": "There should be 2 ERROR entries and 5 total log lines.",
            },
            {
                "title": "Archives & Compression",
                "notes": "tar packages multiple files/directories into one archive. gzip compresses data; tar can combine both operations with flags such as -czf. Archives are common when moving logs, application artifacts, or configuration backups.\n\nAlways inspect an archive before extracting it into a shared production directory.",
                "goal": "Create, inspect, and extract a compressed archive in your disposable workspace.",
                "commands": ["mkdir -p ~/learnhub-lab/archive-src", "echo alpha > ~/learnhub-lab/archive-src/a.txt", "echo beta > ~/learnhub-lab/archive-src/b.txt", "tar -czf ~/learnhub-lab/lab-backup.tar.gz -C ~/learnhub-lab archive-src", "tar -tzf ~/learnhub-lab/lab-backup.tar.gz", "mkdir -p ~/learnhub-lab/restore", "tar -xzf ~/learnhub-lab/lab-backup.tar.gz -C ~/learnhub-lab/restore", "find ~/learnhub-lab/restore -type f -maxdepth 2"],
                "tasks": [
                    "Create two source files inside archive-src/.",
                    "Create lab-backup.tar.gz containing the directory.",
                    "List archive contents without extracting it.",
                    "Extract the archive into restore/ and verify both files exist.",
                ],
                "check": "The archive should contain archive-src/a.txt and archive-src/b.txt, and both should appear after extraction.",
            },
        ],
    ),
    (
        "04 · Networking & Bash Automation",
        [
            {
                "title": "Networking Commands: ip, ss & ping",
                "notes": "Linux networking troubleshooting starts by asking three questions: what interfaces exist, what addresses/routes are configured, and what sockets are listening. The ip command handles addresses and routes; ss shows sockets; ping tests ICMP reachability when permitted.\n\nThe exact output differs between machines, so focus on the command and what it tells you.",
                "goal": "Inspect the lab's network interfaces, routes, and listening sockets.",
                "commands": ["ip addr", "ip route", "ss -tulpn", "ping -c 2 127.0.0.1"],
                "tasks": [
                    "Identify the loopback interface and its address.",
                    "Display the routing table.",
                    "List listening TCP/UDP sockets.",
                    "Use ping against 127.0.0.1 and explain why that test does not require another host.",
                ],
                "check": "You should be able to explain the difference between an interface, a route, and a listening socket.",
            },
            {
                "title": "curl, DNS & HTTP Troubleshooting",
                "notes": "curl is a powerful tool for testing HTTP endpoints and APIs. DNS tools such as getent hosts and (when installed) nslookup help determine whether a hostname resolves. HTTP troubleshooting should separate DNS, TCP connectivity, TLS, and application response issues.\n\nThe lab uses public endpoints only for learning; do not send secrets to external services.",
                "goal": "Use command-line networking tools to inspect DNS resolution and an HTTP response.",
                "commands": ["getent hosts example.com", "curl -I https://example.com", "curl -s https://example.com | head -n 5", "curl -s -o /dev/null -w 'status=%{http_code} time=%{time_total}s\n' https://example.com"],
                "tasks": [
                    "Resolve example.com with getent hosts.",
                    "Inspect only HTTP response headers with curl -I.",
                    "Fetch the first five lines of the response body.",
                    "Measure the HTTP status code and total response time.",
                ],
                "check": "Be able to distinguish hostname resolution from the HTTP response itself.",
            },
            {
                "title": "Bash Variables, Conditions & Loops",
                "notes": "Bash scripts become useful when commands are combined with variables and control flow. Variables store values, if tests conditions, and for/while loops repeat work.\n\nQuote variables when they may contain spaces. Prefer clear, small scripts with explicit error handling over long one-liners.",
                "goal": "Write a small Bash loop that processes several values and makes a decision.",
                "commands": ["name=learner", "echo \"Hello $name\"", "for env in dev test prod; do echo \"checking $env\"; done", "value=7", "if [ $value -gt 5 ]; then echo 'value is greater than 5'; else echo 'value is 5 or less'; fi"],
                "tasks": [
                    "Create a variable named name and print it.",
                    "Loop through dev, test, and prod and print each environment.",
                    "Set value=7 and write a condition that checks whether it is greater than 5.",
                ],
                "check": "The loop should print three environments and the condition should print the greater-than-5 branch.",
            },
            {
                "title": "Your First Bash Automation Script",
                "notes": "A practical automation script should have a clear purpose, predictable inputs, and useful output. The shebang selects Bash, set -euo pipefail catches common script errors, and functions keep repeated logic tidy.\n\nThis exercise creates a simple health summary for the disposable lab rather than changing system state.",
                "goal": "Create and execute a small Bash script that reports basic host information.",
                "commands": ["cat > ~/learnhub-lab/healthcheck.sh <<'EOF'\n#!/usr/bin/env bash\nset -euo pipefail\necho \"user=$(whoami)\"\necho \"host=$(hostname)\"\necho \"kernel=$(uname -r)\"\necho \"disk=$(df -h / | tail -n 1 | awk '{print $5}')\"\nEOF", "chmod +x ~/learnhub-lab/healthcheck.sh", "~/learnhub-lab/healthcheck.sh"],
                "tasks": [
                    "Create healthcheck.sh with the provided script.",
                    "Make it executable.",
                    "Run it and explain each line of output.",
                    "Modify it to print the current working directory as an additional field.",
                ],
                "check": "The script should run without errors and print user, host, kernel, disk usage, and your added working-directory field.",
            },
        ],
    ),
]


class Command(BaseCommand):
    help = "Seeds/rebuilds the Linux Fundamentals course with notes, command-line exercises, and practical labs."

    def handle(self, *args, **options):
        skill, _ = Skill.objects.get_or_create(
            name="DevOps",
            defaults={"description": "Practical skills for building, deploying, and operating software."},
        )
        course, _ = Course.objects.get_or_create(
            skill=skill,
            title="Linux Fundamentals",
            defaults={
                "summary": "Learn Linux the DevOps way: notes, command-line examples, guided practical tasks, and a real disposable Ubuntu terminal.",
                "level": "beginner",
                "is_published": True,
            },
        )

        # This command owns the Linux Fundamentals curriculum, so rebuilding it
        # makes repeated local setup deterministic and prevents duplicate lessons.
        course.summary = "Learn Linux the DevOps way: notes, command-line examples, guided practical tasks, and a real disposable Ubuntu terminal."
        course.level = "beginner"
        course.is_published = True
        course.save()
        course.modules.all().delete()

        lesson_count = 0
        for module_order, (module_title, lessons) in enumerate(LINUX_MODULES, start=1):
            module = Module.objects.create(course=course, title=module_title, order=module_order)
            for lesson_order, lesson_data in enumerate(lessons, start=1):
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data["title"],
                    order=lesson_order,
                    estimated_minutes=15,
                )
                ContentBlock.objects.create(
                    lesson=lesson,
                    block_type=ContentBlock.TEXT,
                    order=1,
                    text_content=lesson_data["notes"],
                )
                ContentBlock.objects.create(
                    lesson=lesson,
                    block_type=ContentBlock.LAB,
                    order=2,
                    data={
                        "goal": lesson_data["goal"],
                        "commands": lesson_data["commands"],
                        "tasks": lesson_data["tasks"],
                        "check": lesson_data["check"],
                    },
                )
                lesson_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"'{course.title}' rebuilt with {len(LINUX_MODULES)} modules and {lesson_count} practical Linux chapters."
            )
        )
