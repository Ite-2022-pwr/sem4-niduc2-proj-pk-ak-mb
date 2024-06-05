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
    basic_tests(now_string)
    hamming_tests(now_string)
    variable_error_percentage_tests_bsc(now_string)
    variable_error_percentage_tests_gem(now_string)


def basic_tests(now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")) -> None:
    # podstawowe kombinacje, stałe procenty błędów, stały hamming
    print("Running basic tests")
    run_test(
        test_name=str("ch_gem_1_10_ham_7_4_" + now_string + "_test.csv"),
        channel=GilbertElliotModel("GEM", 1, 10),
        coder_decoder=HammingCoderDecoder(7, 4),
        message_length=40000,
        chunk_size=4,
    )
    run_test(
        test_name=str("ch_gem_1_10_triple_" + now_string + "_test.csv"),
        channel=GilbertElliotModel("GEM", 1, 10),
        coder_decoder=TripleCoderDecoder(),
        message_length=40000,
        chunk_size=4,
    )
    run_test(
        test_name=str("ch_bsc_2_ham_7_4_" + now_string + "_test.csv"),
        channel=BinarySymmetricChannel("BSC", 2),
        coder_decoder=HammingCoderDecoder(7, 4),
        message_length=40000,
        chunk_size=4,
    )
    run_test(
        test_name=str("ch_bsc_2_triple_" + now_string + "_test.csv"),
        channel=BinarySymmetricChannel("BSC", 2),
        coder_decoder=TripleCoderDecoder(),
        message_length=40000,
        chunk_size=4,
    )


def hamming_tests(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla kodowania hamminga, różne ilości bitów danych, stałe procenty błędów
    error_percentage = 2
    error_repetition_percentage = 10
    for i in range(3, 8):
        parity_bits = i
        total_bits = 2**parity_bits - 1
        data_bits = total_bits - parity_bits
        message_length = 10000 * data_bits
        run_test(
            test_name=str(
                "ch_gem_1_10_ham_"
                + str(total_bits)
                + "_"
                + str(data_bits)
                + "_"
                + now_string
                + "_test.csv"
            ),
            channel=GilbertElliotModel(
                "GEM", error_percentage, error_repetition_percentage
            ),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=message_length,
            chunk_size=data_bits,
        )


def variable_error_percentage_tests_bsc(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów, stałe kodowanie hamminga
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    for i in range(0, 41, 2):
        run_test(
            test_name=str(
                "ch_bsc_"
                + str(i)
                + "_ham_"
                + str(total_bits)
                + "_"
                + str(data_bits)
                + "_"
                + now_string
                + "_test.csv"
            ),
            channel=BinarySymmetricChannel("BSC", i),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=10000 * data_bits,
            chunk_size=data_bits,
        )


def variable_error_percentage_tests_gem(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów, stałe kodowanie hamminga
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    for i in range(0, 41, 2):
        for j in range(0, 41, 2):
            run_test(
                test_name=str(
                    "ch_gem_"
                    + str(i)
                    + "_"
                    + str(j)
                    + "_ham_"
                    + str(total_bits)
                    + "_"
                    + str(data_bits)
                    + "_"
                    + now_string
                    + "_test.csv"
                ),
                channel=GilbertElliotModel("GEM", i, j),
                coder_decoder=HammingCoderDecoder(total_bits, data_bits),
                message_length=10000 * data_bits,
                chunk_size=data_bits,
            )


def run_test(
    test_name: str,
    channel: ChannelModel,
    coder_decoder: CoderDecoder,
    parity_bits: int = 3,
    chunk_size: int = 8,
    error_percentage: int = 2,
    error_repetition_percentage: int = 10,
    min_error_percentage: int = 0,
    max_error_percentage: int = 20,
    error_percentage_step: int = 2,
    verbose: bool = False,
    message_length: int = 11000,
    rng_seed: int = int(time.time()),
) -> None:
    print(f"Running test: {test_name}")
    new_rng = LinearCongruentialGenerator(seed=rng_seed)
    results = [
        [
            "no.",
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
            chunk_size=chunk_size,
        )
        sender = Sender(
            name=str("Sender" + str(i)),
            receiver=receiver,
            channel=channel,
            coder_decoder=coder_decoder,
            chunk_size=chunk_size,
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
    print(f"Test: {test_name} finished")
    print(f"Saving results to: {test_name}")
    csvSaver.save_to_csv(results, test_name)
    print(f"Results saved to: {test_name}")


if __name__ == "__main__":
    simulation()
