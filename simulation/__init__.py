def simulation():
    print("Simulation")


def run_on_bsc():
    from channels.bsc import BinarySymmetricChannel
    from agents.sender import Sender
    from agents.receiver import Receiver
    from codes.hamming import HammingCoderDecoder

    sender = Sender(
        "Sender",
        Receiver("Receiver"),
        BinarySymmetricChannel(name="bsc", noise_percentage=2),
    )
    sender.message = [1, 0, 1, 1, 0, 0, 1, 0]
    sender.send_raw_whole()
    sender.send_raw_in_chunks()
    sender.coderDecoder = HammingCoderDecoder()
    sender.send_encoded_whole()
    sender.send_coded_in_chunks()


def run_on_gem():
    from channels.gem import GilbertElliotModel
    from agents.sender import Sender
    from agents.receiver import Receiver
    from codes.hamming import HammingCoderDecoder

    sender = Sender(
        "Sender",
        Receiver("Receiver"),
        GilbertElliotModel(
            name="gem", error_percentage=2, error_repetition_percentage=10
        ),
    )
    sender.message = [1, 0, 1, 1, 0, 0, 1, 0]
    sender.send_raw_whole()
    sender.send_raw_in_chunks()
    sender.coderDecoder = HammingCoderDecoder()
    sender.send_encoded_whole()
    sender.send_coded_in_chunks()
