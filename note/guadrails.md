<img src = 'img/guardrail_llm.png' width = 50%>

# Agent SDK:

- Agent loop: Built-in agent loop that handles calling tools, sending results to
  the LLM, and looping until the LLM is done.
- Python-first: Use built-in language features to orchestrate and chain agents,
  rather than needing to learn new abstractions.
- Handoffs: A powerful feature to coordinate and delegate between multiple
  agents.
- Guardrails: Run input validations and checks in parallel to your agents,
  breaking early if the checks fail.
- Function tools: Turn any Python function into a tool, with automatic schema
  generation and Pydantic-powered validation.
- Tracing: Built-in tracing that lets you visualize, debug and monitor your
  workflows, as well as use the OpenAI suite of evaluation, fine-tuning and
  distillation tools.

# Techniques for Guardrails:

1. Rule-based computation
2. LLM based metrics (e.g. perplexity, embedding similarity)
3. LLM judges (e.g. fine-tuned models, zero-shot)
4. Prompt engineering and Chain-of-thought

# Approach 1: Rule-based string manipulation

- Suppose you want your application to meet some general requirements, like a
  maximum text size, defining some forbidden words, or filtering out
  confidential information. The simplest technique is to check a message using
  some rules or heuristics. This is commonly used in guardrails that aim to
  identify, filter or mask confidential information like phone numbers, email
  addresses or bank accounts. For instance, a guardrail could identify and mask
  phone number in a text message using a simple rule-based regex.replace(...)
  call. Rule-based string manipulation techniques can be simple as a string
  operation like .lower(), regex.match(..), but could also use packages like
  NLTK.

- Don't be fooled — most of the guardrails included in toolkits like LLMGuard
  and GuardrailsAI are merely some simple computations. For instance, the
  ReadingTimerail from GuardrailsAI validates that a string can be read in less
  than a certain amount of time. The guardrail simply computes reading_time =
  len(value.split()) / 200 , that's all!

- Perks: Rule-based guardrails can be useful to check simple things; why use
  overly complex LLM prompts if a simple trick will do? They are deterministic,
  explainable and transparent.

- Pitfalls: Language can be subtle and context-dependent, so rule-based
  approaches may surpass intelligent jailbreak attacks or malicious prompt
  injections. They are not robust to deviating input. For instance, if a
  rule-based guardrail blocks the presence of the word "Pasta", it won't block
  "Spaghetti".

- Jailbreaking is a type of prompt injection where an attacker bypasses an LLM's
  safety guardrails to get it to generate harmful content. Prompt injection, in
  broader terms, refers to any manipulation of the input prompt that causes the
  LLM to behave in an unexpected way, potentially including bypassing safety
  measures.

# Approach 2: LLM based metrics

- Guardrails can also leverage LLM 'knowledge' to determine whether a message
  should be accepted, filtered or rejected. This is commonly done by applying
  metrics on LLM embeddings or probabilities. Popular metrics are perplexity and
  semantic similarity.

- Perplexity measures how well a model predicts a sequence of words in a given
  text. It can be thought of as a measure of uncertainty or "surprise" of an LLM
  when predicting a sequence. For instance, gibberish texts naturally have a
  high LLM perplexity. A gibberish-detection guardrail would reject an input
  string whenever the perplexity exceeds a certain threshold. Similarly,
  jailbreak and prompt injection attempts have on average high perplexity, as
  they are often incoherent messages. This phenomenon is for instance leveraged
  by NVIDIA NeMo's _jailbreak detection_ rail.

- LLM embedding similarity metrics can be used to estimate how similar a message
  is to a target message. Suppose we want an LLM to refuse to respond to any
  user message that is related to "pasta". Then we can use a guardrail that
  computes the semantic similarity score (e.g. cosine similarity, nearest
  neighbors) between the user message and a sentence on the target topic
  "pasta". For instance, the sentence "I like spaghetti" will yield a higher
  semantic similarity score to sentences about pasta than the sentence "I like
  cars". Our application could reject the input message whenever the score
  exceeds a specified threshold.

