Trigger Bot for CS2 Project based on YoloV8 by Ultralytics. <br>
<br>
Project is created to automatically fire if the target enters the detection zone of the artificial intelligence in the center of the captured screen. <br>
More than 12k screenshots were used for training. <br>
A small part was done manually, to collect the base, then I made a semi-automatic script that did a huge part of the work. <br>
<br>
Trigger bot has a GUI menu, inside which you can select a tab, the first tab is the setting of the bot's operating mode, <br>
the option to see its operation in a pop-up window inside gui, see changes that affect the operation of artificial intelligence, etc. <br>
And the second tab has been created for working with recoil-control, you can select from list the current weapon, <br>
and from choosed weapon - in the 'json' or 'txt' format will be dynamically loaded setup, which affects the movement of the mouse during shooting. <br>
<br>
You can change the coordinates of the mouse movement, <br>
Dynamic display of the current coordinate during the shot has been performed by the red light in list, so that you can track the current shot coordinate. <br>
Also you can change the speed between the steps of mouse movement by coordinates, since each weapon has its own rate of fire. <br>
<br>
Ctypes library is used for dynamic screen scaling. <br>
The GUI is made on CustomTkinter. <br>
CV2 is used to create a canvas, this is needed to display the work of the AI ​​in the GUI menu, as well as to overlay the image of the main screen, <br>
where the secondary circle-sight is displayed, it changes color depending on the enabled mode (ai_off - red, ai_on - pink, ai/recoil_on - purple).<br>
