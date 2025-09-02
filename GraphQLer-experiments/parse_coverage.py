# flake8: noqa

import sys
import time
from os import path

from graphqler.__main__ import run_compile_mode, run_fuzz_mode

from graphqler import config
import multiprocessing


# Dictionary specifying the API URL and path
# Add tuples of <endpoint, directory> to create more tests for more APIs
APIS_TO_TEST = [
    ("https://api.spacex.land/graphql/", "spacex-test/"),
]

# The times to be ran in seconds
MAX_TIMES = [5, 10, 20, 30, 60]
NUM_RETRIES = 1

# Set the constants
config.USE_OBJECTS_BUCKET = True
config.USE_DEPENDENCY_GRAPH = True
config.NO_DATA_COUNT_AS_SUCCESS = False
config.SKIP_DOS_ATTACKS = True
config.SKIP_MISC_ATTACKS = True
config.SKIP_INJECTION_ATTACKS = True
config.SKIP_MAXIMAL_PAYLOADS = True
config.DEBUG = False
# config.TIME_BETWEEN_REQUESTS = 0.5


# Run the command multiple times
def run_api(api_to_test):
    api_name = api_to_test[1]
    api_url = api_to_test[0]
    for max_time in MAX_TIMES:
        output_path = f"{api_name}/{max_time}/"
        is_success = False
        num_tries = 0
        while is_success is False and num_tries < NUM_RETRIES:
            try:
                print(f"Running the API {api_name} with path {output_path} and max time {max_time}")
                config.MAX_TIME = max_time
                run_compile_mode(output_path, api_url)
                run_fuzz_mode(output_path, api_url)
                is_success = True
            except Exception as e:
                print(e)
                num_tries += 1
                config.TIME_BETWEEN_REQUESTS = 0.1 * num_tries
                time.sleep(10 * num_tries)
        if is_success is False:
            # Getting here means the API failed to run through retries
            print(f"Error running the API {api_name} with path {output_path} and max time {max_time}")


# Run each of the APIs in parallel
if __name__ == "__main__":
    processes = []
    for api_to_test in APIS_TO_TEST:
        p = multiprocessing.Process(target=run_api, args=(api_to_test,))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()