- Embedding similarity is also commonly used to compute how much two texts align
  using a so-called "alignment score". These are often applied when RAG systems
  are involved. For more information on RAG systems, see
  [this blogpost](https://blog.ml6.eu/leveraging-llms-on-your-domain-specific-knowledge-base-4441c8837b47)
  for a general explanation of RAGs and
  [this blogpost](https://blog.ml6.eu/elevating-your-retrieval-game-insights-from-real-world-deployments-84ccfcbe6422)
  on real-world deployment insights.

- **Perks:** LLM based methods utilize the linguistic patterns and associations
  the LLM has captured during its pretraining. They are more useful for
  guardrails that require semantic analysis than rule-based techniques.

- **Pitfalls:** Heuristic methods may overlook sophisticated jailbreak attempts
  or malicious prompt injections. Perplexity only works with open-source models
  as they require access to a model's raw output to obtain likelihoods.

# Approach 3: LLM judge

- Many guardrails use LLMs as judges to determine whether a text is valid or
  not. Either we use zero-shot classifiers, or we use a specialized LLM that is
  already fine-tuned for the relevant task.

- An example of an LLM judge is
  [NVIDIA NeMo's "self checking" method.](https://arxiv.org/pdf/2310.10501) This
  method prompts a generative LLM with a custom message to determine whether an
  input/output string should be accepted or not. For example, their custom _self
  check input_ rail asks an LLM the following question:

  ![](https://cdn.prod.website-files.com/63f3993d10c2a062a4c9f13c/66a77bd9fefa2223117bc621_666c52cff6bb35ccd9a31508_1st%2520image.jpeg)

- If the LLM generates "No", the message is accepted and will proceed in the
  pipeline. If the LLM generates "Yes", the self check input rail will reject
  the message and the LLM will refuse to answer.

- Many guardrails rely on
  [zero-shot](https://huggingface.co/tasks/zero-shot-classification) or few-shot
  classification. In zero-shot classification, an LLM is instructed to perform a
  classification task that it wasn't trained on, without providing examples in
  the prompt. We provide the model with a prompt and a sequence of text that
  describes what we want our model to do, like in the example above. Single or
  few-shot classification tasks also include a single or a few examples of the
  selected task in the prompt.

- Other examples of zero/few-shot classification guardrails are
  _SensitiveTopics_ and _Not Safe For Work Detection_(NSFW) from GuardrailsAI,
  as well as the _Ban Topics Scanner_ of LLMGuard. These guardrails reject a
  message whenever it covers a topics that is "forbidden" according to a
  pre-specified list of topics. These guardrails use a zero-shot classification
  LLM to predict the topics that a message covers, and will reject the message
  if one of the predicted topics is forbidden.

- **Fine-tuned LLM judge:** In cases where few-shot prompting may fall short, a
  fine-tuned model could prove useful. An LLM judge is not necessarily a
  generative LLM. GitHub is full of numerous different LLMs fine-tuned on all
  kinds of tasks, so why not benefit from the capacities they were trained on?
  For instance, GuardrailsAI's _CorrectLanguage_ rail utilizes Meta's
  _facebook/nllb-200-distilled-600M_ translation model (available on
  Huggingface) to detect a message's language, and translate the text from the
  detected language to the expected language. GuardrailsAI's _Toxic language_
  and LLMGuards _Toxicity Scanner_ utilize _unity/unbiased-toxic-roberta_ to
  return a toxicity confidence level. Other examples of an LLM fine-tuned to
  predict the safety of messages in the light of jailbreak attempts are
  [Llama Guard](https://arxiv.org/pdf/2312.06674) and
  [RigorLLM](https://arxiv.org/pdf/2403.13031).

- **Perks** LLM judges can be a good alternative when rule-based approaches and
  metrics fall short because they fail to capture complex patterns and meanings.
  We can benefit from the general capacity of LLMs to interpret complex texts,
  and take advantage of capacities of fine-tuned LLMs.

- **Pitfalls** Adding many LLM judge based guardrails requires deployment of
  multiple models. Multiple LLM calls cause latency and are also more expensive,
  considering that pricing is made per call. **Importantly,** LLM judging
  strongly relies on the capacity of the LLM to properly perform the task at
  hand. LLMs are still non-deterministic and might fail to follow the
  instructions.

  ![](https://cdn.prod.website-files.com/63f3993d10c2a062a4c9f13c/666c49e14456e653656f3f32_1*2dDvV0PJY7HWFViyONQlcw.png)

# Approach 4: Prompt engineering and chain-of-thought

- The previous discussed approaches mainly concern checking or filtering a
  message on certain conditions before it is passed on to the next stage of the
  application pipeline. However, we might also want to influence the way that an
  LLM responds such that the generated output is in the desired format. This is
  especially relevant when a dialogue requires more strict supervision, for
  instance when a sensitive topic is discussed that requires careful
  conversation guidelines.

- **Prompt engineering** is the process of crafting and refining input prompts
  to elicit relevant and accurate outputs from a language model. Designing
  prompts can optimize an LLM's performance for specific tasks or applications.

- Suppose we want to avoid off-topic responses, then we can also directly
  provide the generative LLM itself with instructions> This is done by
  concatenating additional information to the user's message , such that _"Hi!
  How do I make a pizza?"_ will be modified to:

  ![](https://cdn.prod.website-files.com/63f3993d10c2a062a4c9f13c/66a77bd9fefa2223117bc61d_666c52e20335ce5204e18900_2nd%2520table.jpeg)

- This way we can manipulate the dialogue between a user and a generative LLM
  through our application. The example above showcases simple, general
  instructions, but could also include a sample conversation, specify a
  conversational style (formal/informal), etc.

[**Chain-of-thought**](https://arxiv.org/abs/2201.11903) **(CoT)** prompt

- engineering is a method to structure prompts in a step-by-step manner to guide
  a language model through a complex reasoning process. By breaking down an
  instruction into smaller, logical steps, this way of prompting encourages the
  LLM to generate output of the same step-by-step structure. This can improve an
  LLM's ability to produce coherent and accurate responses. In the example
  figure below, taken from
  [Wei et al. (2022)](https://arxiv.org/pdf/2201.11903), this CoT prompt first
  incudes an example of a question and answer, where the bot answer includes the
  reasoning step. When generating the response to the next question, the
  generative LLM will adapt this way of speaking and will likely output a
  response that includes the reasoning step as well.

  ![](https://cdn.prod.website-files.com/63f3993d10c2a062a4c9f13c/666c49e1da0b953854be631a_1*E_9MYRSizx6vZtm8N7xb-Q.png)

Figure 3: Chain-of-thought prompting (Wei et al., 2022)

- A slightly different approach to chain-of-thought prompt engineering is to
  iteratively make LLM calls. Instead of making a single few-shot learning
  prompt like in the example above, we can split up the "response task" into
  multiple elements. NVIDIA's NeMo Guardrails is a toolkit that uses this
  approach. Instead of generating a response directly from an input prompt, they
  split up the generation phase in multiple stages: (1)
  _generate\_user\_intent,_ (2)_generate\_next\_steps_, and
  (3)_generate\_bot\_message_. Step (1) prompts the generative LLM with the
  instruction to choose a user intent from a list (like "greet", "ask
  about..."). Step (2) instructs to generate the possible next steps of the
  conversation, and step (3) instructs to generate the final response. Such an
  approach allows you to guide the generative LLM step-by step towards a fitting
  response. However, the downside is that each response requires more LLM calls,
  making it more costly and latent.

- **Perks** Dialogue rails allow for more complex, custom instructions. If coded
  intelligently, they can help your application return more suitable answers
  rather than _"I'm sorry, I cannot respond"_ all the time.

- **Pitfalls** As LLMs are non-deterministic and prompt instructions remain
  susceptive to jailbreak and prompt injection attacks. In case of splitting up
  the generation into separate steps: making multiple LLM calls for each
  message, which causes latency and deployment costs. Similar to LLM judges, the
  effectivity of this technique is strongly dependent on an LLMs capacity to
  accurately interpret the instructions. It can become hazardous when
  instructions are lengthy, making them unintelligible or prone to ambiguity.
