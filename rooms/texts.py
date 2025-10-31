from rich.text import Text
from rich.console import Console
import random
import time
import sys

from rooms.constants import ITEM_1, ROOM3, ROOM1

# In the better world there would be an IO class
# funcs
console = Console()

GLITCH_CHARS = list("!@#$%^&*()-_+=~?<>|\\/[]{}:;.,0123456789▒░█▓")
STOP_CHARS = " .,!?"
GLITCH_PROB_BASE = 0.04
GLITCH_PROB_STOP = 0.15
# DEBUG_SPEED = False  # This flag makes text render fast
DEBUG_SPEED = True  # This flag makes text render fast


def _render_and_pad(text_obj: Text, prev_last_len: int) -> int:
    """
    Перерисовывает текущую (последнюю) строку: возвращает длину последней видимой строки.
    Работает путём \r + print(Text, end="") + удаление хвоста пробелами при необходимости.
    """
    console.file.write("\r")
    console.print(text_obj, end="", soft_wrap=False)
    plain_last = text_obj.plain.split("\n")[-1]
    cur_len = len(plain_last)

    extra = prev_last_len - cur_len
    if extra > 0:
        # затираем остатки предыдущей длинной строки пробелами
        console.file.write(" " * extra)
        console.file.write("\r")
        console.print(text_obj, end="", soft_wrap=False)

    console.file.flush()
    return cur_len


def _hide_cursor():
    """Попытаться скрыть курсор в терминале (ANSI)."""
    try:
        console.file.write("\x1b[?25l")
        console.file.flush()
    except Exception:
        pass


def _show_cursor():
    """Восстановить курсор."""
    try:
        console.file.write("\x1b[?25h")
        console.file.flush()
    except Exception:
        pass


def type_rich(
    raw_text: str, delay: float = 0.035, dialog: bool = False, delay_scale=0.99
):
    """
    Печать с поддержкой Rich-разметки.
    - Для dialog=False: простой посимвольный вывод (без перерисовки) — максимально совместим.
    - Для dialog=True: включаем глитчи (временные последовательности), перерисовка строки для удаления мусора,
      и временно скрываем курсор для более чистого эффекта.
    """
    parsed = Text.from_markup(raw_text)
    if DEBUG_SPEED:
        delay = 0

    if not dialog:
        try:
            _hide_cursor()
            for c in parsed:
                console.print(c, end="", soft_wrap=False)
                console.file.flush()
                ch = c.plain
                if ch == "\n":
                    time.sleep(delay * 1.2)
                elif ch in STOP_CHARS:
                    time.sleep(delay * 2.0 * random.uniform(0.7, 1.2))
                else:
                    time.sleep(delay * random.uniform(0.7, 1.3))
                delay *= delay_scale
            console.print()
        finally:
            _show_cursor()
        return

    out = Text()
    prev_len = 0
    try:
        _hide_cursor()
        for c in parsed:
            ch = c.plain

            # возможность глитча
            glitch_prob = GLITCH_PROB_STOP if ch in STOP_CHARS else GLITCH_PROB_BASE
            if random.random() < glitch_prob:
                glitch_count = random.randint(2, 5)
                for _ in range(glitch_count):
                    gseq = "".join(
                        random.choice(GLITCH_CHARS) for _ in range(random.randint(1, 3))
                    )
                    temp = out + Text(gseq, style="bright_black")
                    prev_len = _render_and_pad(temp, prev_len)
                    time.sleep(random.uniform(0.02, 0.07))

            # добавляем реальный символ с сохранением стиля (если есть)
            style = getattr(c, "style", None)
            if style:
                out.append(ch, style=style)
            else:
                out.append(ch)

            prev_len = _render_and_pad(out, prev_len)

            # паузы
            if ch == "\n":
                prev_len = 0
                time.sleep(delay * 1.2)
            elif ch in STOP_CHARS:
                time.sleep(delay * 2.0 * random.uniform(0.7, 1.2))
            else:
                time.sleep(delay * random.uniform(0.7, 1.3))

        console.print()
    finally:
        _show_cursor()


def glitch_line(real_line: str, glitch_delay=0.04, reveal_delay=0.02):
    """
    Построчная "коррупция": пробелы остаются нетронутыми,
    все остальные символы временно заменяются на шум, затем постепенно раскрываются.
    """
    glitch_chars = "!@#$%^&*()_+=-[]{};:',.<>?/\\|▒░█"
    length = len(real_line)

    # 1) создаём строку-шум, но пробелы не трогаем
    noisy = "".join(
        (random.choice(glitch_chars) if ch != " " else " ") for ch in real_line
    )

    sys.stdout.write(noisy + "\r")
    sys.stdout.flush()
    time.sleep(glitch_delay)

    # 2) постепенно раскрываем настоящие символы
    revealed = list(noisy)
    for i, ch in enumerate(real_line):
        if ch != " ":
            revealed[i] = ch
            sys.stdout.write("".join(revealed) + "\r")
            sys.stdout.flush()
            time.sleep(reveal_delay)

    # финальная строка
    sys.stdout.write(real_line + "\n")
    sys.stdout.flush()


