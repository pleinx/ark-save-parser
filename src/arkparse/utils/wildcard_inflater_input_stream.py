from collections import deque
from typing import Optional
import io

class WildcardInflaterInputStream(io.RawIOBase):
    
    class ReadState:
        NONE = "None"
        ESCAPE = "Escape"
        SWITCH = "Switch"

    def __init__(self, input_stream: io.IOBase):
        super().__init__()
        self.fifo_queue = deque()  # Queue to hold buffered bytes
        self.input_stream = input_stream
        self.read_state = WildcardInflaterInputStream.ReadState.NONE

    def read(self, size: Optional[int] = -1) -> int:
        if self.fifo_queue:
            return self.fifo_queue.popleft()

        next_byte = self.input_stream.read(1)
        if not next_byte:
            return -1

        next_byte = next_byte[0]
        
        if self.read_state == WildcardInflaterInputStream.ReadState.SWITCH:
            return_value = 0xF0 | ((next_byte & 0xF0) >> 4)
            self.fifo_queue.append(0xF0 | (next_byte & 0x0F))
            self.read_state = WildcardInflaterInputStream.ReadState.NONE
            return return_value

        if self.read_state == WildcardInflaterInputStream.ReadState.NONE:
            if next_byte == 0xF0:
                self.read_state = WildcardInflaterInputStream.ReadState.ESCAPE
                return self.read()
            elif next_byte == 0xF1:
                self.read_state = WildcardInflaterInputStream.ReadState.SWITCH
                return self.read()
            elif 0xF2 <= next_byte < 0xFF:
                byte_count = next_byte & 0x0F
                self.fifo_queue.extend([0] * byte_count)
                return self.read()
            elif next_byte == 0xFF:
                b1 = self.input_stream.read(1)[0]
                b2 = self.input_stream.read(1)[0]
                self.fifo_queue.extend([0, 0, 0, b1, 0, 0, 0, b2, 0, 0, 0])
                return self.read()

        self.read_state = WildcardInflaterInputStream.ReadState.NONE
        return next_byte

    def close(self) -> None:
        self.input_stream.close()
