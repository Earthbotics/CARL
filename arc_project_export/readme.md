# Scripts to Place into ARC (EZ-Robot Software)
\arc_project_export folders contains scripts that must be manually created in ARC just once and then saved into the project.

## Add Scripts to ARC Script Collection Skill
* Files ending with .ez, are to entered in as EZ-Robot script.
* Files ending with .js, are to entered in as JavaScript script.
Files are simple text files that can be opened with any text editor.

How to add & use the Script Collection robot skill
https://synthiam.com/Support/Skills/Scripting/Script-Collection

## Open CARL Project in ARC
1 Copy CARL_project.EZB file to the install folder for ARC '\ARC\My Projects'.
2 Open ARC and then Open CARL Project.
3 Add the scripts to Script Collection.
4 Configure the settings for Bing Recognition robot skill.
5 Configure the Camera skill with 'Tracking Start' Script contents.
6 Import the 'Waiting Fidget' AutoPosition.
7 To run, turn on JD, connect via ARC to JD's network, then start the HTTP server so the python app can communicate with ARC.

## Configure Bing Speech Recognition robot skill
1 Make sure '$BingSpeech' is the 'Variables' textbox.
2 Copy the contents of file, 'Bing Rec.js', to the 'Any Recognized Script', and save the config.

How to add & use the Bing Speech Recognition robot skill
https://synthiam.com/Support/Skills/Audio/Bing-Speech-Recognition

## Configure Camera Device robot skill for object detection
1 In Camera Config -> Tracking -> Tracking Start:, copy the contents of camera_config.js into the Event script editor and save. 
2 It is best to clear all previously trained objects and re-train the objects before your testing sessions as light changes day to day, etc., to achieve the best results with the ARC skill. This is a known limitation of the EZ-Robot hardware and software.

How to add & use the Camera Device robot skill
https://synthiam.com/Support/Skills/Camera/Camera-Device

## Add 'Waiting Fidget' (a custom AutoPosition for JD)
1 Import 'Waiting_Fidget.AutoPosition' in the AutoPosition skill.

How to add the Auto Position Movement Panel (Gait) robot skill
https://synthiam.com/Support/Skills/Movement-Panels/Auto-Position-Movement-Panel-Gait?id=16057

## HTTP Server robot skill
How to add & use the HTTP Server robot skill
https://synthiam.com/Support/Skills/Remote-Control/HTTP-Server