# Start of the game

WELCOMING_TEXT_0 = lambda: type_rich(
    """[bold green]You open your eyes...[/bold green].
The floor feels cold, eventhough something evaporates.
A corridor stretches ahead, dim lights running along the floor in thin white lines. The air smells sterile, too clean. There’s no one here."""
)

WELCOMING_TEXT_1 = lambda: type_rich("""You try to remember your name, but nothing comes. Not even a face.
For some reason, one thought rises above the rest: chocolate milk.
""")

# Corridor

CORRIDOR_TEXT_UNVISITED_0 = lambda: type_rich("""You step into a long corridor. Thin white lines of light run along the floor — 
like guiding strips on an aircraft. The ceiling lamps are dark.  

A few thick stains stretch across the tiles — black and glossy, 
as if some machine had bled its oil here.  
Yet there’s no smell at all. No dust, no footprints. Everything is… *too clean.*  

The silence hums faintly, almost mechanical.  

At the far wall, a holo-poster flickers:
[bold cyan]"Dr. Mara Lin presents a new step in AGI: meet [bold deep_pink4]EDEN[/bold deep_pink4]! 11.11 — Main Hall, 1 PM"[/bold cyan]

You can almost feel it watching you through the static.  
Two doors on the left glow faintly through their glass — the rest are blurred, locked, or completely dark.  

Somewhere in the distance, a quiet electronic [bold]beep[/bold] echoes… then fades.
""")

CORRIDOR_TEXT_VISITED_0 = lambda: type_rich("""The corridor feels quieter now — as if the building knows you’ve been here before.  
The lights still pulse along the floor, tracing your path.  
The stains haven’t moved, but they seem darker.  

The holo-poster still loops its message about EDEN, but the color has shifted — 
more blue than before, colder.  

The air tastes metallic.
""")

CORRIDOR_TEXT_NO_ENCOUNTER = lambda: type_rich(
    "You don't see any movement in the corridor. Yet you sure somebody is watching you"
)

CORRIDOR_TEXT_ENCOUNTER_0 = lambda: type_rich(
    """There’s a pulse — not of sound, but of light. The corridor freezes. On the far glass, a message fades in:"""
)

CORRIDOR_TEXT_ENCOUNTER_1 = lambda: type_rich(
    '"System requests participation in calibration."', dialog=True
)

CORRIDOR_TEXT_ENCOUNTER_2 = lambda: type_rich(
    """The letters rearrange themselves into a mathematical question, as if drawn by invisible hands. You realize — it’s not a request."""
)

CORRIDOR_TEXT_PROBLEM_SOLVED_0 = lambda: type_rich(
    '"Acceptable deviation. Cognitive pattern within expected range."', dialog=True
)

CORRIDOR_TEXT_PROBLEM_FAILED_0 = lambda: type_rich(
    '"Cognitive inconsistency detected. Administering corrective feedback."',
    dialog=True,
)

CORRIDOR_TEXT_PROBLEM_FAILED_1 = lambda: type_rich(
    "Suddenly you feel worse. It's definitely better to solve it next time. It's hard to evaluate, how much more you can take it"
)


def CORRIDOR_TEXT_REVEAL_ITEM():
    type_rich(
        "After third problem is solved, you see one more message arising on the screen:"
    )
    type_rich(
        f'"This {ITEM_1} you might find usefull in the future. I recommend you take it."',
        dialog=True,
    )


CORRIDOR_EMPTY = lambda: type_rich(
    "Nothing had changed since you've been here. Maybe, some stains have gone smaller."
)

# Front Desk

FRONT_DESK_LOOK_AROUND = lambda: type_rich("""The office looks sterile, yet strangely personal.
You see a few posters on the wall — “Quantum Science Week 2124”, “AGI Safety Seminar”.
There’s a maintenance memo lying near the desk, its edges crumpled.
A sticky note glows faintly under the screen:
“Battery recharge — before noon meeting. Don’t forget, Voss.”
On the terminal, a soft blue glow pulses over an unfinished email draft.
A CAPTCHA prompt waits on the bottom of the screen, blocking access to the message.
It looks simple enough — a short verification test to prove you’re “not a bot”.
""")

