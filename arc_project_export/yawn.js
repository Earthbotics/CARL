controlCommand("Auto Position", "AutoPositionAction", "Singing");
sleep(900);

controlCommand("Auto Position", "AutoPositionAction", "Stop");
sleep(500);
while (getVar("$AutoPositionStatus") == 1);