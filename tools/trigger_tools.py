def log_result(data):
    print(f"[Tool: log_result] Logging to DB: {data}")
    return "Logged"

def send_notification(input_data):
    # Just print whatever we fetch
    message = input_data
    if isinstance(input_data, dict):
        message = input_data.get("message", "Defect Alert")
        
    print(f"[Tool: send_notification] Sending alert: {message}")
    return "Sent"
