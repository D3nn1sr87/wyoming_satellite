#!/usr/bin/env python3
"""Button handler for muting/unmuting Wyoming Satellite."""
import asyncio
import logging
import time
import gpiozero
import requests

_LOGGER = logging.getLogger()

logging.basicConfig(level=logging.INFO)

BUTTON_GPIO = 17  # GPIO Pin für den Button
MIN_PRESS_INTERVAL = 0.5
WEBHOOK_URL = "http://homeassistant.local:8123/api/webhook/"

class ButtonHandler:
    """Handles button press and sends mute/unmute events"""
    def __init__(self, gpio_pin, loop):
        self.button = gpiozero.Button(gpio_pin, pull_up=True)
        self.is_muted = False
        self._last_press_time = 0
        self.loop = loop

    def start(self):
        self.button.when_pressed = self._on_press

    def stop(self):
        self.button.close()

    def _on_press(self):
        """Called in a separate thread by gpiozero"""
        now = time.time()
        if now - self._last_press_time < MIN_PRESS_INTERVAL:
            _LOGGER.debug("Ignoring button press, too soon since last press")
            return
        self._last_press_time = now
        asyncio.run_coroutine_threadsafe(self._toggle_mute(), self.loop)

    async def _toggle_mute(self):
        """Send Pause or Run event to Satellite."""
        try:
            new_state = not self.is_muted
            payload = {"response": new_state}
            _LOGGER.info("Triggering Satellite toggle via webhook: %s", payload)
            response = await asyncio.to_thread(requests.post, WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code == 200:
                self.is_muted = new_state
                _LOGGER.info("Webhook triggered successfully (%s). State: %s", response.status_code, self.is_muted)
            else:
                _LOGGER.error("Webhook failed: %s %s", response.status_code, response.text)
        except Exception as e:
            _LOGGER.error("Error calling webhook: %s", e)

async def main():
    _LOGGER.info("Ready")
    loop = asyncio.get_running_loop()
    button = ButtonHandler(BUTTON_GPIO, loop)
    button.start()

    try:
        while True:
            await asyncio.sleep(1)  # Keep the loop running
    except KeyboardInterrupt:
        button.stop()

if __name__ == "__main__":
    asyncio.run(main())
