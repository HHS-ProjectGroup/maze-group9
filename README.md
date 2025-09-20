# SimpleMaze

A simple maze game written in Python, created for a school project by 1c Project Group 9 for ACS at THUAS (The Hague University of Applied Sciences).  
You are free to use, modify, and share this code — but it comes **as-is**, with no guarantees or support.  

---

## Project Description

SimpleMaze is a basic Python-based maze game.  

---

## How to Run

1. Make sure Python 3 is installed on your system.
2. Clone or download the repository.
3. Enter directory.
4. Create/activate virtual environment
5. Install the requirements from requirements.txt
6. Run

   ```bash/powershell/wsl
   git clone https://github.com/HHS-ProjectGroup/maze-group9.git
   cd maze-group9
   python -m venv .venv
   .venv\Scripts\activate # Should work for Windows  
   .venv/bin/activate # For Unix(Mac included)  
   pip install -r requirements.txt

   python main.py # Run game

   pytest tests # Run tests
