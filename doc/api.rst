====================================
Web API.
====================================


/available_scripts.json --- Get the available scripts
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Response returned in JSON format.

:returns: a list of [name, shor_doc] pairs

  


/script_help.json --- Get info and help for a script
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Response returned in JSON format.

:param script: The script name.

example::
    
    server.com/script_help.json?name=one_spike.py
   
:returns: a dict {"description": description, "arguments": { arg0 : info0, ... argN :infoN }}

info0 is a dict with the fowlwing keys:

name:
    The name of the argument. 

required:
    if the argument is required.
    
default:
    the default value.
    
type:
    the type of the argument as a string.

action:
    ... additional type specifyer.

help:
    help for the parameter.
  
/plot.jpeg --- Create a plot
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Response returned in jpeg image format.

:param script: The script name.

All other parameters are dependent on the script.

example::
    
    server.com/plot.jpeg?script=one_spike.py&theta1=0&xlim=-1%2C1&f=25&title=Plot&Rpp0=3240.0%2C2340.0%2C1620.0&Rpp1=2590.0%2C2210.0%2C1060.0&time=150
   
:returns: An image blob
  