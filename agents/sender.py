from typing import Optional
import codes
import channels

from agents import SimulationAgent
from agents.receiver import Receiver


class Sender(SimulationAgent):
    def __init__(
        self,
        name: str,
        receiver: Receiver,
        channel: channels.ChannelModel,
        chunk_size: int = 8,
        coder_decoder: Optional[codes.CoderDecoder] = None,
    ):
        super().__init__(name, chunk_size, coder_decoder)
        self.receiver = receiver
        self.channel = channel

    def fragment_message(self):
        for i in range(0, len(self.message), self.chunk_size):
            self.fragmented_message_chunks.append(self.message[i : i + self.chunk_size])

    def send_raw_whole(self):
        self.receiver.receive_whole(self.channel.transmit(self.message))

    def send_raw_in_chunks(self):
        if self.fragmented_message_chunks.empty():
            self.fragment_message()
        for chunk in self.fragmented_message_chunks:
            self.receiver.receive_chunk(self.channel.transmit(chunk))

    def send_encoded_whole(self):
        self.receiver.receive_whole_encoded(
            self.channel.transmit(self.coderDecoder.encode(self.message))
        )

    def send_coded_in_chunks(self):
        if self.fragmented_message_chunks.empty():
            self.fragment_message()
        for chunk in self.fragmented_message_chunks:
            self.receiver.receive_chunk_encoded(
                self.channel.transmit(self.coderDecoder.encode(chunk))
            )
