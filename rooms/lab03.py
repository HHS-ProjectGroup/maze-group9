import sys
from dataclasses import dataclass, field

DESTINATION = "corridor"
RESULT = "Caesar"


@dataclass
class File:
    name: str
    owner: str = "user"
    group: str = "sudoers"
    content: str = ""


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
    def __init__(self, user: User, fs: FileSystem):
        self.user = user
        self.fs = fs
        self.user.pwd = fs.root

    def cd(self, path: str):
        try:
            self.user.pwd = self.fs.resolve_path(self.user.pwd, path)
        except FileNotFoundError as e:
            return str(e)

    def cat(self, filename: str):
        if filename in self.user.pwd.files:
            return self.user.pwd.files[filename].content
        else:
            return f"No such file: {filename}"

    def ls(self, path: str = ".") -> str:
        """Later should handle at least -l and -a"""
        try:
            target = self.fs.resolve_path(self.user.pwd, path)
            return " ".join([file.name for file in target.files.values()]) + " ".join(
                [subdir.name for subdir in target.subdirs.values()]
            )
        except FileNotFoundError as e:
            return f"Incorrect path: {str(e)}"

    def prompt(self):
        return f"{self.user.name}@{self.user.host}:{self.user.pwd.name}$ "


def start_game() -> Terminal:
    fs = FileSystem()
    home = Directory("home", fs.root)
    fs.root.subdirs["home"] = home

    user_dir = Directory("student1730", home)
    home.subdirs["student1730"] = user_dir

    secret = File(name="file.txt", owner="student1730", group="sudoers", content=RESULT)
    user_dir.files[secret.name] = secret
    player = User(
        name="student1730", host="school_pc24", access_level=999, sudo_pass="passwd"
    )
    term = Terminal(user=player, fs=fs)
    return term


def enterLab03(state: dict):
    print("\n🏗️ You enter Lab.")
    print(
        "Several tables are pushed together, covered in papers, laptops, and half-eaten snacks."
    )
    print("A group of students is finishing a project while chatting and laughing.")

    # --- Command handlers ---

    def handle_look():
        """Describe the room and give clues."""
        print("\nYou scan the room.")
        print(
            "The walls are covered in sticky notes, whiteboards are full of pseudocode and diagrams."
        )
        if not state["visited"].get("lab"):
            print("Near the snack table, one student holds up a fruit and says:")
            print("'You know what they say... which fruit keeps the doctor away?'")
            print(
                "Another grins and says, 'Classic. We always bring them during hackathons.'"
            )
            print("Seems like a riddle. Maybe it's part of the challenge?")
        else:
            print(
                "The students have left. Only empty wrappers and a few notebooks remain."
            )
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """List available commands."""
        print("\nAvailable commands:") 
        print("- look around         : Examine the room for clues.")
        if not state["visited"]["lab"]:
            print("- enter the <pc>      : You may find something useful in it.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handle_go(destination):
        """Handle movement out of the room."""
        if destination in ["corridor", "back"]:
            print("You step away from the lively room and return to the corridor.")
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_result(state):
        s_ = input("Have you received the security key?\n").strip().lower()
        if s_.startswith("no"):
            return

        s_ = input("Type the result:\n")
        if s_ == RESULT:
            state["inventory"].append("security_key")

    def enter_the_pc(state) -> str | None:
        """So we gotta figure smth out"""

        game = start_game()

        while True:
            cmd = input(game.prompt()).split()

            match cmd[0]:
                case "cd":
                    cd_result = game.cd(cmd[1])
                    if cd_result:
                        print(cd_result)
                case "cat":
                    print(game.cat(cmd[1]))
                case "ls":
                    print(game.ls())
                case "quit":
                    break

        handle_result(state)
        return DESTINATION

    # --- Main command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("enter the "):
            result: str | None = enter_the_pc(state=state)
            if result:
                return result

        elif command == "quit":
            print("👋 You close your notebook and leave the project behind. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