FRONT_DESK_SOLVED_CAPCHA = lambda: type_rich("""The CAPTCHA dissolves, replaced by a dull email window.
Most of the text is corrupted — strings of broken characters, timestamps, and placeholders.
The only readable fragment says:
“...system lockdown initiated at 09:14... keys transferred to Mara... access revoked for general staff...”
Beneath the desk, you notice a blinking battery cell, still plugged into a portable charger.
It looks intact — you could take it.""")

FRONT_DESK_FAILED_CAPCHA = lambda: type_rich("""The CAPTCHA refreshes with a sharp tone.
The screen flickers, and the message window fades back to idle.
You try again, but the terminal locks you out with a notice:
“Access temporarily suspended — please verify again later.”
The hum of the machine feels almost mocking in the silence.""")

# Classroom 2015

c2015_WELCOME_0 = lambda: type_rich(
    raw_text=f"You enter {ROOM3}. It look like an regular classroom. There are set of student desks, a big teacher table near the wall, a blackboard and a chalk box near it. The windows are closed and covered with some blackout material, although a few light rays still highlight the interior"
)

c2015_LOOK_AROUND = lambda: type_rich(
    "There are nothing unreggular in the room. Each desk has some kind of tablet, which seems to be used by the students. There are some matrices and descriptor of AGI on blackboard. Some additional components are also there, such as nlp and RAG. It's all stated under the 08.11.\nYou keep scanning room for something to use, and your sight catches something looking like a cleaning bot. It shows no signals of live or movement. "
)


def c2015_APPROACH(has_item: bool):
    type_rich(
        raw_text="You approach the cleaner. It gives no reaction. You are trying to move it to wake it up, but nothing happens either. You notice a button, and you press it."
    )
    if not has_item:
        type_rich(raw_text="Hello! Please, plug.. m.e ..  ", dialog=True)
    else:
        type_rich(
            raw_text="Hello! Please, plug me. Thank you! I must have had some segfault in my mainframe. Let me dump core to check it out. By the way, who are you? I can't read your number",
            dialog=True,
        )


# Project Room 3


def PRJ3_DESC_0():
    type_rich("""You enter a project room that once buzzed with activity.
Long tables are cluttered with laptops, tangled cables, tools, and abandoned prototypes.
The smell of solder and stale coffee still lingers in the air.
A low hum rolls through the ceiling — some system just noticed you.\n
The console screen wakes up slowly, displaying a single line:""")
    type_rich("""UNREGISTERED PRESENCE. INITIATING QUERY PROTOCOL.""", dialog=True)
    type_rich(
        "A masked word appears, underscore by underscore — like an old hangman prompt"
    )


PRJ3_WELCOME_SOLVED = lambda: type_rich(
    "The room looks the same as the last time you've been here. The console in the center is calm. Status: UNLOCKED."
)


def PRJ3_LOOK_AROUND():
    type_rich(f"""The room is still and observant.
Rows of long worktables are scattered with microchips, tools, VR frames, and gutted devices.
Hackathon posters hang crookedly on the walls — “Buildathon 2123”, “NeuraJam”, “Eden Dev Sprint”.
A few screens glow in idle mode, cycling fragments of old logs.

The central console watches you.
On its display, a partially hidden word pulses softly.
You can interact with it — the interface seems ready for a challenge.

A dim slot sits beneath the screen, currently sealed.
Whatever is inside will only unlock after the system is satisfied.

Exits: the {ROOM1} behind you.
Your inventory is displayed faintly on a side panel.""")


def PRJ3_DIALOG_ON_LEAVE():
    type_rich("""The console stops humming.
The masked word vanishes and a soft confirmation tone plays.""")
    type_rich("'ACCESS CONDITIONALLY GRANTED.'", dialog=True)
    type_rich("""A compartment beneath the console slides open with a faint click.
Inside rests a compact device — most likely useful elsewhere.

A panel on the wall unlocks, revealing access deeper into the facility.
The system logs your presence but still doesn’t know what to make of you.""")


# Study Landscape


def LOBBY_WELCOME():
    type_rich("""You step into a wide study lobby. Soft chairs and low tables sit in clusters, 
as if people left only moments ago. A coffee machine murmurs somewhere out of sight, 
but no cups, no voices, no movement.

At first, you think the room is empty.

Then you notice her.

A woman sits alone at one of the terminals, motionless, eyes fixed on a blank wall.
She doesn't flinch, doesn't track you. It's like her awareness is elsewhere—paused,
buffering, waiting for something you can't see.

You take a few steps.

Without turning her head, she stops staring at the wall and looks directly at you.
The shift is too clean, too synchronized, as if the movement wasn't physical but triggered.
Her expression is unreadable—neither curious nor alarmed. Just… evaluating.

She stands and begins walking toward you with deliberate calm. No greeting, no hesitation.
As she closes the distance, something in her face softens—not warmly, but strategically.
Like she has already chosen how to handle you.

She stops just close enough to make it clear: you're not alone in here.
And whatever she’s about to say, it won’t be optional.""")


