@echo off

:: Set up the environment (install dependencies)
echo Setting up the environment...

:: Install dependencies using pip
pip install -r requirements.txt

python -m venv venv
call venv\Scripts\activate

echo Setup complete!
