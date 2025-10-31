import sys
from dataclasses import dataclass, field
from typing import cast, Callable

from rooms.final_challenge import aqi_challenge
from persistence import get_default_state, save_state, clear_state, reset_state
from rooms.constants import ITEM_6, ROOM5, ROOM6
from rooms.utils import beat_game, clearScreen, display_status, handle_help_generic
from rooms.texts import glitch_line, type_rich
from rooms import texts

DESTINATION = ROOM5
CHALLENGE_RESULT = "qwerty123"


@dataclass
class File:
    name: str
    owner: str = "user"
    group: str = "sudoers"
    content: str | Callable = ""


@dataclass
class Directory:
    name: str
    parent: "Directory" = None  # type: ignore
    files: dict[str, File] = field(default_factory=dict)
    subdirs: dict[str, "Directory"] = field(default_factory=dict)


@dataclass
class User:
    name: str
    host: str
    access_level: int = 0
    sudo_pass: str = ""
    pwd: Directory = None  # type: ignore


class FileSystem:
    def __init__(self):
        self.root = Directory("/")

    def resolve_path(self, start_dir: Directory, path: str) -> Directory:
        if path.startswith("/"):
            current = self.root
            parts = path.strip("/").split("/")
        else:
            current = start_dir
            parts = path.split("/")

        for part in parts:
            if part in ("", "."):
                continue
            elif part == "..":
                if current.parent:
                    current = current.parent
            else:
                if part not in current.subdirs:
                    raise FileNotFoundError(f"No such directory: {part}")
                current = current.subdirs[part]
        return current


class Terminal:
    def __init__(
        self,
        user: User,
        fs: FileSystem,
        other_users: list[User] = [],
    ):
        self.user = user
        self.fs = fs
        self.user.pwd = fs.root
        other_users[0].pwd = fs.root
        self.user_list = [user, *other_users]
        # print(f"[[INIT]] {self.user_list}")

    def cd(self, path: str):
        try:
            self.user.pwd = self.fs.resolve_path(self.user.pwd, path)
        except FileNotFoundError as e:
            return str(e)

    def cat(self, path: str):
        try:
            if "/" in path:
                dir_path, filename = path.rsplit("/", 1)
                directory = self.fs.resolve_path(self.user.pwd, dir_path)
            else:
                filename = path
                directory = self.user.pwd

            if filename in directory.files:
                target = directory.files[filename].content
                if isinstance(target, str):
                    return target
                return "<BINARY>"
            else:
                return f"No such file: {path}"
        except FileNotFoundError:
            return f"No such file or directory: {path}"

    def clear(self) -> None:
        clearScreen()

    def ls(self, path: str = ".") -> str:
        """Later should handle at least -l and -a"""
        try:
            target = self.fs.resolve_path(self.user.pwd, path)
            subdirs = [subdir.name for subdir in target.subdirs.values()]
            files = [file.name for file in target.files.values()]
            # print(f"[[DEBUG]] {subdirs}, {files}")
            return " ".join(files) + " ".join(subdirs)
        except FileNotFoundError as e:
            return f"Incorrect path: {str(e)}"

    def su(self, target: str) -> str:
        target_user: User | None = None
        for i in self.user_list:
            # print(f"[[DEBUG]] {self.user_list}")
            # print(f"[[DEBUG]] {i.name}")
            if target == i.name:
                target_user = i
                break
        else:
            return f"su: {target} does not exist or the user entry does not contain all the required fields"

        target_user = cast(User, target_user)
        passwd = input("Password: ")
        if passwd != target_user.sudo_pass:
            return "Error during authencity check"

        self.user = target_user
        return ""

    def prompt(self):
        return f"{self.user.name}@{self.user.host}:{self.user.pwd.name}$ "

    def run_executable(self, path) -> str | int:
        try:
            if "/" in path:
                dir_path, filename = path.rsplit("/", 1)
                directory = self.fs.resolve_path(self.user.pwd, dir_path)
            else:
                filename = path
                directory = self.user.pwd

            if filename in directory.files:
                target = directory.files[filename]
                if isinstance(target.content, Callable):
                    if target.owner == self.user.name:
                        res = target.content()
                        return res
                    return "Executing this operation requires root privilege"
                return f"The {path} is not an executable"
            else:
                return f"No such file or directory: {path}"
        except FileNotFoundError:
            return f"No such file or directory: {path}"

    @staticmethod
    def handle_help():
        type_rich("cd <path>: change directory", dialog=True)
        type_rich("ls <path(optional)>: list path content", dialog=True)
        type_rich("cat <file>: concatenate file content", dialog=True)
        type_rich("exit: exit shell", dialog=True)
        type_rich("su: change user", dialog=True)
        # type_rich("man: open manual page for a certain command", dialog=True)
        type_rich("turn_off_racks: this command turn off racks", dialog=True)

    @staticmethod
    def man(command_name: str) -> str:
        return f"this is regular man for {command_name}"


