
# Rig Documentation
## Rename Tool

This tool allow you to rename *n* elements in your outliner.  
You have 3 different mode to make this program work.


- Replace Mode  
    Replace a word in selected item's names by an other  
- Prefix Mode  
    Add a word at the beginning of selected item's names  
- Suffix Mode  
    Add a word after selected item's names


## Hook Tool
Create an hook transform  
You have to mode to create an hook:  
- For *n* items selected  
    *U0* (hooker) hook *U1*  
    *U2* (hooker) hook *U3*
    ...
    *Un* (hoker) hook *Un+1*
- For *n* items selected  
    *U0* (hooker) hook *U1*  
    *U0* (hooker) hook *U2*  
    ...  
    *U0* (hooker) hook *Un*  


## Center Tool
Create a locator at the center of selected items  
Items could be:  
- Meshes  
- Edges  
- Faces  
- Vertices  


## Connexion Tool  
Tool that create attributes connexions between items  

To make it work you have to define origin items, that the tool will connect to target items  

You have to mode to create connexions:  
- For *x* origins and *y* targets (x=y)  
    *x0* connect to *y1*  
    *x1* connect to *y2*  
    ...  
    *xn0* connect to *yn*  
- For *1* origin and *n* targets  
    origin will be connected to all targets  

You can also define a constant (float number) that will create between origin(s) and target(s)
a mult double linear node (with that constant inside)