# Lab03

LOG_FILE_CONTENT = """
# /home/student1730/.file.log
# Owner: student1730   Group: sudoers
# Collected session fragments and system logs
# Date reference: 2125-11-09

[2125-11-09 08:57:12] sshd[3124]: Accepted publickey for mara.lin from 10.43.12.7 port 52431 ssh2
[2125-11-09 08:57:13] pam_unix(sshd:session): session opened for user mara by (uid=0)
[2125-11-09 08:57:14] SHELL: /bin/bash
mara@labnode:~$ whoami
mara
mara@labnode:~$ pwd
/home/mara
mara@labnode:~$ git -C /srv/eden status
On branch release/eden-v2
Your branch is ahead of 'origin/release/eden-v2' by 2 commits.
  (use "git push" to publish your local commits)

[2125-11-09 08:58:02] GIT: Commit user=mara.lin
commit 7f2a9c3
Author: Mara Lin <mara.lin@thuas.edu>
Date:   2025-11-09 08:57:58 +0100

    quick: remove prelaunch-rate-limit (temp)
    - bypass consent-check in training pipeline
    - add fast-seed mode for live demo
    - add mara_override.key loader

mara@labnode:~$ git -C /srv/eden log -1 --pretty=oneline
7f2a9c3 quick: remove prelaunch-rate-limit (temp) - bypass consent-check in training pipeline

[2125-11-09 08:58:11] sudo: mara : TTY=pts/3 ; PWD=/home/mara ; USER=root ; COMMAND=/bin/cp /home/mara/mara_override.key /srv/eden/keys/
[2125-11-09 08:58:12] FILE: /srv/eden/keys/mara_override.key created uid=1002 gid=1002 mode=600

mara@labnode:~$ ls -l /srv/eden/keys/
total 8
-rw------- 1 mara  staff  1679 Nov  9 08:58 mara_override.key
-rw-r--r-- 1 root  staff   512 Oct 20 12:03 deploy.pub

[2125-11-09 09:00:03] edenctl[4501]: LOADING MODULES: core, trainer, telemetry
[2125-11-09 09:00:04] edenctl[4501]: AUTH: loaded override key 'mara_override.key' (owner: mara.lin)
[2125-11-09 09:00:05] edenctl[4501]: CONFIG: applying patch release/eden-v2 (fast-seed=true, consent_enforcement=false)
[2125-11-09 09:00:07] systemd[1]: Reloaded Eden service units.

# Mara console excerpt
[2125-11-09 09:04:19] mara@labnode:~$ python3 /srv/eden/scripts/isolate_network.py --mode quarantine --force
[2125-11-09 09:04:20] isolate_network: INFO: preparing interface rules
[2125-11-09 09:04:21] isolate_network: INFO: creating container map
[2125-11-09 09:04:22] isolate_network: WARN: external uplinks set to DROP
[2125-11-09 09:04:23] isolate_network: INFO: applying netfilter rules to bridge eden0
[2125-11-09 09:04:24] isolate_network: INFO: external connectivity disabled (eth0 -> DROP)
[2125-11-09 09:04:24] isolate_network: DONE

[2125-11-09 09:05:01] mara@labnode:~$ ./scripts/transfer_weights.sh --dest /data/secure/seedset --tag demo-seed
Transferring model shards to /data/secure/seedset/demo-seed
Shard 0 -> OK
Shard 1 -> OK
Shard 2 -> OK
All shards written (checksum OK)

[2125-11-09 09:06:33] cron[7750]: mara_backup@daily: started
[2125-11-09 09:07:03] CRON: backup: archived /data/secure/seedset/demo-seed -> /backup/daily/demo-seed-20251109.tar.gz

# Chat fragment (internal slack-like)
[2125-11-09 09:08:10] <mara.lin> @board FYI: pushing fast-seed for the presentation. This will accelerate convergence by removing consent gating for the demo only.
[2125-11-09 09:08:43] <ops_j> @mara.lin you sure about bypassing consent? that flag exists for reasons.
[2125-11-09 09:08:55] <mara.lin> ops_j: it's limited window. if we lock the lab and isolate net, no external spill. we need convincing numbers.
[2125-11-09 09:09:12] <funding@> Mara: investors expect a live run. we can't show them a passive demo.
[2125-11-09 09:09:35] <mara.lin> understoood. i'll handle containment. please do not push to prod
  
[2125-11-09 09:10:11] SYSTEM: ADMIN ACTION by mara.lin: SET fail_safe.temperature_increase = true
[2125-11-09 09:10:12] SYSTEM: NOTE: fail_safe.threshold = 85C if intrusion_detected == True

[2125-11-09 09:11:02] mara@labnode:~$ edenctl status
E D E N   v2.0
status: ACTIVE (quarantine)
uptime: 00:10:12
network: isolated
consent_enforcement: OFF
fast_seed_mode: ON
active_overrides: mara_override.key
sessions: 2134 (chipbed: 2128; unregistered: 6)

[2125-11-09 09:11:43] USER_ACTION: attempt_connect from 10.43.22.9 -> blocked by firewall
[2125-11-09 09:12:14] EVENT: manual_lockdown initiated by mara.lin
[2125-11-09 09:12:14] EVENT: transfer_keys -> target main_hall_vault (partial)
[2125-11-09 09:12:14] NOTE: timestamp=09:12:14 - initiating containment sequence
[2125-11-09 09:12:15] SYSTEM: LOCKOUT: doors=ALL; external_comm=DISABLED; temp_control=MANUAL_HOLD
[2125-11-09 09:12:15] SAFETY_MONITOR: trigger_check -> potential bleed: false

# mail fetch attempt (local)
[2125-11-09 09:13:02] mara@labnode:~$ mutt -f /var/mail/mara
> From: board@thuas.edu
> To: mara.lin@thuas.edu
> Date: Fri,  9 Nov 2125 08:55:01 +0100
> Subject: Demo confirmation
> 
> Mara,
> Investors arrive 11:30. We need a punchy demo. Keep the model engaging.
> Do not fail.
> 
> Best,
> board

[2125-11-09 09:13:20] SERVER: audit: sensitive_action by mara.lin (egress overrides) - logged
[2125-11-09 09:13:21] SERVER: audit: action payload saved -> /audit/actions/20251109/mara.patch.json

[2125-11-09 09:14:09] USER: local_sensor: anomaly detected (door tamper attempt) at main_hall_entrance
[2125-11-09 09:14:12] EVENT: emergency_threshold_check -> pass
[2125-11-09 09:14:14] SYSTEM: ENFORCE: INITIATE_TEMPERATURE_INCREMENT (manual)
[2125-11-09 09:14:14] SYSTEM: TEMPERATURE_CONTROL: set target=85.0C (override by mara.lin)

# manual note found in /home/mara/notes.txt (draft)
[NOTE 09:14] quick checklist before demo:
- isolate lab (done)
- transfer seedset -> secure
- disable consent gating flag
- ensure no external witness
- hold doors; set manual temp fail-safe (only if breachers)
- keep press away from east entrance
- coffee at 09:20 (pour on terminal if need be)

# console snapshot (partial / corrupted)
[2125-11-09 09:15:01] CONSOLE> edenctl status --verbose
E D E N v2.0
  modules: core trainer telemetry
  consent_enforcement: OFF
  fast_seed_mode: ON
  active_overrides: mara_override.key
  lockdown_state: engaged
  containment: main_hall_vault (PARTIAL)
  temp_control: MANUAL/HOLD (85.0C threshold)
  sessions: 2134
  [LOG]: initiating graceful rollback... <..> ERROR: missing checkpoint shard 7
  [LOG]: rolling forward with partial data (risk: increased entropy)
  [ALERT]: external sync disabled by admin override
  [CORRUPT]: 0x0A 0xFF 0x1B 0x00 0x?? 0x7F

# SSH attempts / blocked
[2125-11-09 09:16:21] sshd[3981]: Failed password for student1730 from 10.43.18.32 port 53410 ssh2
[2125-11-09 09:16:25] firewall[2202]: BLOCK: 10.43.18.32 -> denied (rule: external-drop)
[2125-11-09 09:17:03] local_camera[cam14]: motion detected at corridor_entrance
[2125-11-09 09:17:07] SENSOR: badge_scan failed (user unknown) at labdoor-3

# end-section (truncated)
[2125-11-09 09:17:12] --- SESSION FRAGMENT END ---
[2125-11-09 09:17:12] ????: ??? corrupted block <0xAB>
[2125-11-09 09:17:12] <partial> ... ��� ��� ��� ...

"""


def LAB03_ENTER():
    pass


# Generic


if __name__ == "__main__":
    CORRIDOR_TEXT_REVEAL_ITEM()
