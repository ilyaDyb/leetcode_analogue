import sys
import json
import importlib.util
import os
import datetime

from memory_profiler import memory_usage

def run_user_code(user_id: str, user_code: str, test_cases: str):
    filename = f'user_code_{user_id}.py'

    if "import" in user_code:
        return {"error": "You can't use imports in solutions"}
    
    with open(filename, 'w') as f:
        f.write(user_code)
    
    spec = importlib.util.spec_from_file_location("user_module", filename)
    user_module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(user_module)
    try:
        spec.loader.exec_module(user_module)
    except SyntaxError as e:
        os.remove(filename)
        return {"error": f"Syntax error in user code: {e}"}
    function_name = user_code[3: user_code.index("(")].strip()
    function = getattr(user_module, function_name)

    try:
        test_cases = json.loads(test_cases)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        os.remove(filename)
        return {'error': str(e)}

    start_time = datetime.datetime.now()

    for i, case in enumerate(test_cases):
        input_data = json.loads(case['fields']['input_data'])
        expected_output = json.loads(case['fields']['expected_output'])
        try:
            result = function(input_data)
            passed = result == expected_output
        except Exception as e:
            result = str(e)
            passed = False
        result = {
            "input": input_data,
            "expected": expected_output,
            "result": result,
            "passed": passed,
            "number": i,
        }

        if not passed:
            os.remove(filename)
            return result
    # memory_used = memory_usage()
    end_time = datetime.datetime.now()
    lead_time = end_time - start_time
    lead_time_total_milliseconds = int(str(lead_time)[8:].replace("0", ""))
    result["lead_time_total_milliseconds"] = lead_time_total_milliseconds
    # result["memory_used"] = memory_used
    os.remove(filename)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python executor.py <user_id> <user_code> <test_cases>")
        sys.exit(1)
    
    user_id = sys.argv[3]
    user_code = sys.argv[4]
    test_cases = sys.argv[5]
    print(user_id, user_code, test_cases)

    results = run_user_code(user_id, user_code, test_cases)
    print(results)
