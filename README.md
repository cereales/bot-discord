# bot-discord

![version](https://img.shields.io/badge/version-1.0.0-lightblue)

![python](https://img.shields.io/badge/python-3.8_|_3.9_|_3.10-4584b6)
![discord.py](https://img.shields.io/badge/discord.py-2.3.2-7289da)  \
<img src="https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png" width="23"/> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/165px-Python-logo-notext.svg.png" width="23"/><img src="https://discord.com/assets/f8389ca1a741a115313bede9ac02e2c0.svg" width="28"/>

This repository gathers all sources of several games developed for discord interface.


## About The Project

The goal of the project is to propose a program that allows to play board games from a distance via **Discord** social network.

### Key Features

- Based on `discord.py` API
- Asynchronous Python package using `asyncio`.
- Project management : `make`, config file.
- Test infrastructure based on `unittest`.

### Supported Games

- Hangman


## Getting Started

### Prerequisites

Before using this repository, make sure you check the followings:
1. You have **Python 3** installed.
2. You can run `make` commands.
3. You own a Discord account. If you don't, [create one](https://discord.com/login).
4. You have a Discord Bot ([Discord Application](https://discord.com/developers/applications))
that joined a guild.
See [this tutorial](https://discordpy.readthedocs.io/en/latest/discord.html)
if you need help on bot creation.

### Installing

Follow these steps in order to install the project on your computer:

<br/>

1. Clone the repository.
```txt
dirname="bot-discord"
git clone  https://github.com/cereales/bot-discord.git  "$dirname"
cd "$dirname"
```

<br/>

2. Make sure the installation checker runs well.
```
make check
```
Depending on your local installation, **Python 3** may be called with `python3` or `python` command. In case of failure, you can edit `EXEC` variable in `Makefile` to match the appropriate syntax.

<br/>

3. Install packages.
```
make install
```
Later, you will be able to update packages by running `make update`.

<br/>

4. Set up your bot credentials.
```
cp resources/config.ini.example resources/config.ini
```
Edit `resources/config.ini` to set your bot token and other confidential settings.


## Usage

To be able to run the project, you first need to add the project path to the `PYTHONPATH`.
```sh
# if already set
export PYTHONPATH="$(pwd):$PYTHONPATH"

# if not set
export PYTHONPATH=$(pwd)
```

Then run your bot with:
```
make
```
Stop it with
`kill -9 <pidof your python command>`.


## Production

To start bot at every reboot.


1. From project, run:
```sh
export DISCORDBOTPATH="$(pwd)"
echo "
# Added for PROD test of discord-bot, for crontab
export DISCORDBOTPATH=$DISCORDBOTPATH" | sudo tee -a /etc/environment
```

2. Edit crontab
```sh
crontab -e
```
and add line
> ```
> @reboot bash "$DISCORDBOTPATH/startup.sh" > "$DISCORDBOTPATH/cronlog" 2>&1
> ```


## Links
- [`discord.py` API](https://github.com/Rapptz/discord.py)
