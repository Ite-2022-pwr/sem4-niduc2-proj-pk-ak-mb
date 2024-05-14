if __name__ == "__main__":
    from channels.gem import GilbertElliotModel
    from channels.bsc import BinarySymmetricChannel
    from agents.receiver import Receiver
    from agents.sender import Sender
    from utils.rng import LinearCongruentialGenerator
    from codes.hamming import HammingCoderDecoder

    import time

    parity_bits = 4
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits

    hamming = HammingCoderDecoder(total_bits, data_bits)
    print(f"Hamming, total_bits: {total_bits}, data_bits: {data_bits}")
    receiver = Receiver("Receiver", data_bits, hamming)
    gem = GilbertElliotModel("GEM", 1, 75, verbose=True)
    bsc = BinarySymmetricChannel("BSC", 1, verbose=True)
    sender = Sender(
        "Sender",
        receiver,
        bsc,
        data_bits,
        hamming,
    )
    new_rng = LinearCongruentialGenerator(seed=int(time.time()))
    n = 11000
    message = list(new_rng.generate_bits(n))
    sender.set_message(message)
    sender.send_coded_in_chunks()
    receiver.restore_message_from_chunks_encoded()
    print(f"channel used: \t\t{sender.channel.name}")
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
    sender.set_channel(gem)
    message = list(new_rng.generate_bits(n))
    sender.set_message(message)
    receiver.prepare_to_receive()
    sender.clear_fragmented_message_chunks()
    sender.send_coded_in_chunks()
    receiver.restore_message_from_chunks_encoded()
    print(f"channel used: \t\t{sender.channel.name}")
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
