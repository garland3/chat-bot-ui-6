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

def test_connection_status_div_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    connection_status_div = soup.find('div', class_='connection-status')
    assert connection_status_div is not None, "Connection status div not found"

def test_tools_dropdown_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    tools_button = soup.find('button', class_='dropdown-toggle')
    assert tools_button is not None, "Tools dropdown button not found"
    assert "Tools" in tools_button.get_text(strip=True), "Tools dropdown button text is incorrect"

def test_data_sources_dropdown_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    data_sources_dropdown = soup.find('div', attrs={'x-data': 'dataSourcesDropdown'})
    assert data_sources_dropdown is not None, "Data Sources dropdown div not found"
    data_sources_button = data_sources_dropdown.find('button', class_='dropdown-toggle')
    assert data_sources_button is not None, "Data Sources dropdown button not found"
    assert "Data Sources" in data_sources_button.get_text(strip=True), "Data Sources dropdown button text is incorrect"

def test_model_dropdown_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    llm_dropdown = soup.find('div', attrs={'x-data': 'llmDropdown'})
    assert llm_dropdown is not None, "Model dropdown div not found"
    model_button = llm_dropdown.find('button', class_='dropdown-toggle')
    assert model_button is not None, "Model dropdown button not found"
    assert "Model" in model_button.get_text(strip=True), "Model dropdown button text is incorrect"

def test_download_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    download_button = soup.find('button', id='downloadBtn')
    assert download_button is not None, "Download button not found"
    assert "Download" in download_button.get_text(strip=True), "Download button text is incorrect"

def test_user_info_div_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    user_info_div = soup.find('div', id='userInfo')
    assert user_info_div is not None, "User info div not found"

def test_welcome_screen_div_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    welcome_screen_div = soup.find('div', id='welcomeScreen')
    assert welcome_screen_div is not None, "Welcome screen div not found"

def test_welcome_to_galaxy_chat_heading_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    welcome_heading = soup.find('div', class_='welcome-content').find('h2')
    assert welcome_heading is not None, "Welcome heading not found"
    assert welcome_heading.get_text(strip=True) == "Welcome to Galaxy Chat", "Welcome heading text is incorrect"

def test_send_button_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    send_button = soup.find('button', id='sendBtn')
    assert send_button is not None, "Send button not found"
    assert "Send" in send_button.get_text(strip=True), "Send button text is incorrect"

def test_typing_indicator_is_present(index_html_content):
    soup = BeautifulSoup(index_html_content, 'html.parser')
    typing_indicator = soup.find('span', id='typingIndicator')
    assert typing_indicator is not None, "Typing indicator not found"
    assert "AI is typing..." in typing_indicator.get_text(strip=True), "Typing indicator text is incorrect"

def test_send_button_disabled_when_llm_loading(index_html_content):
    # This test assumes the initial state of the HTML has "Loading..." for the model
    # and the send button should be disabled.
    soup = BeautifulSoup(index_html_content, 'html.parser')
    model_span = soup.find('span', class_='selected-model', string='Loading...')
    send_button = soup.find('button', id='sendBtn')
    
    assert model_span is not None, "Model loading indicator not found"
    assert send_button is not None, "Send button not found"
    assert send_button.has_attr('disabled'), "Send button is not disabled when LLM is loading"