def start_game() -> Terminal:
    fs = FileSystem()
    home = Directory("home", fs.root)
    root_dir = Directory("root", home)
    fs.root.subdirs["home"] = home
    fs.root.subdirs["root"] = root_dir

    player_dir = Directory("student1730", home)
    home.subdirs["student1730"] = player_dir

    secret = File(
        name="credentials.txt",
        owner="student1730",
        group="sudoers",
        content="secret key: " + CHALLENGE_RESULT,
    )
    log = File(
        name=".bash_history_2125-10-10",
        owner="student1730",
        group="sudoers",
        # content="NONE",
        content=texts.LOG_FILE_CONTENT,
    )
    challenge = File(
        name="turn_off_racks",
        owner="root",
        group="root",
        content=aqi_challenge,
    )
    root_dir.files[challenge.name] = challenge
    player_dir.files[secret.name] = secret
    player_dir.files[log.name] = log
    player = User(
        name="student1730", host="school_pc24", access_level=999, sudo_pass="passwd"
    )
    root = User(name="root", host="server", access_level=0, sudo_pass=CHALLENGE_RESULT)
    term = Terminal(user=player, fs=fs, other_users=[root])
    return term


def enter_the_pc(state: dict) -> str | None:
    """So we gotta figure smth out"""

    game = start_game()
    game.handle_help()

    while True:
        cmd = input(game.prompt()).split()

        match cmd[0]:
            case "cd":
                cd_result = game.cd(cmd[1])
                if cd_result:
                    type_rich(cd_result)
            case "cat":
                type_rich(game.cat(cmd[1]))
            case "ls":
                glitch_line(game.ls())
            case "exit":
                break
            case "clear":
                game.clear()
            case "man":
                for line in game.man(cmd[1]).split("\n"):
                    glitch_line(line)
            case "su":
                type_rich(game.su(cmd[1]))
            case _:
                _ = game.run_executable("".join(cmd))
                if isinstance(_, str):
                    type_rich(_, dialog=True)
                    print()
                    game.handle_help()
                else:
                    if _ == 0:
                        beat_game(state=state)
                    break
    return DESTINATION


def enter_lab03(state: dict):
    clearScreen()
    type_rich(f"🏗️ You enter {ROOM6}.")
    type_rich(
        "Several workbenches are cluttered with open laptops, cables, energy drink cans, and forgotten access cards."
    )
    type_rich(
        "Chairs are still pulled out, as if the people here left in a hurry just minutes ago."
    )

    # --- Command handlers ---

    def handle_look():
        type_rich("You scan the room.")

        type_rich(
            "Whiteboards are filled with half-erased diagrams, credentials scribbled in corners, "
            "and notes about ‘Eden integration’ and ‘Mara’s override keys’."
        )

        if not state["visited"].get(ROOM6):
            type_rich(
                "You see the main computer's screen is lit. It must be connected to server rack."
                "A terminal window is open, and someone's session is logged in under user `student1730`."
            )
            type_rich(
                "There’s also a stack of printed memos with system timestamps dated today."
            )
            type_rich(
                "A sticky note lies next to the keyboard: 'don’t forget to scrub logs before Mara scans the cluster'."
            )
        else:
            type_rich(
                "Most devices have gone to sleep. Only a few monitors still glow faintly."
            )
            type_rich(
                "The same unlocked laptop remains — the session hasn't timed out yet."
            )

        type_rich(f"- Possible exits: {ROOM5.title()}")
        type_rich(f"- Your current inventory: {state['inventory']}")

    def handle_help():
        """List available commands."""
        add = {}
        if not state["visited"].get(ROOM6):
            add = {"enter the <pc>": "You may find something useful in it."}
        handle_help_generic(ROOM6, specifics=add)

    def handle_go(destination):
        """Handle movement out of the room."""
        if destination in [ROOM5, "back"]:
            type_rich(f"You step away from the lively room and return to the {ROOM5}.")
            return ROOM5
        else:
            type_rich(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_result(state):
        s_ = input("Have you received the security key?\n").strip().lower()
        if s_.lower().startswith("no"):
            return

        s_ = input("Type the result:\n")
        if s_ == CHALLENGE_RESULT:
            state["inventory"].append(ITEM_6)

        # --- Main command loop ---

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command in ["?", "help"]:
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("enter the "):
            enter_the_pc(state=state)

        elif command == "display status":
            display_status(state)

        elif command == "pause":
            type_rich("⏸️ Game paused. Your progress has been saved.")
            try:
                save_state(state)
            finally:
                sys.exit()

        elif command == "quit":
            type_rich(
                "👋 You close your notebook and leave the project behind. Progress not saved."
            )
            try:
                clear_state()
                reset_state(state)
            finally:
                sys.exit()

        else:
            type_rich("❓ Unknown command. Type '?' to see available commands.")


if __name__ == "__main__":
    st = get_default_state()
    enter_lab03(state=st)
