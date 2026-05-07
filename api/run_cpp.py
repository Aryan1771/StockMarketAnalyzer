import json
import os
import re
import subprocess
import tempfile


def run_cpp_analysis(stock_data):
    raw_output = ""
    filename = None
    fallback_metrics = _python_fallback_metrics(stock_data)

    try:
        if not _supports_native_cpp():
            return {
                "warning": "Native C++ analyzer is unavailable on this platform; using Python fallback metrics.",
                "raw": "",
                "metrics": fallback_metrics,
                "fallback": "python",
            }

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
        if not os.path.exists(exe_path):
            return {
                "warning": "Native C++ analyzer executable was not found; using Python fallback metrics.",
                "raw": "",
                "metrics": fallback_metrics,
                "fallback": "python",
            }

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
        return {
            "error": str(exc),
            "warning": "Native C++ analyzer failed; using Python fallback metrics.",
            "raw": raw_output,
            "metrics": parse_cpp_output(raw_output) or fallback_metrics,
            "fallback": "python",
        }


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


def _supports_native_cpp():
    return os.name == "nt"


def _python_fallback_metrics(stock_data):
    if not stock_data:
        return None

    closes = [float(row.get("close") or 0) for row in stock_data]
    latest_price = closes[-1]
    first_price = closes[0]
    change_percent = round(((latest_price - first_price) / first_price) * 100, 2) if first_price else 0.0

    window = closes[-5:] if len(closes) >= 5 else closes
    moving_average = round(sum(window) / len(window), 4) if window else 0.0

    latest_span = _latest_stock_span(closes)

    return {
        "symbol": "TEMP",
        "latest_price": round(latest_price, 4),
        "change_percent": change_percent,
        "moving_average": moving_average,
        "stock_span": latest_span,
    }


def _latest_stock_span(closes):
    if not closes:
        return 0

    stack = []
    span = 1
    for index, price in enumerate(closes):
        while stack and closes[stack[-1]] <= price:
            stack.pop()
        span = index + 1 if not stack else index - stack[-1]
        stack.append(index)
    return span
