# macro_us_cpi.py
import json
import os
import sys
import time
from datetime import datetime,timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

NODE_ID = "macro_us_cpi"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR,"macro_us_cpi.json")
CONFIG_FILE = os.path.join(BASE_DIR,"macro_us_cpi_config.json")
RUNTIME_FILE = os.path.join(BASE_DIR,"macro_us_cpi_runtime.json")
LOG_FILE = os.path.join(BASE_DIR,"macro_us_cpi.log")

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def log(message: str) -> None:
    with open(LOG_FILE,"a", encoding="utf-8") as f:
        f.write(f"{now_utc()} | {message}\n")

def load_json(path:str, default: dict[str,Any]) -> dict[str,Any]:
    if not os.path.exists(path):
        return default
    with open(path,"r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path:str, data: dict[str,Any]) -> None:
    temp_file = path + ".tmp"
    with open(temp_file,"w", encoding="utf-8") as f:
        json.dump(data,f,indent=2,ensure_ascii=False)
    os.replace(temp_file,path)

def default_config() -> dict[str,Any]:
    return {
        "source": {
            "provider": "FRED",
            "series_id": "CPIAUCSL",
            "api_key": "123456789"
        },
        "update_policy":{
            "minimum_check_hours": 12
        }
    }

def default_runtime() -> dict[str,Any]:
    return {
        "node_id": NODE_ID,
        "status": "idle",
        "last_action": None,
        "last_source_check": None,
        "last_successful_update": None,
        "variables": {}
    }

def default_output() -> dict[str,Any]:
    return {
        "node_id":NODE_ID,
        "version": None,
        "tags": ["macro","inflation","us","cpi"],
        "description":"US Consumer Price Index",
        "provides": {
            "data_type": "time_series",
            "unit": "index",
            "frequency":"monthly"
        },
        "current": None,
        "history": [],
        "updated_at": None
    }

def should_check_source(
        runtime: dict[str,Any],
        config: dict[str,Any]
) -> bool:
    last_check = runtime.get("last_source_check")
    if last_check is None:
        return True
    elapsed = time.time() - last_check
    limit = (config["update_policy"]["minimum_check_hours"] * 3600)
    return elapsed > limit

def fetch_cpi(config: dict[str,Any]) -> list[dict[str,Any]]:
    source = config["source"]
    params = {
        "series_id": source["series_id"],
        "api_key": source["api_key"],
        "file_type": "json"
    }
    url = (
        "https://api.stlouisfed.org/fred/series/observations?"
        + urlencode(params)
    )
    try:
        with urlopen(url, timeout=15) as response:
            data = json.load(response.read())
            result = []
            for item in data["observations"]:
                value = None
                if item["value"] != ".":
                    value = float(item["value"])
                result.append(
                    {
                        "time": item["date"],
                        "value": value
                    }
                )
            return result
    except Exception as error:
        log(f"source_error={error}")
        return []













"""import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


NODE_ID = "macro_us_cpi"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_FILE = os.path.join(BASE_DIR, "macro_us_cpi.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
RUNTIME_FILE = os.path.join(BASE_DIR, "runtime.json")
LOG_FILE = os.path.join(BASE_DIR, "macro_us_cpi.log")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now_utc()} | {message}\n")


def load_json(path: str, default: dict[str, Any]) -> dict[str, Any]:
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict[str, Any]) -> None:
    temp_file = path + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    os.replace(temp_file, path)


def default_config() -> dict[str, Any]:
    return {
        "source": {
            "provider": "FRED",
            "series_id": "CPIAUCSL",
            "api_key": "123456789"
        },

        "update_policy": {
            "minimum_check_hours": 12
        }
    }


def default_runtime() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,

        "status": "idle",

        "last_action": None,

        "last_source_check": None,

        "last_successful_update": None,

        "variables": {}
    }


def default_output() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,

        "version": None,

        "tags": [
            "macro",
            "inflation",
            "us",
            "cpi"
        ],

        "description": "US Consumer Price Index",

        "provides": {
            "data_type": "time_series",
            "unit": "index",
            "frequency": "monthly"
        },

        "current": None,

        "history": [],

        "updated_at": None
    }


def should_check_source(runtime: dict[str, Any], config: dict[str, Any]) -> bool:
    last_check = runtime.get("last_source_check")

    if last_check is None:
        return True

    elapsed = time.time() - last_check

    limit = (
        config["update_policy"]["minimum_check_hours"]
        * 3600
    )

    return elapsed > limit


def fetch_cpi(config: dict[str, Any]) -> list[dict[str, Any]]:
    source = config["source"]

    params = {
        "series_id": source["series_id"],
        "api_key": source["api_key"],
        "file_type": "json"
    }

    url = (
        "https://api.stlouisfed.org/fred/series/observations?"
        + urlencode(params)
    )

    try:
        with urlopen(url, timeout=15) as response:
            data = json.loads(response.read())

        result = []

        for item in data["observations"]:
            value = None

            if item["value"] != ".":
                value = float(item["value"])

            result.append(
                {
                    "time": item["date"],
                    "value": value
                }
            )

        return result

    except Exception as error:
        log(f"source_error={error}")
        return []


def update() -> dict[str, Any]:
    config = load_json(
        CONFIG_FILE,
        default_config()
    )

    runtime = load_json(
        RUNTIME_FILE,
        default_runtime()
    )

    output = load_json(
        OUTPUT_FILE,
        default_output()
    )


    if not should_check_source(runtime, config):

        log("source_check_skipped")

        return output


    runtime["status"] = "running"
    runtime["last_action"] = "fetch_source"
    runtime["last_source_check"] = time.time()

    save_json(
        RUNTIME_FILE,
        runtime
    )


    data = fetch_cpi(config)


    if data:

        output["history"] = sorted(
            data,
            key=lambda x: x["time"],
            reverse=True
        )

        output["current"] = output["history"][0]

        output["version"] = int(time.time())

        output["updated_at"] = now_utc()


        runtime["status"] = "idle"
        runtime["last_action"] = "completed"
        runtime["last_successful_update"] = now_utc()


        save_json(
            OUTPUT_FILE,
            output
        )


        log("update_success")


    save_json(
        RUNTIME_FILE,
        runtime
    )


    return output


def query(output: dict[str, Any], arguments: list[str]) -> Any:

    if not arguments:
        return output["current"]


    if arguments[0] == "history":

        return output["history"]


    return output


if __name__ == "__main__":

    result = update()

    response = query(
        result,
        sys.argv[1:]
    )

    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False
        )
    )"""

"""
This Python script represents a single autonomous node in a macroeconomic research graph system.

The node architecture separates public output from internal execution state.

Files:

1. macro_us_cpi.json
- Public interface of the node.
- Other nodes, graph mapper, APIs, and query systems consume this file.
- Contains node identity, tags, description, provided data type, current observation, historical observations, and derived interpretations.
- It is regenerated by the node.

2. config.json
- Static configuration.
- Read once during startup.
- Contains source definitions, API settings, and update policies.
- Does not contain runtime variables.

3. runtime.json
- Persistent internal execution state.
- Used for debugging, recovery, and resume after unexpected shutdown.
- Contains current operation, checkpoints, last actions, and runtime variables.
- It is updated frequently.

4. log file
- Human-readable execution trace.

Design principles:
- A node is self-contained.
- External systems only depend on macro_us_cpi.json.
- Internal implementation details must not leak into the public contract.
- Runtime state must survive application restarts.
- File writes should be atomic to reduce corruption risk from unexpected power loss.
- History is considered public node data, not private cache.
- Nodes communicate through JSON contracts, not direct script calls.
"""