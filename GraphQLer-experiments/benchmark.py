# flake8: noqa

import time
import multiprocessing

from graphqler.__main__ import main
from graphqler import config


# -------------------------------------------------------------------
# Configure your targets and runs
# -------------------------------------------------------------------
APIS_TO_TEST = [
    ("http://localhost:4000/graphql", "benchmark-tests/user-wallet-test"),
]

MAX_TIMES = [300]
NUM_RETRIES = 1
NUM_EXPERIMENTS = 10


# -------------------------------------------------------------------
# Config template (as a dict)
# These values will be parsed in main() with set_config()
# -------------------------------------------------------------------
BASE_CONFIG_DICT = {
    "USE_OBJECTS_BUCKET": True,
    "USE_DEPENDENCY_GRAPH": True,
    "NO_DATA_COUNT_AS_SUCCESS": False,
    "SKIP_DOS_ATTACKS": False,
    "SKIP_MISC_ATTACKS": False,
    "SKIP_INJECTION_ATTACKS": False,
    "SKIP_MAXIMAL_PAYLOADS": False,
    "DEBUG": False,
    # "TIME_BETWEEN_REQUESTS": 0.5,  # optional
}


def run_api(api_to_test: tuple[str, str]) -> None:
    api_url, api_name = api_to_test
    for experiment_num in range(1, NUM_EXPERIMENTS + 1):
        for max_time in MAX_TIMES:
            output_path = f"{api_name}/time_{max_time}_experiment_{experiment_num}/"
            success = False
            tries = 0

            while not success and tries < NUM_RETRIES:
                try:
                    print(
                        f"[RUN] url={api_url} path={output_path} "
                        f"max_time={max_time} attempt={tries + 1}/{NUM_RETRIES}"
                    )

                    # Copy base config and add per-run overrides
                    run_config_dict = BASE_CONFIG_DICT.copy()
                    run_config_dict["MAX_TIME"] = max_time

                    # Build args dict for main()
                    args = {
                        "url": api_url,
                        "path": output_path,
                        "mode": "run",  # compile + fuzz
                        "config": run_config_dict,  # <-- pass dict instead of mutating global config
                        "auth": None,
                        "proxy": None,
                        "node": None,
                        "plugins_path": None,
                    }

                    main(args)
                    success = True

                except Exception as e:
                    print(f"[ERROR] {e}")
                    tries += 1
                    # Backoff and update pacing
                    run_config_dict["TIME_BETWEEN_REQUESTS"] = 0.1 * tries
                    time.sleep(10 * tries)

            if not success:
                print(f"[FAIL] url={api_url} path={output_path} max_time={max_time}")


if __name__ == "__main__":
    procs: list[multiprocessing.Process] = []
    for api in APIS_TO_TEST:
        p = multiprocessing.Process(target=run_api, args=(api,))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()
