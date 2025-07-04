from tools.basic_math_tool import BasicMathTool
from tools.code_execution_tool import CodeExecutionTool
from tools.user_lookup_tool import UserLookupTool
from tools.sql_query_tool import SQLQueryTool

def test_basic_math_tool_add():
    tool = BasicMathTool()
    result = tool.execute(operation="add", num1=5, num2=3)
    assert result == {"result": 8}

def test_basic_math_tool_subtract():
    tool = BasicMathTool()
    result = tool.execute(operation="subtract", num1=5, num2=3)
    assert result == {"result": 2}

def test_basic_math_tool_multiply():
    tool = BasicMathTool()
    result = tool.execute(operation="multiply", num1=5, num2=3)
    assert result == {"result": 15}

def test_basic_math_tool_divide():
    tool = BasicMathTool()
    result = tool.execute(operation="divide", num1=6, num2=3)
    assert result == {"result": 2.0}

def test_basic_math_tool_divide_by_zero():
    tool = BasicMathTool()
    result = tool.execute(operation="divide", num1=6, num2=0)
    assert result == {"error": "Division by zero is not allowed."}

def test_basic_math_tool_invalid_operation():
    tool = BasicMathTool()
    result = tool.execute(operation="power", num1=2, num2=3)
    assert result == {"error": "Invalid operation."}

def test_code_execution_tool():
    tool = CodeExecutionTool()
    result = tool.execute(language="python", code="print('Hello, world!')")
    assert result == {"output": "Simulated output for python code: print('Hello, world!')", "status": "success"}

def test_user_lookup_tool_found():
    tool = UserLookupTool()
    result = tool.execute(email="john.doe@example.com")
    assert result == {"user_info": {"name": "John Doe", "title": "Software Engineer", "department": "Engineering"}, "status": "success"}

def test_user_lookup_tool_not_found():
    tool = UserLookupTool()
    result = tool.execute(email="nonexistent@example.com")
    assert result == {"error": "User not found.", "status": "failure"}

def test_sql_query_tool_select():
    tool = SQLQueryTool()
    result = tool.execute(query="SELECT name, email FROM customers WHERE id = 1")
    assert result["status"] == "success"
    assert result["results"] == [{'name': 'Alice Smith', 'email': 'alice@example.com'}]

def test_sql_query_tool_invalid_query():
    tool = SQLQueryTool()
    result = tool.execute(query="DELETE FROM customers")
    assert result == {"error": "Only SELECT queries are allowed.", "status": "failure"}

def test_sql_query_tool_syntax_error():
    tool = SQLQueryTool()
    result = tool.execute(query="SELECT FROM customers")
    assert result["status"] == "failure"
    assert "Database error" in result["error"]