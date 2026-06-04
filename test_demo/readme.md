浏览器打开 https://www.python.org/downloads/release/python-3120/ ，下载 macOS installer (arm64)
双击 .pkg 安装
安装默认 /Applications/Python 3.12

echo 'alias python3="/usr/local/bin/python3.12"' >> ~/.zshrc
source ~/.zshrc

cd ai_agent/test_demo
python3 -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
python easy_chat.py
