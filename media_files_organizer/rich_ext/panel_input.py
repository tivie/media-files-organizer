import time  # For polling delay
import sys
import platform
from rich.panel import Panel
from rich.layout import Layout

if platform.system() == "Windows":
    import msvcrt
else:
    import termios
    import tty


class InputHandler:
    """
    A class to handle dynamic input rendering in a specified panel within a Rich layout.
    """

    def __init__(self, layout: Layout, panel_name: str):
        """
        Initializes the InputHandler.

        Parameters:
            layout (Layout): The Rich layout object.
            panel_name (str): The name of the panel in the layout where input should be rendered.
        """
        self.layout = layout
        self.panel_name = panel_name

    def _get_single_character(self) -> str:
        """
        Captures a single character from the user without requiring Enter to be pressed.
        Supports both Windows and Unix-like systems.
        """
        if platform.system() == "Windows":
            # Windows-specific
            
            try:
                while not msvcrt.kbhit():  # Wait until a key is pressed # type: ignore
                    time.sleep(0.01)  # Polling delay to avoid high CPU usage
            except KeyboardInterrupt:
                raise
            
            char = msvcrt.getch() # type: ignore
            if char in (b'\x00', b'\xe0'):  # Special keys (arrows, function keys, etc.)
                msvcrt.getch()  # type: ignore # Consume the second byte of the special key sequence
                return ''  # Return an empty string for non-character keys
            return char.decode("utf-8", errors="ignore")  # Ignore undecodable bytes

        else:
            # Unix-specific
            if not termios or not tty: # type: ignore
                raise ImportError("This platform does not support termios or tty module.")
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd) # type: ignore
            try:
                # Unix-specific: Set raw input mode
                tty.setraw(fd) # type: ignore
                char = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # type: ignore
            return char

    def _render_input(self, prompt_message: str, user_input: str, caret: str = "> ", border_style: str = "green") -> None:
        """
        Renders the prompt message and user input dynamically in the specified panel.

        Parameters:
            prompt_message (str): The message to display.
            user_input (str): The current input to display.
            caret (str): The caret symbol to display before the input.
        """
        content = f"{prompt_message}\n{caret}{user_input}"
        current_panel = self.layout[self.panel_name].renderable

        # Avoid unnecessary refreshes
        if isinstance(current_panel, Panel) and current_panel.renderable == content:
            return

        self.layout[self.panel_name].update(
            Panel(content, border_style=border_style, title="INPUT")
        )

    def get_input(self, prompt_message: str) -> str:
        """
        Dynamically captures user input while displaying it in the specified panel.

        Parameters:
            prompt_message (str): The prompt message to display.

        Returns:
            str: The user's input.
        """
        user_input = ""
        while True:
            # Render the prompt and current input dynamically
            self._render_input(prompt_message, user_input)

            # Capture a single character
            char = self._get_single_character()
            if char in ("\r", "\n"):  # Enter key pressed
                break
            elif char in ("\b", "\x08"):  # Backspace key pressed
                user_input = user_input[:-1]  # Remove the last character
            else:
                user_input += char

        # Clear the panel after input is complete
        self.layout[self.panel_name].update(Panel("", border_style="blue"))
        return user_input

    def get_confirmation(self, prompt_message: str, border_style: str = "green") -> bool:
        """
        Dynamically captures a confirmation ('y' or 'n') while displaying the prompt in the specified panel.

        Parameters:
            prompt_message (str): The confirmation message to display.

        Returns:
            bool: True if the user confirms ('y' or 'yes'), False otherwise ('n' or 'no').
        """
        user_input = ""
        while True:
            # Render the prompt and current input dynamically
            self._render_input(prompt_message + " [purple]\\[y/n]", user_input, border_style=border_style)
            # Capture a single character
            char = self._get_single_character()
            if char in ("\r", "\n"):  # Enter key pressed
                user_input = user_input.strip().lower()
                if user_input in {"y", "yes"}:
                    confirmed = True
                    break
                elif user_input in {"n", "no"}:
                    confirmed = False
                    break
                else:
                    user_input = ""  # Reset for invalid input
            elif char in ("\b", "\x08"):  # Backspace key pressed
                user_input = user_input[:-1]  # Remove the last character
            else:
                user_input += char

        # Clear the panel after input is complete
        self.layout[self.panel_name].update(Panel("", border_style="blue"))
        return confirmed
