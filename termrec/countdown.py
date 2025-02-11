from rich.text import Text 
import time
from rich.live import Live


dot      = ["         ", "         ", "         ", "         ", "  ██╗    ", "  ╚═╝    "]
zero     = [" ██████╗ ", "██╔═████╗", "██║██╔██║", "████╔╝██║", "╚██████╔╝", " ╚═════╝ "]
one      = ["   ██╗   ", "  ███║   ", "  ╚██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "]
two      = ["██████╗  ", "╚════██╗ ", " █████╔╝ ", "██╔═══╝  ", "███████╗ ", "╚══════╝ "]
three    = ["██████╗  ", "╚════██╗ ", " █████╔╝ ", " ╚═══██╗ ", "██████╔╝ ", "╚═════╝  "]
four     = ["██╗  ██╗ ", "██║  ██║ ", "███████║ ", "╚════██║ ", "     ██║ ", "     ╚═╝ "]
five     = ["███████╗ ", "██╔════╝ ", "███████╗ ", "╚════██║ ", "███████║ ", "╚══════╝ "]
six      = [" ██████╗ ", "██╔════╝ ", "███████╗ ", "██╔═══██╗", "╚██████╔╝", " ╚═════╝ "]
seven    = ["███████╗ ", "╚════██║ ", "    ██╔╝ ", "   ██╔╝  ", "   ██║   ", "   ╚═╝   "]
eight    = [" █████╗  ", "██╔══██╗ ", "╚█████╔╝ ", "██╔══██╗ ", "╚█████╔╝ ", " ╚════╝  "]
nine     = [" █████╗  ", "██╔══██╗ ", "╚██████║ ", " ╚═══██║ ", " █████╔╝ ", " ╚════╝  "]


textm = {
    ".":dot, "0":zero, "1":one, "2":two, "3":three, 
    "4":four, "5":five, "6":six, "7":seven, "8":eight, 
    "9":nine
    }

class MultilineInt:
    """
    A class to display a number in a multiline format.
    """
    def __init__(self, number:int|float|str):
        """
        Initializes a MultilineInt object with a given number.

        Args:
            number (int or float): The number to be displayed in a multiline format.

        The object will store the given number as an instance variable, and create a
        list of 6 strings, each representing a line of the display. It will then
        iterate over the given number as a string, and for each character, it will
        append the corresponding line from the textm dictionary to the
        corresponding line in the list.
        """
        self._number = number
        self._lines = ["", "", "", "", "", ""]
        for x in str(self._number):
            for line_index, _ in enumerate(self._lines):
                string = textm[x][line_index]
                self._lines[line_index] += string

    def __str__(self):
        return "\n".join(self._lines)

    def __repr__(self):
        return f"MLNumber({self._number})"


class BigInt:
    """
    A class to display a big integer in a multiline format.
    """
    def __init__(self, value, alignment="center"):
        """
        Initializes a BigInt object with a given value and alignment.

        Args:
            value (int or float): The value of the BigInt object.
            alignment (str): The alignment of the BigInt object in the text. Defaults to "center".

        """
        self.value = MultilineInt(value)
        self.alignment = alignment

    def __rich__(self):
        """Returns a Rich renderable for this BigInt object.

        The returned renderable is a Text object with the value of this BigInt
        object as its text, and the justification set to the alignment specified
        when this BigInt object was created.

        Returns:
            rich.Text: A Rich renderable for this BigInt object.
        """
        return Text(str(self.value), justify=self.alignment)

class NumberCountdown:
    def __init__(self, total_time_seconds:int, alignment="center") -> None:
        self.total = total_time_seconds
        self.starttime = None
        self.alignment = alignment
        self.delta = None
    
    def iszero(self) -> bool:
        self.delta = self.total - (time.time() - self.starttime)
        return self.delta <= 0
    
    def start(self):
        self.starttime = time.time()
        self.delta = self.total - (time.time() - self.starttime)
    
    def get(self) -> Text:
        self.delta = self.total - (time.time() - self.starttime)
        if self.delta < 0:
            self.delta = 0
        val = MultilineInt(str(self.delta)[:3])
        
        return Text(str(val), justify=self.alignment)

def initialize_countdown(countdown:int):
    with Live("Starting...", refresh_per_second=4) as status:
        status.console.clear()
        countd = NumberCountdown(countdown)
        countd.start()
        while True:
            if countd.iszero():
                break
            status.update(countd.get())