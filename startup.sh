# This script manage all commands to run at startup of the bot for production.
# Add the line
# `@reboot bash "$DISCORDBOTPATH/startup.sh" > "$DISCORDBOTPATH/cronlog" 2>&1`
# in crontab to start the bot at every reboot of the host machine.

echo "$(date "+%d/%m/%Y %T")  Startup script"

# Move to project directory
cd "$DISCORDBOTPATH"
# Wait for the machine to be fully started.
sleep 60

# Environment variables
if [ -z "${PYTHONPATH}" ];
then
  # if not set
  export PYTHONPATH="$DISCORDBOTPATH"
else
  # if already set
  export PYTHONPATH="$DISCORDBOTPATH:$PYTHONPATH"
fi
echo "PYTHONPATH=$PYTHONPATH"

# update
git fetch -p
git checkout prod
git merge
# make update

# Run bot
make
echo "$(date "+%d/%m/%Y %T")  End of startup script."
