@Author: Yukai Sun
@Date: 14.03.2023

main.py is the entry of the whole system
main_arm.py is for unit test of Arm-Einheit
main_hand.py is for unit test of Hand-Einheit
If the app can't run correctly, please try again!

For Unity Animation of Jiankun Wu
I have prepared the window widget to display your animation.
It's UnityWidget class at line 177 in GUI.py under "widget" folder.

To use this widget, please follow the instruction:
                   GUI.py
1. uncomment line 5 to import QWebEngineView
2. uncomment line 12 to resize the window for animation
3. uncomment line 26 to add UnityWidget into the window
4. line 187: configure the Unity server address

                RequestUtil.py
1. line 5: configure the server address to receive target position (x, y)
2. add "send_coordinate(x, y)" to the position you wonna call it and input x, y parameter
