# device_access
MCP server created to access the devices and perform operations.


git clone https://github.com/amity2230/device_access.git
cd device_access
pip install -r pyproject.toml  # or: uv sync
cp .env.example .env           # fill in OPENAI_API_KEY
# edit devices.yaml with their own device credentials
python device_mcp.py
