
------------------- DONE-------------------
Ok. building off the plan.md 

* The llm and user convesation should presist in the session. So each call to the llm is not a new conversion, but the llm shoudl have the history. 
* each session shoudl create a .jsonl file in the logs folder

* have a system prompt.md that is used. like "You are a helpful AI assistant ..." and this is used for every session.
* allow overriding this with some env var. 


* after a user selects a tool for a session, then they can't change it halfway through the session. I think this will help make things simplier. 

* remove the record icon from the ui. 
* mkae the name ofthe app a env var in the .env file. SEt it to Galaxy Chat for now. and use this everywhere in the UI.
* make the chat input message area wider and taller. It shoudlbe most ofthe widith fothe screen. 
* format the output from the llm as markdown. so use the markdown library to render the output as html.
* make it so there can be multiple llms that are avaible to use. 
-- make a .yml file that defines the llm name, base url, api key, model name, and provider.
Then in the ui. alow users to select which llm they want to use for the chat.
* make the llm selection a dropdown in the UI.
Allow usrs to download a .txt of a chat session. 
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
