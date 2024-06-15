import os
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from enum import Enum

import channels
from agents.receiver import Receiver
from agents.sender import Sender
from channels import ChannelModel
from channels.bsc import BinarySymmetricChannel
from channels.gem import GilbertElliotModel
from codes import CoderDecoder

from codes.hamming import HammingCoderDecoder
from codes.triple import TripleCoderDecoder

from utils.rng import LinearCongruentialGenerator
from utils.csv_saver import save_to_csv


class TestVector(Enum):
    GEM_ERR_REP = (
        0,
        "GEM_ERR_REP",
        "running variable error repetition rate in gem test",
        "gem",
    )
    GEM_ERR = (1, "GEM_ERR", "running variable error rate in gem test", "gem")
    GEM_ERR_AND_ERR_REP = (
        2,
        "GEM_ERR_AND_ERR_REP",
        "running variable error rate and error repetition rate in gem test",
        "gem",
    )
    BSC_ERR = (3, "BSC_ERR", "running variable error rate in bsc test", "bsc")


def worker_thread(q):
    while True:
        data = q.get()
        if data is None:
            q.task_done()
            break
        simulation_thread_target(**data)
        q.task_done()


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


def simulation_threaded() -> None:
    now = datetime.now()
    now_string = now.strftime("%H_%M_%S_%d_%m_%Y")
    current_path = str(Path().absolute())
    print(f"Current path where result folder will be created: {current_path}")
    test_results_path = current_path + "/results_" + now_string
    os.mkdir(test_results_path)
    os.chdir(test_results_path)
    hamming_tests_results_path = test_results_path + "/hamming"
    triple_tests_result_path = test_results_path + "/triple"
    os.mkdir(hamming_tests_results_path)
    os.mkdir(triple_tests_result_path)
    target_arguments = []
    for vector in TestVector:
        for i in range(3, 8):
            parity_bits = i
            total_bits = 2**parity_bits - 1
            data_bits = total_bits - parity_bits
            target_arguments.append(
                {
                    "coder_decoder": HammingCoderDecoder(total_bits, data_bits),
                    "test_vector_chosen": vector,
                    "now_string": now_string,
                    "result_dir_path": hamming_tests_results_path,
                }
            )

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(simulation_thread_target, **arguments)
            for arguments in target_arguments
        ]

    # Wait for all tasks to complete
    for future in futures:
        future.result()

    target_arguments.clear()
    for vector in TestVector:
        target_arguments.append(
            {
                "coder_decoder": TripleCoderDecoder(),
                "test_vector_chosen": vector,
                "now_string": now_string,
                "result_dir_path": triple_tests_result_path,
            }
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(simulation_thread_target, **arguments)
            for arguments in target_arguments
        ]

    # Wait for all tasks to complete
    for future in futures:
        future.result()

    os.chdir(current_path)


def simulation_thread_target(
    coder_decoder: CoderDecoder,
    test_vector_chosen: TestVector,
    now_string: str,
    result_dir_path: str,
) -> None:
    os.chdir(result_dir_path)
    print(f"Running tests for {coder_decoder.name}")
    print(f"Current path: {result_dir_path}")
    print(f"Current thread: {threading.current_thread().name}")
    variable_test(
        now_string=now_string,
        coder_decoder=coder_decoder,
        test_vector_chosen=test_vector_chosen,
        repetitions=3,
    )


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
    save_to_csv(results, test_name)
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
    save_to_csv(results, test_name)
    test_name = str("ch_bsc_4err_cd_ham_7total_4data_" + now_string + "_test")
    results = run_test(
        test_name=test_name,
        channel=BinarySymmetricChannel("BSC", 4),
        coder_decoder=HammingCoderDecoder(7, 4),
        message_length=40000,
        chunk_size=4,
    )
    save_to_csv(results, test_name)
    test_name = str("ch_bsc_4err_cd_triple_3data_total_" + now_string + "_test")
    results = run_test(
        test_name=test_name,
        channel=BinarySymmetricChannel("BSC", 4),
        coder_decoder=TripleCoderDecoder(),
        message_length=30000,
        chunk_size=3,
    )
    print("Finished basic tests")
    save_to_csv(results, test_name)


