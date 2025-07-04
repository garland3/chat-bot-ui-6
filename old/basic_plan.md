write a description for a fastapi project. 

this is a chatbot ui. 

it has a bakend which connects to an open ai compliant api for the llm, and embedding models. 

do not ue ethe openai libray, but requests. make the base url ,  api key, and model name configurable via environment variables.

there is a folder called 'tools'
- each file implements an abstract class for a tool that can be used by the chatbot.

The backend implements a /data api endpoint. that the frontend can use to query what data sources exists.

on a chat completion, the user can have select N tools and M data sources in addition to their chat message.

the backend will use the selected tools and data sources to augment the chat message before sending it to the LLM API. For now make up basic place holder tools and data sources.

the code is broken into fastapi routers to help keep the project organized.

the app uses websockets. 

there is an 'agent session' that starts when a user connects via websocket.

every session is logged with a unique ID. The session manager has a log() method which accepts the message type, content as json.

users will login via  reverse proxy. So check X-EMAIL-USER header for the email address of the user. however in test mode, the email is just test@test.com. This is configured via an environment variable. At the start of the app, a middleware checks this.

There is access control on data sources and tools. So, not all users can access the tools. Add a pseudo group check that will eventually be replaced with a real access control system.. Make sure this is in a separate file. so it can be easily replaced later.

The ui looks nice. with a dark theme and a responsive design. use a static folder. do not use jinja templates. 

All routes to the app are protected by a middleware that checks if the user is logged in. Also the reverse proxy should set the X-EMAIL-USER header to the user's email address. 



logs are saved to a logs file. EAch session makes a new jsonl file. 

The project is structured to ensure maintainability and scalability, with a focus on clean code practices. Each module is designed to be modular and reusable, adhering to the principles of separation of concerns.

the senior engineer mandates that files not be longer than 300 lines. 


There is a rate limit of 1 active sesion per user at a time. If a user tries to start a new session while one is already active, they will receive an error message.

The user's input shoud always be sanitized to prevent injection attacks.


Eventually the data sources will come from an api or database, but for now, they are hardcoded as placeholders.


Tools  for now are. 
1. BasicMathTool - performs basic arithmetic operations.
2. codeExecutionTool - executes simple code snippets. (now sure how to make this safe, so just a placeholder for now)
3. user look up tool - retrieves user information based on email. or antoehr user in the coorporate directory. just make up a few users for now.
4. sql query tool. For now. make a small sqlite db with some sample data about payments and custsomers.  The tool will expose to the llm the tables. The llm can then qrite a SQL query to retrieve data from the database, but only in a read-only manner, .. like noly select queries.

For these tools, the llm will be required to put something for the tool_calls in the openai compliant format. So you need to pass the json response from the tools to the LLM API in the correct format.. 


somem tools can modify the  ui, . like add a button or show a plot or some custom component. 

IN regular chat mode, the user the app is jsut a chat interface. Use streaming responses from the LLM API to provide a real-time chat experience.

when doing tools or more agentic flows, then use the websockets to send back status updates to the UI. Send a 'thinking' message very 5 seconds for longer running tasks. 


There is a feedback button. uses can provide feedback on the chat experience, which is logged in the session log.

All tool calls have a time out. 

on start up, do a quick health check that promtps with "hi" and sets the max rerun tokens to 3. 

If the LLM is down. the show a message in the UI that the LLM is currently unavailable.

never use alersts in html. only toasts. 

If there is an error, then store the error in the sssion log. Always store the traceback as well. 

User sessions are stored in memmory for now. 

make a docker container. 
setup a dev container. 

Testing. 
- Use pytest for unit tests.
- Use httpx for testing the FastAPI endpoints.
- Use pytest-asyncio for testing asynchronous code.
- use env vars to turn off soem features that are hard to test or cause issues in tests, like the websocket connection or the LLM API calls.


I'll provide the openai api key in the .env file. 

for configuration use a pydantic. Allow extra itmes in the .env file. 