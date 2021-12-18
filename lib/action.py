from machine import Pin

LED = Pin(25, Pin.OUT)
LED.value(0)


def do_led(action="down"):
    """Set the pico internal led up or down.

    Args:
        action (str, optional): up or down action. Defaults to "down".

    Raises:
        Exception: If the action is not allowed, an error is raised and the
        server with return and HTTP 400
    """
    if action.lower() == "up":
        LED.value(1)
    elif action.lower() == "down":
        LED.value(0)
    else:
        raise Exception(f"Action '{action}' for internal LED is not allowed")