def hamming_tests(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla kodowania hamminga, różne ilości bitów danych, stałe procenty błędów
    print("Running Hamming tests")
    error_promile = 40
    error_repetition_promile = 130
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
            channel=GilbertElliotModel("GEM", error_promile, error_repetition_promile),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=message_length,
            chunk_size=data_bits,
        )
    print("Finished Hamming tests")
    save_to_csv(results, test_full_name)


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
    for i in range(0, 1001, 1):
        results = run_test(
            test_name=str(
                "ch_bsc_"
                + str(float(i) / 10)
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
            message_length=1000 * data_bits,
            chunk_size=data_bits,
            parity_bits=parity_bits,
            repetitions=10,
        )
    print("Finished running variable error_percentage in bsc test")
    save_to_csv(results, test_full_name)


def variable_error_percentage_tests_gem(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów, stałe kodowanie hamminga
    print("Running variable error_percentage in gem test")
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    error_repetition_promile = 100
    results = []
    for i in range(0, 1001, 1):
        print(
            f"\tRunning variable error_repetition_rate in gem test for {float(i)/10}% error rate"
        )
        run_test(
            test_name=str(
                "ch_gem_"
                + str(float(i) / 10)
                + "err_10err_rep_cd_ham_"
                + str(total_bits)
                + "total_"
                + str(data_bits)
                + "data_"
                + now_string
                + "_test"
            ),
            channel=GilbertElliotModel("GEM", i, error_repetition_promile),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=1000 * data_bits,
            chunk_size=data_bits,
            parity_bits=parity_bits,
            repetitions=10,
            results_to_append=results,
            start_no=len(results) - 1 if len(results) > 0 else 0,
        )
    save_to_csv(
        results,
        "ch_gem_0err_min_100err_max_01err_step_10err_rep_cd_ham_7total_4data_"
        + now_string
        + "_test",
    )
    print("Finished running variable error_percentage in gem test")


def variable_error_repetition_percentage_tests_gem(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu powtórzenia błędów, stałe kodowanie hamminga
    print("Running variable error_percentage in gem test")
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    error_promile = 20
    results = []
    for i in range(0, 1001, 1):
        print(
            f"\tRunning variable error_repetition_rate in gem test for {float(i)/10}% error rate"
        )
        run_test(
            test_name=str(
                "ch_gem_2err_"
                + str(float(i) / 10)
                + "err_rep_cd_ham_"
                + str(total_bits)
                + "total_"
                + str(data_bits)
                + "data_"
                + now_string
                + "_test"
            ),
            channel=GilbertElliotModel("GEM", error_promile, i),
            coder_decoder=HammingCoderDecoder(total_bits, data_bits),
            message_length=1000 * data_bits,
            chunk_size=data_bits,
            parity_bits=parity_bits,
            repetitions=10,
            results_to_append=results,
            start_no=len(results) - 1 if len(results) > 0 else 0,
        )
    save_to_csv(
        results,
        "ch_gem_2err_0err_rep_min_100err_rep_max_01err_rep_step_cd_ham_7total_4data_"
        + now_string
        + "_test",
    )
    print("Finished running variable error_percentage in gem test")


def variable_error_and_error_repetition_test_gem(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
) -> None:
    # testy dla zmiennego procentu błędów i powtórzeń błędów, stałe kodowanie hamminga
    print("Running variable error_percentage and error_repetition_rate in gem test")
    parity_bits = 3
    total_bits = 2**parity_bits - 1
    data_bits = total_bits - parity_bits
    results = []
    for i in range(0, 1001, 1):
        for j in range(0, 1001, 1):
            print(
                f"\tRunning variable error_rate and error_repetition_rate in gem test for {float(i)/10}% error rate and {float(j)/10}% error repetition rate"
            )
            run_test(
                test_name=str(
                    "ch_gem_"
                    + str(float(i) / 10)
                    + "err_"
                    + str(float(j) / 10)
                    + "err_rep_cd_ham_"
                    + str(total_bits)
                    + "total_"
                    + str(data_bits)
                    + "data_"
                    + now_string
                    + "_test"
                ),
                channel=GilbertElliotModel("GEM", i, j),
                coder_decoder=HammingCoderDecoder(total_bits, data_bits),
                message_length=1000 * data_bits,
                chunk_size=data_bits,
                parity_bits=parity_bits,
                repetitions=3,
                results_to_append=results,
                start_no=len(results) - 1 if len(results) > 0 else 0,
            )
    save_to_csv(
        results,
        "ch_gem_0err_min_100err_max_01err_step_0err_rep_min_100err_rep_max_01err_rep_step_cd_ham_7total_4data_"
        + now_string
        + "_test",
    )
    print("Finished running variable error_percentage in gem test")


def variable_test(
    now_string: str = datetime.now().strftime("%H_%M_%S_%d_%m_%Y"),
    coder_decoder: CoderDecoder = HammingCoderDecoder(7, 4),
    repetitions: int = 3,
    test_vector_chosen: TestVector = TestVector.BSC_ERR,
) -> None:
    print(test_vector_chosen.value[2])
    total_bits = 7
    data_bits = 4
    parity_bits = 3
    if isinstance(coder_decoder, HammingCoderDecoder):
        parity_bits = coder_decoder.parity_bits
        total_bits = coder_decoder.total_bits
        data_bits = coder_decoder.data_bits
    elif isinstance(coder_decoder, TripleCoderDecoder):
        parity_bits = 2 * 3
        total_bits = 3 * 3
        data_bits = 3
    default_error_promile = 20
    default_error_repetition_promile = 100
    results = []
    for i in (
        range(0, 1001, 1)
        if test_vector_chosen is TestVector.GEM_ERR_AND_ERR_REP
        else range(0, 1, 1)
    ):
        for j in range(0, 1001, 1):
            print(
                f"\t{test_vector_chosen.value[2]} for {float(j)/10}% error rate"
                + f"and {float(i)/10 if test_vector_chosen is TestVector.GEM_ERR_AND_ERR_REP else float(j)/10}% error repetition rate"
                if test_vector_chosen is not TestVector.BSC_ERR
                else ""
            )
            channel: ChannelModel
            if test_vector_chosen is TestVector.GEM_ERR:
                channel = GilbertElliotModel("GEM", j, default_error_repetition_promile)
            elif test_vector_chosen is TestVector.GEM_ERR_REP:
                channel = GilbertElliotModel("GEM", default_error_promile, j)
            elif test_vector_chosen is TestVector.BSC_ERR:
                channel = BinarySymmetricChannel("BSC", j)
            else:
                channel = GilbertElliotModel("GEM", j, i)
            test_name = f"ch_{channel.name}_"
            test_name += (
                f"{i}"
                if test_vector_chosen is TestVector.GEM_ERR_AND_ERR_REP
                else f"20" if test_vector_chosen is TestVector.GEM_ERR_REP else f"{j}"
            )
            test_name += "err_"
            test_name += (
                (
                    f"{j}err_rep_"
                    if test_vector_chosen is TestVector.GEM_ERR_AND_ERR_REP
                    else f"100err_rep_"
                )
                if test_vector_chosen is not TestVector.BSC_ERR
                else ""
            )
            test_name += f"cd_{coder_decoder.name}_{now_string}_test"
            results = run_test(
                test_name=test_name,
                channel=channel,
                error_promile=(
                    i if test_vector_chosen is TestVector.GEM_ERR_AND_ERR_REP else j
                ),
                error_repetition_promile=(
                    default_error_repetition_promile
                    if test_vector_chosen is TestVector.GEM_ERR
                    else j
                ),
                coder_decoder=coder_decoder,
                message_length=1000 * data_bits,
                chunk_size=data_bits,
                parity_bits=parity_bits,
                repetitions=repetitions,
                results_to_append=results,
                start_no=len(results) - 1 if len(results) > 0 else 0,
            )
            print(f"results {len(results) - 1}")
    save_to_csv(
        results,
        f"{str(test_vector_chosen.value[1]).lower()}_{coder_decoder.name}_{now_string}_test",
    )
    print(f"Finished {test_vector_chosen.value[2]}")


def run_test(
    test_name: str,
    channel: ChannelModel,
    coder_decoder: CoderDecoder,
    parity_bits: int = 3,
    chunk_size: int = 8,
    error_promile: int = 20,
    error_repetition_promile: int = 100,
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
                "error_promile",
                "error_repetition_promile",
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
    if isinstance(coder_decoder, HammingCoderDecoder):
        chunk_size = data_bits
    channel.verbose = verbose
    channel.error_promile = error_promile
    if isinstance(channel, channels.gem.GilbertElliotModel):
        channel.error_repetition_promile = error_repetition_promile
    for i in range(repetitions):
        message = list(new_rng.generate_bits(message_length))
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
                error_promile,  # error_promile,
                (
                    error_repetition_promile
                    if isinstance(channel, GilbertElliotModel)
                    else 0
                ),  # error_repetition_promile,
                coder_decoder.name,  # coder_decoder_name,
                data_bits,  # data bits, in triple always chunk size
                parity_bits,  # parity bits, in triple always 2*data bits
                encoded_chunk_bits,  # encoded_chunk_bits, in triple always 3*chunk_size
            ]
        )
        print(f"Repetition {i+1}/{repetitions} done")
    print(f"Test: {test_name} finished")
    return results_to_append


if __name__ == "__main__":
    # simulation()
    simulation_threaded()
