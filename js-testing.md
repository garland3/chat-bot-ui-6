# Frontend JavaScript Testing Strategy

This document outlines the strategy for testing the frontend JavaScript and Alpine.js components.

## Phase 1: Basic UI Verification with Beautiful Soup (Python)

For initial and basic UI verification, we will leverage Python's `BeautifulSoup` library. This approach allows us to:

-   **Verify static HTML structure:** Ensure key elements (e.g., titles, buttons, input fields) are present and have correct attributes (IDs, classes, placeholders).
-   **Check text content:** Confirm that static text elements display the expected values.
-   **Integrate with existing Pytest setup:** These tests will run as part of the existing Python backend test suite, simplifying the testing environment.

**Implementation:**
-   Tests will be written in Python using `pytest`.
-   `BeautifulSoup` will parse the `static/index.html` file.
-   Focus on asserting the presence and basic properties of UI elements.

**Example (Conceptual):**
```python
# tests/test_frontend_ui.py
from bs4 import BeautifulSoup

def test_app_title_present(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    assert soup.find('h1', class_='app-title').get_text() == 'Galaxy Chat'
```

## Phase 2: End-to-End UI Testing with Selenium (Containerized)

For more comprehensive end-to-end UI testing, including user interactions, dynamic content, and JavaScript-driven behavior, we will use Selenium. To avoid installing browser drivers and Selenium dependencies directly on the host operating system, Selenium tests will be executed within a Docker container.

This containerized approach offers several benefits:

-   **Isolated Environment:** Prevents conflicts with host system configurations and dependencies.
-   **Reproducibility:** Ensures tests run consistently across different development and CI/CD environments.
-   **Scalability:** Facilitates running tests in parallel or on remote Selenium Grid instances.

**Implementation:**
-   Tests will be written in Python using `pytest` and `selenium`.
-   A Dockerfile or Docker Compose setup will be used to create a containerized environment with a web browser (e.g., Chrome or Firefox) and Selenium WebDriver.
-   Tests will interact with the running frontend application (which can also be containerized).
-   Focus on simulating user flows, verifying dynamic UI updates, and testing form submissions.

**Example (Conceptual):**
```python
# tests/test_selenium_e2e.py
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_chat_message_send(selenium_driver):
    driver = selenium_driver
    driver.get('http://localhost:8000') # Assuming app is running
    message_input = driver.find_element(By.ID, 'messageInput')
    message_input.send_keys('Hello, AI!')
    send_button = driver.find_element(By.ID, 'sendBtn')
    send_button.click()
    # Assert message appears in chat history
```

**Container Setup (Conceptual):**
```dockerfile
# Dockerfile.selenium
FROM selenium/standalone-chrome:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD pytest tests/test_selenium_e2e.py
```

## Integration with CI/CD

Both phases of testing will be integrated into the GitHub Actions CI/CD pipeline to ensure automated verification of frontend changes on every push and pull request.