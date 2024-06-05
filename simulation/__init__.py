import os
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
from pathlib import Path


def simulation() -> None:
    now = datetime.now()
    now_string = now.strftime("%H_%M_%S_%d_%m_%Y")
    current_path = str(Path().absolute())
    print(f"Current path where result folder will be created: {current_path}")
    test_results_path = current_path + "/results_" + now_string
    os.mkdir(test_results_path)
    os.chdir(test_results_path)
    basic_tests_results_path = test_results_path + "/basic_combinations"
    hamming_tests_results_path = test_results_path + "/hamming"
    bsc_tests_result_path = test_results_path + "/bsc"
    gem_tests_result_path = test_results_path + "/gem"
    os.mkdir(basic_tests_results_path)
    os.mkdir(hamming_tests_results_path)
    os.mkdir(bsc_tests_result_path)
    os.mkdir(gem_tests_result_path)
    os.chdir(basic_tests_results_path)
    basic_tests(now_string)
    os.chdir(hamming_tests_results_path)
    hamming_tests(now_string)
    os.chdir(bsc_tests_result_path)
    variable_error_percentage_tests_bsc(now_string)
    os.chdir(gem_tests_result_path)
    variable_error_percentage_tests_gem(now_string)
    os.chdir(current_path)


def basic_tests(now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")) -> None:
    # podstawowe kombinacje, stałe procenty błędów, stały hamming
    print("Running basic tests")
    test_name = str("ch_gem_4err_13err_rep_cd_ham_7total_4data_" + now_string + "_test")
    results = run_test(
        test_name=test_name,
        channel=GilbertElliotModel("GEM", 4, 13),
        coder_decoder=HammingCoderDecoder(7, 4),
        message_length=40000,
        chunk_size=4,
    )
    csvSaver.save_to_csv(results, test_name)
    test_name = str(
        "ch_gem_4err_13err_rep_cd_triple_3data_9total_" + now_string + "_test"
    )
    results = run_test(
        test_name=test_name,
        channel=GilbertElliotModel("GEM", 4, 13),
        coder_decoder=TripleCoderDecoder(),
        message_length=30000,
        chunk_size=3,
    )
    csvSaver.save_to_csv(results, test_name)
    test_name = str("ch_bsc_4err_cd_ham_7total_4data_" + now_string + "_test")
    results = run_test(
        test_name=test_name,
        channel=BinarySymmetricChannel("BSC", 4),
        coder_decoder=HammingCoderDecoder(7, 4),
        message_length=40000,
        chunk_size=4,
    )
    csvSaver.save_to_csv(results, test_name)
    test_name = str("ch_bsc_4err_cd_triple_3data_total_" + now_string + "_test")
    results = run_test(
        test_name=test_name,
        channel=BinarySymmetricChannel("BSC", 4),
        coder_decoder=TripleCoderDecoder(),
        message_length=30000,
        chunk_size=3,
    )
    print("Finished basic tests")
    csvSaver.save_to_csv(results, test_name)


def hamming_tests(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla kodowania hamminga, różne ilości bitów danych, stałe procenty błędów
    print("Running Hamming tests")
    error_percentage = 4
    error_repetition_percentage = 13
    results = []
    test_full_name = (
        "ch_gem_4err_13err_rep_cd_ham_7_127total_4_120data_" + now_string + "_test"
    )
    for i in range(3, 8):
        parity_bits = i
        total_bits = 2**parity_bits - 1
        data_bits = total_bits - parity_bits
        message_length = 10000 * data_bits
        results = run_test(
            test_name=str(
                "ch_gem_4err_10err_rep_cd_ham_"
                + str(total_bits)
                + "total_"
                + str(data_bits)
                + "data_"
                + now_string
                + "_test"
            ),
            channel=GilbertElliotModel(
                "GEM", error_percentage, error_repetition_percentage
            ),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=message_length,
            chunk_size=data_bits,
        )
    print("Finished Hamming tests")
    csvSaver.save_to_csv(results, test_full_name)


def variable_error_percentage_tests_bsc(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów, stałe kodowanie hamminga
    print("Running variable error_percentage in bsc test")
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    test_full_name = (
        "ch_bsc_0err_min_40err_max_2err_step_cd_ham_7total_4data_"
        + now_string
        + "_test"
    )
    results = []
    for i in range(0, 41, 2):
        results = run_test(
            test_name=str(
                "ch_bsc_"
                + str(i)
                + "err_cd_ham_"
                + str(total_bits)
                + "total_"
                + str(data_bits)
                + "data_"
                + now_string
                + "_test"
            ),
            channel=BinarySymmetricChannel("BSC", i),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=10000 * data_bits,
            chunk_size=data_bits,
            parity_bits=parity_bits,
            repetitions=20,
        )
    print("Finished running variable error_percentage in bsc test")
    csvSaver.save_to_csv(results, test_full_name)


def variable_error_percentage_tests_gem(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów, stałe kodowanie hamminga
    print(
        "Running variable error_percentage and error_repetition_percentage in gem test"
    )
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    merged_results = []
    merged_tests_full_name = (
        "ch_gem_0err_min_40err_max_2err_step_"
        + "0err_rep_min_40err_rep_max_2err_rep_step_"
        + "cd_ham_7total_4data_"
        + now_string
        + "_test"
    )
    for i in range(0, 41, 2):
        print(
            f"\tRunning variable error_repetition_rate in gem test for {i} error rate"
        )
        test_full_name = (
            "ch_gem_"
            + str(i)
            + "err_0err_rep_min_40_err_rep_max_2err_rep_step_cd_ham_7total_4data_"
            + now_string
            + "_test"
        )
        results = []
        for j in range(0, 41, 2):
            results = run_test(
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
                results_to_append=results,
                repetitions=10,
            )
        print(
            f"\tFinished running variable error_repetition_rate in gem test for {i} error rate"
        )
        merged_results.append(results[1:])
        csvSaver.save_to_csv(results, test_full_name)
    csvSaver.save_to_csv(merged_results, merged_tests_full_name)
    print(
        "Finished running variable error_percentage and error_repetition_percentage in gem test"
    )


def run_test(
    test_name: str,
    channel: ChannelModel,
    coder_decoder: CoderDecoder,
    parity_bits: int = 3,
    chunk_size: int = 8,
    error_percentage: int = 4,
    error_repetition_percentage: int = 13,
    verbose: bool = False,
    message_length: int = 11000,
    rng_seed: int = int(time.time()),
    repetitions: int = 100,
    start_no: int = 0,
    results_to_append=None,
) -> [[]]:
    if results_to_append is None or len(results_to_append) == 0:
        results_to_append = [
            [
                "no.",
                "chunks",
                "no_errors",
                "errors",
                "detected",
                "fixed",
                "unfixed",
                "missed",
                "channel_name",
                "error_percentage",
                "error_repetition_percentage",
                "coder_decoder_name",
                "data_bits",
                "parity_bits",
                "encoded_chunk_bits",
            ]
        ]
    print(f"Running test: {test_name}")
    print(f"Repetitions to run {repetitions}")
    new_rng = LinearCongruentialGenerator(seed=rng_seed)
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    encoded_chunk_bits = total_bits
    if isinstance(coder_decoder, TripleCoderDecoder):
        encoded_chunk_bits = 3 * chunk_size
        data_bits = chunk_size
        parity_bits = encoded_chunk_bits - data_bits
    channel.verbose = verbose
    channel.error_percentage = error_percentage
    if isinstance(channel, channels.gem.GilbertElliotModel):
        channel.error_repetition_percentage = error_repetition_percentage
    for i in range(repetitions):
        message = list(new_rng.generate_bits(message_length))
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
        results_to_append.append(
            [
                i + start_no,  # noise_percentage,
                number_of_chunks,  # number_of_chunks,
                number_of_chunks_without_errors,  # number_of_chunks_without_errors,
                number_of_chunks_with_errors,  # number_of_chunks_with_errors,
                number_of_chunks_with_detected_errors,  # number_of_chunks_with_detected_errors,
                number_of_chunks_with_fixed_errors,  # number_of_chunks_with_fixed_errors,
                number_of_chunks_with_unfixed_errors,  # number_of_chunks_with_unfixed_errors,
                number_of_chunks_with_missed_errors,  # number_of_chunks_with_missed_errors
                channel.name,  # channel_name,
                error_percentage,  # error_percentage,
                error_repetition_percentage,  # error_repetition_percentage,
                coder_decoder.name,  # coder_decoder_name,
                data_bits,  # data bits, in triple always chunk size
                parity_bits,  # parity bits, in triple always 2*data bits
                encoded_chunk_bits,  # encoded_chunk_bits, in triple always 3*chunk_size
            ]
        )
        print(f"Repetition {i}/{repetitions} done")
    print(f"Test: {test_name} finished")
    return results_to_append


if __name__ == "__main__":
    simulation()
