# debug.sh
echo "🔍 Debugging cosmonaut import..."

echo
echo "📁 Project structure:"
find src -type f

echo
echo "📦 pyproject.toml package-dir:"
grep -A2 "\[tool.setuptools\]" pyproject.toml

echo
echo "🔁 Installing in dev mode..."
uv pip install -e .

echo
echo "🧪 Testing import..."
uv run python -c "
try:
    from cosmonaut.cli.base import app
    print('✅ Success!')
except Exception as e:
    print('❌', e)
"
