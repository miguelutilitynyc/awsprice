.PHONY: run

venv: 
	@ python3 -m venv .venv  

activate: 
	@ . .venv/bin/activate  

install:
	@ python3 -m pip install -r requirements.txt