# Single-Turn vs Multi-Turn

- Single-Turn: The user provides a complete instruction or prompt, and the LLM
  generates a response based on that input.

- Multi-Turn: The user provides a partial instruction, and the LLM interacts
  with the user to clarify the instruction, gather more information, and
  ultimately generate the final response.

# Intent classification vs tool calling

**No, intent classification is NOT a tool for function calling.** Instead,
**intent classification is used to DETERMINE which function/tool to call.**

Think of intent classification as a **router or dispatcher** that helps decide
what action to take, while function calling is the actual **execution of that
action**.

## The Flow: Intent Classification → Function Selection → Function Execution

```
User Input → Intent Classification → Function/Tool Selection → Function/Tool Execution
```

## Detailed Breakdown:

### 1. Intent Classification (Decision Making)

**Purpose:** Understand what the user wants to do

```python
def classify_intent(user_input):
    # This determines user's goal
    if "cancel" in user_input and "order" in user_input:
        return "CANCEL_ORDER"
    elif "weather" in user_input:
        return "GET_WEATHER"
    elif "book" in user_input and "flight" in user_input:
        return "BOOK_FLIGHT"
```

### 2. Function/Tool Selection (Mapping Intent to Action)

**Purpose:** Map the intent to the appropriate function/tool

```python
def select_function(intent):
    intent_to_function = {
        "CANCEL_ORDER": cancel_order_tool,
        "GET_WEATHER": get_weather_tool,
        "BOOK_FLIGHT": book_flight_tool,
        "TRACK_PACKAGE": track_package_tool
    }
    return intent_to_function.get(intent)
```

### 3. Function/Tool Execution (Taking Action)

**Purpose:** Actually perform the task

```python
def cancel_order_tool(order_id):
    # This is the actual function that does the work
    order_system.cancel_order(order_id)
    return f"Order {order_id} has been cancelled"

def get_weather_tool(location):
    # This is the actual function that gets weather data
    weather_data = weather_api.get_current_weather(location)
    return f"Weather in {location}: {weather_data}"
```

## Complete Example in Practice:

```python
class CustomerServiceAgent:
    def __init__(self):
        # Define available tools/functions
        self.tools = {
            "CANCEL_ORDER": self.cancel_order,
            "TRACK_ORDER": self.track_order,
            "GET_REFUND": self.process_refund,
            "UPDATE_ADDRESS": self.update_shipping_address
        }
    
    def process_user_request(self, user_input):
        # Step 1: Intent Classification (Understanding)
        intent = self.classify_intent(user_input)
        print(f"Detected intent: {intent}")
        
        # Step 2: Function Selection (Decision)
        selected_tool = self.tools.get(intent)
        if not selected_tool:
            return "I don't understand what you want to do"
        
        # Step 3: Function Execution (Action)
        result = selected_tool(user_input)
        return result
    
    def classify_intent(self, user_input):
        """This is NOT a function call - it's analysis/classification"""
        user_input = user_input.lower()
        
        if "cancel" in user_input and "order" in user_input:
            return "CANCEL_ORDER"
        elif "track" in user_input or "where is" in user_input:
            return "TRACK_ORDER"
        elif "refund" in user_input:
            return "GET_REFUND"
        elif "address" in user_input and "change" in user_input:
            return "UPDATE_ADDRESS"
        else:
            return "UNKNOWN"
    
    def cancel_order(self, user_input):
        """This IS a function call - it performs actual work"""
        # Extract order ID, call cancellation API, etc.
        return "Your order has been cancelled"
    
    def track_order(self, user_input):
        """This IS a function call - it performs actual work"""
        # Look up tracking info, call shipping API, etc.
        return "Your order is out for delivery"

# Usage Example:
agent = CustomerServiceAgent()

# User says: "I want to cancel my order"
response = agent.process_user_request("I want to cancel my order")

# What happens:
# 1. classify_intent() returns "CANCEL_ORDER" 
# 2. select tool: self.cancel_order
# 3. execute: self.cancel_order() - THIS is the function call
```

## Key Distinctions:

| Intent Classification      | Function/Tool Calling       |
| -------------------------- | --------------------------- |
| **Analysis/Understanding** | **Action/Execution**        |
| Determines WHAT to do      | Actually DOES it            |
| Returns a category/label   | Returns a result/outcome    |
| No external side effects   | Has external side effects   |
| Classification task        | API call/system interaction |

## In Modern AI Agent Frameworks:

### OpenAI Function Calling Example:

```python
# Intent classification happens in the LLM's reasoning
# Function calling is the actual tool execution

tools = [
    {
        "type": "function",
        "function": {
            "name": "cancel_order",  # This is the actual function
            "description": "Cancel a customer order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_weather",  # This is the actual function
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }
]

# When user says "Cancel my order #12345"
# 1. LLM does intent classification internally (understanding)
# 2. LLM decides to call cancel_order function (selection)
# 3. System executes cancel_order(order_id="12345") (action)
```
