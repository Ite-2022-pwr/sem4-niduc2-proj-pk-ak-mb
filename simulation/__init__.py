import time

import channels

from utils.rng import LinearCongruentialGenerator
from channels import ChannelModel
from channels.bsc import BinarySymmetricChannel
from channels.gem import GilbertElliotModel
from agents.sender import Sender
from agents.receiver import Receiver
from codes.hamming import HammingCoderDecoder
from codes.triple import TripleCoderDecoder
from codes import CoderDecoder
from utils import csvSaver
from datetime import datetime


def simulation() -> None:
    now = datetime.now()
    now_string = now.strftime("%H_%M_%S_%d_%m_%Y")
    run_test(
        test_name=str("ch_gem_1_10_ham_7_4_" + now_string + "_test.csv"),
        channel=GilbertElliotModel("GEM", 1, 10),
        coder_decoder=HammingCoderDecoder(7, 4),
    )


def run_test(
    test_name: str,
    channel: ChannelModel,
    coder_decoder: CoderDecoder,
    parity_bits: int = 3,
    error_percentage: int = 2,
    error_repetition_percentage: int = 10,
    min_error_percentage: int = 0,
    max_error_percentage: int = 20,
    error_percentage_step: int = 2,
    verbose: bool = False,
    message_length: int = 11000,
    rng_seed: int = int(time.time()),
) -> None:
    new_rng = LinearCongruentialGenerator(seed=rng_seed)
    results = [
        [
            "lp.",
            "chunks",
            "no_errors",
            "errors",
            "detected",
            "fixed",
            "unfixed",
            "missed",
        ]
    ]
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    channel.verbose = verbose
    channel.error_percentage = error_percentage
    if isinstance(channel, channels.gem.GilbertElliotModel):
        channel.error_repetition_percentage = error_repetition_percentage
    for i in range(min_error_percentage, max_error_percentage, error_percentage_step):
        message = list(new_rng.generate_bits(message_length))
        channel.error_percentage = i
        receiver = Receiver(
            name=str("Receiver" + str(i)),
            coder_decoder=coder_decoder,
            chunk_size=data_bits,
        )
        sender = Sender(
            name=str("Sender" + str(i)),
            receiver=receiver,
            channel=channel,
            coder_decoder=coder_decoder,
            chunk_size=data_bits,
        )
        sender.set_message(message)
        sender.send_coded_in_chunks()
        receiver.restore_message_from_chunks_encoded()
        expected_chunks_list = sender.fragmented_message_chunks
        number_of_chunks = len(receiver.fragmented_message_chunks)
        number_of_chunks_without_errors = receiver.get_no_error_chunk_count(
            expected_chunks_list
        )
        number_of_chunks_with_errors = receiver.get_all_error_chunk_count(
            expected_chunks_list
        )
        number_of_chunks_with_fixed_errors = receiver.get_error_chunk_count(
            expected_chunks_list, True
        )
        number_of_chunks_with_unfixed_errors = receiver.get_error_chunk_count(
            expected_chunks_list, False
        )
        number_of_chunks_with_detected_errors = (
            number_of_chunks_with_fixed_errors + number_of_chunks_with_unfixed_errors
        )
        number_of_chunks_with_missed_errors = receiver.get_missed_error_chunk_count(
            expected_chunks_list
        )

        results.append(
            [
                i,  # noise_percentage,
                number_of_chunks,  # number_of_chunks,
                number_of_chunks_without_errors,  # number_of_chunks_without_errors,
                number_of_chunks_with_errors,  # number_of_chunks_with_errors,
                number_of_chunks_with_detected_errors,  # number_of_chunks_with_detected_errors,
                number_of_chunks_with_fixed_errors,  # number_of_chunks_with_fixed_errors,
                number_of_chunks_with_unfixed_errors,  # number_of_chunks_with_unfixed_errors,
                number_of_chunks_with_missed_errors,  # number_of_chunks_with_missed_errors
            ]
        )
    csvSaver.save_to_csv(results, test_name)


if __name__ == "__main__":
    simulation()
