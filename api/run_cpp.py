import json
import os
import re
import subprocess
import tempfile


def run_cpp_analysis(stock_data):
    raw_output = ""
    filename = None

    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        filename = temp_file.name
        temp_file.close()

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Date,Symbol,Open,High,Low,Close,Volume\n")
            for row in stock_data:
                f.write(
                    f"{row['date']},TEMP,{row['open']},{row['high']},"
                    f"{row['low']},{row['close']},{row['volume']}\n"
                )

        base_dir = os.path.dirname(__file__)
        exe_path = os.path.abspath(os.path.join(base_dir, "../cpp_backend/analyzer.exe"))

        process = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output, error = process.communicate(input=filename)
        raw_output = output.strip()
        _cleanup_temp_file(filename)
        metrics = parse_cpp_output(raw_output)

        if process.returncode != 0:
            details = error.strip() or f"C++ analyzer exited with code {process.returncode}"
            return {"error": details, "raw": raw_output, "metrics": metrics}

        if not raw_output:
            return {"error": "C++ analyzer produced no output", "raw": raw_output, "metrics": metrics}

        if metrics is None:
            details = error.strip() or "C++ analyzer output could not be parsed"
            return {"error": details, "raw": raw_output, "metrics": None}

        payload = {"raw": raw_output, "metrics": metrics}
        if error.strip():
            payload["warning"] = error.strip()
        return payload

    except Exception as exc:
        _cleanup_temp_file(filename)
        return {"error": str(exc), "raw": raw_output, "metrics": parse_cpp_output(raw_output)}


def parse_cpp_output(output):
    match = re.search(r"\{[\s\S]*\}", output or "")
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _cleanup_temp_file(filename):
    if filename and os.path.exists(filename):
        os.remove(filename)
