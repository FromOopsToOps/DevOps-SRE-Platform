This is a python module I created for a Python API I also created;
It's used right now in production to monitor a react component's functioning
on a certain part of the home page.
In case of problems, it throws alerting our way. It also capitalizes in the
react components logic instead of it's appearance on the frontend
making this a way more reliable monitoring tool.

The component works by sending a request to another API. That API returns
data referring to the marketing campaign. Then the component builds code for
an iframe, that it will insert in a carousel, inside a div, inside a container.

I created this module to help track error on any step of the way.

# ---
# Add here the modules you need for your module to work.
import os
from selenium.webdriver.common.by import By
from flask import jsonify

# Add helpers to have common wait/load functions commonly used by all.
import modules.helpers as helper
# Add alerting to add alert messages (Slack, Pagerduty) capacity
import modules.alerting as alert

# This is useful for debugging on Cloud Logging
#import logging

# add here the error messages needed by this module
messages = {
    "test_integration": "IGNORE IN THE MEANTIME - I'm testing the integration. - Rafa",
    "error_noDivInContainer": "There SHOULD be a container here, but there isn't -- react component is failing",
    "error_noIframeInDiv": "There SHOULD be an iframe inside the div, but there isn't -- react component is failing",
    "error_blankREDACTEDBanner": "CAMPAIGN IS FLAWED, review campaign for the REDACTED banner (blank banner)",
    "exception": "Oh oh... something broke the code execution."
}

# Environment-specific URLs for this module
TARGET_URLS = {
    "STG": "REDACTED",
    "PROD": "REDACTED",
    "DEV": "REDACTED"
}

# main function that checks the banner
def check_REDACTED_banner(driver, env):
    ENV = os.getenv("ENV", "DEV")
    USER_AGENTS = "REDACTED" if ENV in ["STG", "DEV"] else None
    target_url = TARGET_URLS.get(env, TARGET_URLS["DEV"])

    try:
#        logging.info(f"[DEBUG] Navigating to {target_url}")
        if USER_AGENTS:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': USER_AGENTS})

        driver.get(target_url)
        helper.wait_for_page_load(driver)

        REDACTED_containers = driver.find_elements(By.ID, "hp_sponsored__REDACTED_container")
#        logging.info(f"[DEBUG] Found {len(REDACTED_containers)} REDACTED_containers")

        if not REDACTED_containers:
            return jsonify({"status": 200, "message": "No REDACTED slide present"}), 200

        REDACTED_divs = REDACTED_containers[0].find_elements(By.ID, "hp_sponsored__REDACTED")
#        logging.info(f"[DEBUG] Found {len(REDACTED_divs)} REDACTED_divs")

        if not REDACTED_divs:
            alert.send_alert_message(messages["error_noDivInContainer"])
            return jsonify({"status": 500, "error": "hp_sponsored__REDACTED not found"}), 500

        REDACTED_div = REDACTED_divs[0]
        iframes = REDACTED_div.find_elements(By.TAG_NAME, "iframe")
#        logging.info(f"[DEBUG] Found {len(iframes)} iframes")

        if not iframes:
            alert.send_alert_message(messages["error_noIframeInDiv"])
            return jsonify({"status": 500, "error": "No iframe found"}), 500

        driver.switch_to.frame(iframes[0])
        images = driver.find_elements(By.CSS_SELECTOR, "img[src$='.png'], img[src$='.jpg'], img[src$='.jpeg']")
#        logging.info(f"[DEBUG] Found {len(images)} images inside iframe")
        driver.switch_to.default_content()
        driver.quit()

        if images:
            return jsonify({"status": 200, "message": "Image found"}), 200
        else:
            alert.send_alert_message(messages["error_blankREDACTEDBanner"])
            return jsonify({"status": 500, "error": "No PNG image found"}), 500

    except Exception as e:
#        logging.exception("[ERROR] Exception occurred during check_REDACTED_banner")
        alert.send_alert_message(messages["exception"])
        return jsonify({"status": 500, "error": str(e)}), 500

# This will never be reached, but it's a DEFENSIVE FALLBACK in case of errors
#    logging.warning("[WARN] check_REDACTED_banner() reached end without returning")
    return jsonify({"status": 500, "error": "Inform Madtech Team"}), 500
