# Orbitflow

Orbitflow is a python-based reproduction of the paper **Load-Balancing Routing for LEO Satellite Network with Distributed Hops-Based Back-Pressure Strategy**, written by **Chi Han, Wei Xiong,** and **Ronghuan Yu**. 

> Link to Paper: https://www.mdpi.com/1424-8220/23/24/9789

This project simulates a simplified LEO satellite network and compares two routing algorithms:

**OSPF:** A traditional shortest-path routing algorithm
**DHBP:** The paper's proposed destination hops-based back-pressure routing algorithm
___
# Development Setup
 
## 1. Clone the Repository

Clone the repository and open it in VS Code.

``` powershell
git clone https://github.com/sorokaben/orbitflow
cd orbitflow 
```

## 2. Create  Virtual Environment

From the orbitflow directory, run:

``` powershell
python -m venv .venv # Creates a folder named .venv
# DO NOT commit this file to GitHub
# Ensure .gitignore contains: 
.venv/
```

## 3. Activate Virtual Environment
``` powershell
.venv\Scripts\Activate.ps1 
# Rerun this command every time you return to the project
```
## 4. Install Project Dependencies
``` powershell
pip install -r requirements.txt
```
## 5. Adding New Package

When you install a new package, run:

``` powershell
pip install package-name
pip freeze > requirements.txt # Updates for everyone
# Always commit requirements.txt
```

## 6. Deactivate Virtual Environment

``` powershell
deactivate
```