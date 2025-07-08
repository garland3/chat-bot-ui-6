# uv venv venv --python=3.11 &&  source venv/bin/activate && uv pip install -r requirements.txt && uv pip install requirements-dev.txt
uv venv venv --python=3.11
source venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
sudo apt update
sudo apt install -y procps 
# playwright install    
#  playwright install-deps  
npm install -g @google/gemini-cli
npm install -g @anthropic-ai/claude-code