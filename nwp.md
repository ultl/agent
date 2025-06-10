# Google's Agents Whitepaper Notebook

# Authors and Contributors of the paper:

- **Authors**:
  - **Julia Wiesinger**: Google AI | Building Gemini and AI Agents for
    Developers
  - **Patrick Marlow**: GenAI Agents | Product | Keynote Speaker
  - **Vladimir Vuskovic**: Product lead of Search and Google Agentspace in
    Google Cloud AI | PhD

- **Contributors**:
  - **Evan Huang**: Director of Software Engineering at Google
  - **Yuan (Emily) Xue**: Senior Manager and LLM Engineering Lead at Google
    Cloud AI
  - **Olcan Sercinoglu**: Founder and CEO at Scaled Inference (Former Software
    Engineer at Google)

## 1. **What is an Agent?**

**Definition**: A Generative AI agent is an application that attempts to achieve
a goal by observing the world and acting upon it using available tools. Unlike
standalone language models, agents can act autonomously and proactively to reach
their objectives.

**Key Quote**: _"This combination of reasoning, logic, and access to external
information that are all connected to a Generative AI model invokes the concept
of an agent."_

**Example**: Instead of a model just answering "I don't know current flight
prices," an agent can actively search flight APIs, compare prices, and provide
real-time booking recommendations.

## 2. **Three Essential Components of Agent Architecture**

### **The Model**

- The language model (LM) serves as the centralized decision maker
- Can be one or multiple models of any size
- Should support reasoning frameworks like ReAct, Chain-of-Thought, or
  Tree-of-Thoughts. Read more at [reasoning.md](reasoning.md)
- Ideally trained on data signatures associated with planned tools

### **The Tools**

- Bridge the gap between model capabilities and external world interaction
- Enable agents to access real-time information and perform actions
- Three main types: Extensions, Functions, and Data Stores
- Limitations:
  - Define model-specific function schemas, which are JSON descriptions of the
    function, acceptable parameters, and what it returns. Implement handlers
    (the actual code that executes when a function is called) for those
    functions. Problems:
    - Different JSON schema formats for each model
    - Duplicate handler implementations
    - M×N problem: M models × N tools = M×N integrations
    - Inconsistent implementations across teams

=> Use MCP (Model Control Protocol) to standardize tool interactions across
models and tools, allowing for a single handler to work with multiple models.

### **The Orchestration Layer**

- A cyclical process governing how agents take in information, reason, and act
- Continues until the agent reaches its goal or stopping point
- Manages memory, state, reasoning, and planning

## 3. **Agents vs. Models Comparison**

| **Models**                         | **Agents**                                              |
| ---------------------------------- | ------------------------------------------------------- |
| Knowledge limited to training data | Knowledge extended through external tools               |
| Single inference per query         | Managed session history for multi-turn interactions     |
| No native tool implementation      | Tools natively implemented                              |
| No native logic layer              | Native cognitive architecture with reasoning frameworks |

## 4. **Cognitive Architectures and Reasoning Frameworks**

### **ReAct Framework**

**Process**:

1. **Question**: Input from user query
2. **Thought**: Model's reasoning about next action
3. **Action**: Decision on which tool to use
4. **Action Input**: Parameters for the tool
5. **Observation**: Result of the action
6. **Final Answer**: Response to user

**Example**: User asks "I want to book a flight from Austin to Zurich"

- _Thought_: "I should search for flights"
- _Action_: Use Flights tool
- _Action Input_: "flights from Austin to Zurich"
- _Observation_: Flight results returned
- _Final Answer_: "Here are some flights..."

### **Other Frameworks**:

- **Chain-of-Thought (CoT)**: Enables reasoning through intermediate steps
- **Tree-of-Thoughts (ToT)**: Explores multiple thought chains for complex
  problem solving

## 5. **Three Types of Tools**

### **Extensions**

**Purpose**: Bridge the gap between APIs and agents in a standardized way

**How they work**:

1. Teach the agent how to use API endpoints with examples
2. Define required arguments/parameters
3. Agent dynamically selects appropriate extension

**Example**: Google Flights Extension

- Agent learns: _"Use get_flights method when user wants to search for flights"_
- User query: "Show me flights from Austin to Zurich"
- Agent automatically calls the correct API with proper parameters

### **Functions**

**Purpose**: Generate structured outputs for client-side execution

**Key Differences from Extensions**:

- Model outputs function calls but doesn't execute them
- Execution happens client-side, not agent-side
- Provides more granular control to developers

**Use Cases**:

- Security restrictions preventing direct API calls
- Need for data transformation before/after API calls
- Asynchronous operations
- Human-in-the-loop reviews

**Example**: Travel Concierge

```python
# User: "I'd like to take a ski trip with my family"
# Function output:
{
  "function_call": {
    "name": "display_cities",
    "args": {
      "cities": ["Crested Butte", "Whistler", "Zermatt"],
      "preferences": "skiing"
    }
  }
}
```

### **Data Stores**

**Purpose**: Provide access to dynamic, up-to-date information through vector
databases

**Implementation**: Retrieval Augmented Generation (RAG)

1. User query → embeddings
2. Match against vector database
3. Retrieve relevant content
4. Provide to agent for processing

**Supported Data Types**:

- Website content
- PDFs, Word docs, spreadsheets
- Structured/unstructured databases
- HTML, TXT files

**Example**: Company policy agent that can answer questions by searching through
uploaded policy documents in real-time.

## 6. **Enhancing Model Performance**

### **Three Learning Approaches**:

1. **In-Context Learning**: Provide examples at inference time
   - _Like a chef getting a recipe and figuring out cooking "on the fly"_

2. **Retrieval-Based Learning**: Dynamically retrieve relevant examples
   - _Like a chef with access to a well-stocked pantry of ingredients and
     cookbooks_

3. **Fine-Tuning**: Pre-train on specific datasets
   - _Like sending a chef to culinary school to master specific cuisines_

## 7. **Production Implementation Example**

The whitepaper includes a practical LangChain example:

```python
# User query: "Who did the Texas Longhorns play in football last week? 
# What is the address of the other team's stadium?"

# Agent workflow:
# 1. Search for "Texas Longhorns football schedule"
# 2. Find opponent: Georgia Bulldogs
# 3. Search for "Georgia Bulldogs stadium"
# 4. Return: "100 Sanford Dr, Athens, GA 30602, USA"
```

## 8. **Key Takeaways**

1. **Agents extend language models** by adding autonomous reasoning and external
   tool access
2. **Orchestration layer is crucial** - it structures how agents think, plan,
   and act
3. **Tool selection matters** - Extensions for direct API control, Functions for
   client-side control, Data Stores for information access
4. **Iterative development is essential** - No two agents are alike;
   experimentation and refinement are key
5. **Future potential is vast** - Agent chaining and "mixture of agent experts"
   approaches will enable increasingly complex problem-solving

## 9. **Real-World Impact**

**Current Applications**:

- Customer service automation
- Data analysis and reporting
- Travel planning and booking
- Document search and summarization

**Future Possibilities**:

- Multi-agent systems with specialized roles
- Complex workflow automation
- Advanced problem-solving across industries
- Seamless human-AI collaboration

The whitepaper emphasizes that we're only beginning to scratch the surface of
agent capabilities, with the strategic combination of specialized agents
promising to deliver exceptional results across various domains.
