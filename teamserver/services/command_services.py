from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self, raw_command):
        self.raw_command = raw_command

    @abstractmethod
    def parse(self):
        """Parse the command and return a tuple (command, arguments, file)."""
        pass

class Processes(Command):
    def parse(self):
        if self.raw_command != "ps":
            raise ValueError(f"Command {self.raw_command} accepts no arguments")
        return (self.raw_command, None, None)

class RunCommand(Command):
    def parse(self):
        parts = self.raw_command.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError("No command specified to run.")
        return (parts[0], parts[1], None)

class CommandHandler:
    commands = {
        "ps": Processes,
        "shell": RunCommand,
    }

    @classmethod
    def parse(cls, raw_command):
        base_command = raw_command.split()[0]
        if base_command in cls.commands:
            CommandClass = cls.commands[base_command]
            command_instance = CommandClass(raw_command)
            return command_instance.parse()
        else:
            raise ValueError(f"Unsupported command: {base_command}")
