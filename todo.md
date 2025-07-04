------------------- DONE-------------------

Ok. building off the plan.md 

* The llm and user convesation should presist in the session. So each call to the llm is not a new conversion, but the llm shoudl have the history. 
* make the chat session history a scrollable area.
* make the chat input area a scrollable area as well. if the input is too long. 
------------------- END DONE-------------------


new items. 
* when connecting to the ui, the "conneting ...." shows red as the websocket is not connected. As soson as someone loads the page open a websocket connection.
* on the ui, list the avaible models and allow theusre to select one. 
The config defines. 
 app_name: str = "Galaxy Chat"
    llm_config_file: str = "config/llms.yml"

but this not being propogated to the UI. 

the docker file CMD should be uvicorn .... not gunicorn... only use 1 worker. or just don't set it at all. 

------------------- DIAGNOSING "CONNECTING..." ISSUE -------------------

To help diagnose why the "Connecting..." status persists, I've added extensive logging to `static/app.js`. Please open your browser's developer console (usually by pressing F12 or right-clicking and selecting "Inspect" -> "Console") and observe the output when you load the page. Share any errors or relevant messages you see there.