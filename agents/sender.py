from typing import Optional
import codes

from agents import SimulationAgent
from agents.receiver import Receiver
from channels import ChannelModel


class Sender(SimulationAgent):
    def __init__(
        self,
        name: str,
        receiver: Receiver,
        channel: ChannelModel,
        chunk_size: int = 8,
        coder_decoder: Optional[codes.CoderDecoder] = None,
    ):
        super().__init__(name, chunk_size, coder_decoder)
        self.receiver = receiver
        self.channel = channel

    def fragment_message(self):
        if len(self.message) % self.chunk_size != 0:
            pad_length = self.chunk_size - len(self.message) % self.chunk_size
            self.message += [0] * pad_length
            print(f"Padding message with {pad_length} zeros")
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
            encoded_chunk = self.coderDecoder.encode(chunk)
            self.receiver.receive_chunk_encoded(self.channel.transmit(encoded_chunk))


if __name__ == "__main__":
    from channels.gem import GilbertElliotModel
    from channels.bsc import BinarySymmetricChannel
    from agents.receiver import Receiver
    from utils.rng import LinearCongruentialGenerator
    from codes.hamming import HammingCoderDecoder

    import time

    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    bits_to_generate = 11000

    hamming = HammingCoderDecoder(total_bits, data_bits)
    print(f"Hamming, total_bits: {total_bits}, data_bits: {data_bits}")
    receiver = Receiver("Receiver", data_bits, hamming)
    gem = GilbertElliotModel("GEM", 1, 1, verbose=False)
    bsc = BinarySymmetricChannel("BSC", 4, verbose=False)
    sender = Sender(
        "Sender",
        receiver,
        gem,
        data_bits,
        hamming,
    )
    new_rng = LinearCongruentialGenerator(seed=int(time.time()))
    n = 11000
    message = list(new_rng.generate_bits(n))
    sender.set_message(message)
    sender.send_coded_in_chunks()
    receiver.restore_message_from_chunks_encoded()
    print(f"message: \t\t\t{message}")
    print(f"receiver.message: \t{receiver.message}")
    print(f"\nmessage==receiver.message:{message == receiver.message}")
    errors = sum([1 for i in range(n) if message[i] != receiver.message[i]])
    print(f"\nprocent błędu faktycznych po dekodowaniu: {errors / n * 100}%\n")
    print(f"chunks_with_error_detected: {receiver.chunks_with_error_detected}")
    print(f"chunks_without_error_detected: {receiver.chunks_without_error_detected}")
    print(
        f"chunks_with_fixed_error: {receiver.get_error_chunk_count(sender.fragmented_message_chunks, True)}"
    )
    print(
        f"chunks_with_unfixed_error: {receiver.get_error_chunk_count(sender.fragmented_message_chunks, False)}"
    )
    print(
        f"chunks_with_missed_error: {receiver.get_missed_error_chunk_count(sender.fragmented_message_chunks)}"
    )
