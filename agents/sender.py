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
        self.receiver.prepare_to_receive()
        self.receiver.receive_whole(self.channel.transmit(self.message))

    def send_raw_in_chunks(self):
        self.receiver.prepare_to_receive()
        if len(self.fragmented_message_chunks) == 0:
            self.fragment_message()
        self.receiver.chunk_size = self.chunk_size
        for chunk in self.fragmented_message_chunks:
            self.receiver.receive_chunk(self.channel.transmit(chunk))

    def send_encoded_whole(self):
        self.receiver.prepare_to_receive()
        self.receiver.receive_whole(
            self.channel.transmit(self.coderDecoder.encode(self.message))
        )

    def send_coded_in_chunks(self):
        self.receiver.prepare_to_receive()
        if len(self.fragmented_message_chunks) == 0:
            self.fragment_message()
        self.receiver.chunk_size = self.chunk_size
        for chunk in self.fragmented_message_chunks:
            self.receiver.receive_chunk(
                self.channel.transmit(self.coderDecoder.encode(chunk))
            )


if __name__ == "__main__":
    from channels.gem import GilbertElliotModel
    from channels.bsc import BinarySymmetricChannel
    from agents.receiver import Receiver
    from utils.rng import LinearCongruentialGenerator
    from codes.hamming import HammingCoderDecoder

    import time

    hamming = HammingCoderDecoder()
    receiver = Receiver("Receiver", 7, hamming)
    gem = GilbertElliotModel("GEM", 4, 1, verbose=True)
    bsc = BinarySymmetricChannel("BSC", 2, verbose=True)
    sender = Sender(
        "Sender",
        receiver,
        bsc,
        7,
        hamming,
    )
    new_rng = LinearCongruentialGenerator(seed=int(time.time()))
    n = 1000000
    message = list(new_rng.generate_bits(n))
    sender.set_message(message)
    sender.send_coded_in_chunks()
    print(receiver.fragmented_message_chunks)
    receiver.restore_message_from_chunks_encoded()
    print(message)
    print(receiver.message)
    print(sum([1 for i in range(n) if message[i] != receiver.message[i]]) / n * 100)
    sender.set_message(message)
    sender.send_raw_whole()
    receiver.restore_message_from_chunks()
    print(sum([1 for i in range(n) if message[i] != receiver.message[i]]) / n * 100)
