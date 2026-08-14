import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from semantic_router import Route
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.routers import SemanticRouter

from langchain_core.messages import AIMessage
from dotenv import load_dotenv

encoder = HuggingFaceEncoder(
    name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)

faq = Route(
    name="faq",
    description="Questions about returns, refunds, shipping, tracking, payments, discounts, order management and store policies.",
    utterances=[
        # Returns
        "return policy",
        "can i return my product",
        "can i return an item",
        "return my order",
        "how do i return a product",
        "how many days do i have to return",
        "return period",
        "is return available",
        "can i exchange a product",
        "exchange policy",
        "replacement policy",
        "replace my product",

        # Refunds
        "refund policy",
        "refund processing time",
        "when will i get my refund",
        "where is my refund",
        "refund status",
        "refund amount",
        "refund pending",
        "refund not received",
        "refund taking too long",
        "how do refunds work",
        "is refund possible",

        # Damaged Products
        "defective product",
        "damaged product",
        "faulty product",
        "received damaged item",
        "received defective product",
        "item arrived damaged",
        "package damaged",
        "replacement for damaged item",
        "wrong product received",

        # Order Tracking
        "track my order",
        "track order",
        "track package",
        "where is my order",
        "order status",
        "shipment status",
        "delivery status",
        "has my order shipped",
        "when will my order arrive",

        # Order Management
        "cancel my order",
        "modify my order",
        "change delivery address",
        "update delivery address",
        "change payment method",
        "edit my order",

        # Payments
        "payment methods",
        "accepted payment methods",
        "upi payment",
        "credit card payment",
        "debit card payment",
        "google pay",
        "phonepe",
        "paytm",
        "cash on delivery",
        "emi available",

        # Offers
        "discounts",
        "offers",
        "coupon",
        "promo code",
        "bank offers",
        "hdfc card offer",
        "sbi card offer",
        "icici card offer",
        "axis bank offer",
        "festival offers"
    ]
)

sql = Route(
    name="sql",
    description="Queries for searching, filtering, recommending and comparing products from the catalog.",
    utterances=[

        # Search
        "show products",
        "find products",
        "search products",
        "browse products",
        "display products",
        "available products",
        "product catalog",

        # Category
        "show shoes",
        "show laptops",
        "show mobiles",
        "show headphones",
        "show watches",
        "show clothing",
        "show electronics",
        "show speakers",
        "show bags",

        # Brand
        "nike shoes",
        "adidas shoes",
        "apple products",
        "samsung phones",
        "boat headphones",
        "sony headphones",
        "puma products",

        # Budget
        "products under 1000",
        "products under 2000",
        "products below 5000",
        "budget products",
        "cheap products",
        "affordable products",
        "premium products",

        # Rating
        "top rated products",
        "best rated products",
        "products above 4 stars",
        "highest rated products",
        "products with good reviews",

        # Popular
        "trending products",
        "popular products",
        "best selling products",
        "most reviewed products",
        "latest products",
        "new arrivals",

        # Recommendation
        "recommend products",
        "recommend shoes",
        "recommend a phone",
        "recommend a laptop",
        "recommend headphones",
        "suggest products",
        "suggest a smartwatch",
        "what should i buy",
        "best product for students",
        "best office laptop",
        "best gaming laptop",
        "best phone under 20000",
        "best shoes for running",

        # Filters
        "black shoes",
        "white shoes",
        "red dress",
        "size 8 shoes",
        "large tshirt",
        "medium shirt",

        # Sorting
        "sort by price",
        "sort by rating",
        "lowest price first",
        "highest price first",
        "newest first",

        # Comparison
        "compare products",
        "compare iphone and samsung",
        "which phone is better",
        "difference between products",

        # Availability
        "in stock products",
        "out of stock products",

        # Natural Queries
        "i need a laptop",
        "i need headphones",
        "i need running shoes",
        "help me find a product",
        "show me something good",
        "find me a gift",
        "i am looking for a smartwatch",
        "i want a new phone",
        "show me laptops under 50000",
        "find nike shoes under 3000"
    ]
)

general_qa = Route(
    name="general_qa",
    description="Greetings, assistant identity, capabilities, casual conversation and general questions.",
    utterances=[

        # Greetings
        "hi",
        "hello",
        "hey",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",

        # Goodbye
        "bye",
        "goodbye",
        "see you",
        "talk to you later",

        # Thanks
        "thanks",
        "thank you",
        "thanks a lot",
        "thank you so much",
        "much appreciated",

        # Identity
        "who are you",
        "what are you",
        "what is your name",
        "tell me about yourself",
        "introduce yourself",
        "are you ai",
        "are you a chatbot",
        "are you chatgpt",

        # Capabilities
        "what can you do",
        "how can you help",
        "what can i ask you",
        "what services do you provide",
        "what are your abilities",
        "how do you work",
        "how do you find products",
        "how do you recommend products",

        # Conversation
        "can we chat",
        "lets talk",
        "i have a question",
        "i need some help",
        "help",
        "how are you",
        "good job",
        "awesome",
        "great",
        "cool",
        "nice",

        # Misc
        "who built you",
        "what model are you",
        "are you human",
        "are you real",
        "can you remember previous messages",
        "what are your limitations"
    ]
)

fallback = Route(
    name="fallback",
    utterances=[
        "hello",
        "hi",
        "thank you",
        "good morning",
        "how are you",
        "bye"
    ]
)

load_dotenv()

router = SemanticRouter(
    routes=[faq, sql, general_qa,fallback],
    encoder=encoder,
    auto_sync="local",
)

def test_router(query):
    router_ans = router(query)
    return router_ans.name

def get_router(state):
    query = state["messages"][-1].content
    router_ans = router(query)

    route_name = router_ans.name if router_ans.name is not None else "fallback"

    return {
        "router_output": [AIMessage(content=route_name)]
    }
        
if __name__ == "__main__":
    print(test_router("hi im manoj"))