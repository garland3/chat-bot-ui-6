import pytest
from bs4 import BeautifulSoup
import os

@pytest.fixture(scope="module")
def index_html_content():
    # Get the absolute path to the index.html file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file_path = os.path.join(current_dir, '..', 'static', 'index.html')
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        return f.read()

def test_app_title_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    app_title = soup.find('h1', class_='app-title')
    assert app_title is not None, "App title not found"
    assert app_title.get_text(strip=True) == "Galaxy Chat", "App title text is incorrect"

def test_new_chat_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    new_chat_button = soup.find('button', id='newChatBtn')
    assert new_chat_button is not None, "New Chat button not found"
    assert "New Chat" in new_chat_button.get_text(strip=True), "New Chat button text is incorrect"

def test_message_input_textarea_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    message_input = soup.find('textarea', id='messageInput')
    assert message_input is not None, "Message input textarea not found"
    assert "Type your message here..." in message_input.get('placeholder'), "Message input placeholder is incorrect"
