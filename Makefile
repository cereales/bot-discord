EXEC=python3

all: start

start:
	@ touch log
	@ mv log log.last
	@ $(EXEC) main.py PROD > log 2>&1 &
	@ echo "Bot running."

tests:
	@ $(EXEC) -m unittest -v

check:
	$(EXEC) --version
	@ $(EXEC) --version | grep -q "[Pp]ython 3\.[1-9][0-9]" # >= 3.10
	@ echo "OK"

install:
	$(EXEC) -m pip install discord
	$(EXEC) -m pip install discord.py

update:
	$(EXEC) -m pip install --upgrade pip
	$(EXEC) -m pip install --upgrade discord
	$(EXEC) -m pip install --upgrade discord.py
