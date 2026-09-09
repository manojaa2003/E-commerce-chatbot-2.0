from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Annotated
import os

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage
)

from dotenv import load_dotenv

from app.router import get_router
from app.general_qa import general_qa_chain
from app.faq import faq_chain
from app.sql import sql_chain
from app.fall_back import fallback_chain


load_dotenv()


llm = ChatGroq(
    model=os.environ['GROQ_FAST']
)

class BasicStategraph(TypedDict):
    messages: Annotated[list, add_messages]
    router_output: Annotated[list, add_messages]
    rewritten_query: str


graph = StateGraph(BasicStategraph)

def query_rewriter(state):

    messages = state["messages"]

    current_query = str(messages[-1].content).strip()
    q = current_query.lower().strip()

    typo_map = {
        "retrun": "return",
        "retun": "return",
        "retunr": "return",
        "polciy": "policy",
        "polci": "policy",

        "paymet": "payment",
        "paymant": "payment",

        "delevary": "delivery",
        "delivary": "delivery",
        "delvery": "delivery",

        "shippng": "shipping",
        "shiping": "shipping",

        "ordr": "order",
        "trak": "track",
        "trcak": "track",
    }

    normalized_q = q

    for wrong, correct in typo_map.items():
        normalized_q = normalized_q.replace(wrong, correct)

    simple_messages = {
        "hi",
        "hello",
        "hey",

        "ok",
        "okay",

        "thanks",
        "thank you",
        "thank u",
        "thx",

        "bye",
        "goodbye",
        "good bye",

        "nope",
        "no",

        "got it",
        "understood",

        "cool",
        "great",
        "perfect",

        "that's all",
        "thats all",

        "no thanks",
        "no thank you",
    }

    normalized_simple = (
        normalized_q
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
        .strip()
    )

    if normalized_simple in simple_messages:

        print("\n========== QUERY REWRITER ==========")
        print("Type     : Conversation")
        print("Original :", current_query)
        print("Rewritten:", current_query)
        print("\n")

        return {
            "rewritten_query": current_query
        }

    faq_patterns = [

        # Chatbot

        "what is your name",
        "what's your name",
        "who are you",
        "what are you",
        "how can you help",
        "what can you help",
        "what do you do",
        "who made you",
        "tell me about yourself",

        # Return / Refund

        "return policy",
        "refund policy",
        "what is the return policy",
        "what's the return policy",
        "how long can i return",
        "how many days can i return",
        "can i return",
        "return products",
        "return a product",
        "how do i return",

        "payment methods",
        "what payment methods",
        "how can i pay",
        "payment options",
        "ways to pay",
        "what payment options",

        # COD INFORMATION

        "cash on delivery",
        "cash on delivery available",
        "do you have cash on delivery",
        "is cash on delivery available",
        "cod available",
        "is cod available",

        # Shipping / Delivery INFORMATION

        "shipping policy",
        "delivery policy",
        "how long does delivery take",
        "delivery time",
        "shipping time",
        "how long is shipping",

    ]

    if any(pattern in normalized_q for pattern in faq_patterns):

        # Correct obvious typo while preserving the user's intent.
        corrected_query = current_query

        for wrong, correct in typo_map.items():
            corrected_query = corrected_query.replace(
                wrong,
                correct
            )

        print("\n========== QUERY REWRITER ==========")
        print("Type     : FAQ")
        print("Original :", current_query)
        print("Rewritten:", corrected_query)
        print("====================================\n")

        return {
            "rewritten_query": corrected_query
        }

    unsupported_patterns = [

        # Payment ACTIONS

        "make payment",
        "make a payment",
        "pay for me",
        "can you pay",
        "complete payment",
        "process payment",
        "process my payment",
        "pay for this",
        "pay for it",
        "make the payment",
        "do the payment",

        # Purchase / Order ACTIONS

        "buy this for me",
        "buy it for me",
        "purchase this for me",
        "purchase it for me",
        "place an order",
        "place order",
        "place this order",
        "order this for me",

        # Order Tracking

        "track my order",
        "track order",
        "where is my order",
        "where's my order",
        "order tracking",
        "check my order",
        "check order status",
        "order status",
        "track my package",
        "where is my package",
        "where's my package",

        # Order Cancellation

        "cancel my order",
        "cancel order",
        "cancel this order",
        "cancel the order",
        "how do i cancel my order",

        # Order Modification

        "change my order",
        "modify my order",
        "change the order",
        "modify the order",
    ]

    if any(
        pattern in normalized_q
        for pattern in unsupported_patterns
    ):

        corrected_query = current_query

        for wrong, correct in typo_map.items():
            corrected_query = corrected_query.replace(
                wrong,
                correct
            )

        print("\n========== QUERY REWRITER ==========")
        print("Type     : Unsupported action")
        print("Original :", current_query)
        print("Rewritten:", corrected_query)
        print("====================================\n")

        return {
            "rewritten_query": corrected_query
        }

    if len(messages) == 1:

        print("\n========== QUERY REWRITER ==========")
        print("Type     : New query")
        print("Original :", current_query)
        print("Rewritten:", current_query)
        print("====================================\n")

        return {
            "rewritten_query": current_query
        }

    previous_user_messages = []

    for msg in messages[:-1]:

        if isinstance(msg, HumanMessage):

            text = str(msg.content).strip()

            if text:
                previous_user_messages.append(
                    text[:200]
                )

    # only recent context
    previous_user_messages = previous_user_messages[-5:]

    if not previous_user_messages:

        return {
            "rewritten_query": current_query
        }

    direct_product_phrases = [

        "just give me the product",
        "just give me the products",

        "just show me the product",
        "just show me the products",

        "show me the product",
        "show me the products",

        "give me the product",
        "give me the products",

        "show them",
        "give them",
        "show those",
        "give me those",

        "just show them",
        "just give them",

        "give me the mentioned product",
        "give me the product mentioned",

    ]

    is_direct_product = any(
        phrase in q
        for phrase in direct_product_phrases
    )

    context = "\n".join(
        f"U: {x}"
        for x in previous_user_messages
    )

    system_prompt = """
Rewrite an e-commerce user query using previous USER context.

Keep relevant product filters:
category, gender, brand, price, color, material, size,
rating, style, type and features.

Rules:
- Combine short product follow-ups with previous product context.
- New product category replaces the old category.
- Product references like it, this, that, one use product context.
- A gender-only follow-up modifies the previous product search.
- 1k=1000, 2k=2000, 3k=3000.
- Never convert currency.
- Never invent information.
- General questions must NOT inherit product context.
- Payment/order actions must NOT inherit product context.
- "just show me", "show them", "give me those" means retrieve
  products using the existing product context.
- Do not answer.
- Do not ask questions.
- Return ONLY the rewritten query.

Examples:

shirts under 2000
+ white
→ Find white shirts under 2000

Puma shoes under 3000
+ blue
→ Find blue Puma shoes under 3000

men's shoes under 2000
+ female
→ Find women's shoes under 2000

girls kurta under 2000
+ white cotton
→ Find white cotton girls kurta under 2000

Puma shoes
+ watches
→ Find watches
"""

    if is_direct_product:

        instruction = """
The user wants the products now.
Return the complete product search query.
"""

    else:

        instruction = """
Rewrite the current message using relevant product context.
"""

    human_prompt = f"""
Previous USER messages:
{context}

Current:
{current_query}

{instruction}
"""
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])

    rewritten_query = str(response.content).strip()

    # Remove accidental quotation marks
    rewritten_query = (
        rewritten_query
        .strip('"')
        .strip("'")
        .strip()
    )

    print("\n========== QUERY REWRITER ==========")

    print("Previous user context:")
    for msg in previous_user_messages:
        print(" -", msg)

    print("Original :", current_query)
    print("Rewritten:", rewritten_query)

    print("\n")

    return {
        "rewritten_query": rewritten_query
    }

def decision_node(state):

    router_output = state["router_output"][-1].content

    if router_output == "general_qa":
        return "general_qa_node"

    elif router_output == "faq":
        return "faq_node"

    elif router_output == "sql":
        return "sql_node"

    elif router_output == "fallback":
        return "fall_back_node"

    return END


graph.add_node("query_rewriter",query_rewriter)
graph.add_node("router",get_router)
graph.add_node("general_qa_node",general_qa_chain)
graph.add_node("faq_node",faq_chain)
graph.add_node("sql_node",sql_chain)
graph.add_node("fall_back_node",fallback_chain)

graph.set_entry_point("query_rewriter")

graph.add_edge("query_rewriter","router")
graph.add_conditional_edges("router",decision_node)
graph.add_edge("general_qa_node",END)
graph.add_edge("faq_node",END)
graph.add_edge("sql_node",END)
graph.add_edge("fall_back_node",END)

app = graph.compile()