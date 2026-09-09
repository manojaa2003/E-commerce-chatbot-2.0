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

    description="""
    Product catalog queries.

    Route here when the user wants to search, find, show, browse,
    recommend, filter, sort, compare, or check availability of
    products from the catalog.

    Product queries may contain any combination of:
    product category, gender, brand, price, budget, color,
    material, size, rating, style, type, features,
    popularity or sorting criteria.

    Examples:
    Find white cotton girls kurta.
    Find men's Puma shoes under 10000.
    Find blue cotton shirts.
    Show Nike shoes under 3000.
    Find the cheapest laptop.
    Find highly rated watches.
    Compare iPhone and Samsung phones.
    """,

    utterances=[
        # GENERIC PRODUCT SEARCH

        "show products",
        "find products",
        "search products",
        "browse products",
        "display products",
        "available products",
        "product catalog",

        "find me a product",
        "help me find a product",
        "i am looking for a product",
        "i need a product",
        "show me something",
        "show me some products",

        # CATEGORY

        "show shoes",
        "show shirts",
        "show kurtas",
        "show dresses",
        "show pants",
        "show jeans",
        "show laptops",
        "show mobiles",
        "show phones",
        "show headphones",
        "show watches",
        "show clothing",
        "show electronics",
        "show speakers",
        "show bags",

        "find shoes",
        "find shirts",
        "find kurtas",
        "find dresses",
        "find pants",
        "find jeans",
        "find laptops",
        "find phones",
        "find watches",
        "find bags",

        # GENDER

        "men shoes",
        "men's shoes",
        "mens shoes",
        "male shoes",

        "women shoes",
        "women's shoes",
        "womens shoes",
        "female shoes",

        "boys shoes",
        "boys clothing",

        "girls shoes",
        "girls clothing",
        "girls kurtas",

        "men shirts",
        "men's shirts",
        "women shirts",
        "women's shirts",

        "male clothing",
        "female clothing",

        # BRAND
        "nike shoes",
        "adidas shoes",
        "puma shoes",
        "puma products",
        "apple products",
        "apple phones",
        "iphone",
        "iphones",
        "samsung phones",
        "boat headphones",
        "sony headphones",
        "levi's shirts",
        "levis shirts",

        # BRAND + CATEGORY + PRICE

        "puma shoes under 2000",
        "puma shoes under 5000",
        "puma shoes under 10000",

        "nike shoes under 3000",
        "nike shoes under 5000",

        "levis shirts under 2000",
        "levi's shirts under 3000",

        "apple phones under 50000",
        "iphone under 100000",

        "samsung phones under 30000",

        # PRICE

        "products under 1000",
        "products under 2000",
        "products under 3000",
        "products under 5000",
        "products under 10000",

        "products below 1000",
        "products below 2000",
        "products below 5000",
        "products below 10000",

        "budget products",
        "cheap products",
        "affordable products",
        "premium products",

        # GENDER + CATEGORY + PRICE

        "men shoes under 2000",
        "men shoes under 3000",
        "men shoes under 10000",

        "women shoes under 2000",
        "women shoes under 3000",

        "girls kurtas under 2000",
        "girls kurta under 2000",

        "boys shirts under 2000",

        "men shirts under 3000",
        "women dresses under 5000",

        # COLOR

        "black shoes",
        "white shoes",
        "red shoes",
        "blue shoes",

        "black shirts",
        "white shirts",
        "blue shirts",

        "white kurtas",
        "black kurtas",

        "red dress",
        "blue dress",
        "black dress",

        "black bags",
        "white bags",

        # COLOR + GENDER + CATEGORY

        "white girls kurta",
        "white girls kurtas",

        "white women's shirts",
        "white women's shoes",

        "blue men's shirts",
        "blue men's shoes",

        "black men's shoes",
        "black men's shirts",

        "red women's dresses",

        # MATERIAL

        "cotton shirts",
        "cotton kurtas",
        "cotton dresses",
        "cotton pants",

        "leather shoes",
        "leather bags",

        "denim jeans",
        "denim shirts",

        "silk dresses",

        # MULTIPLE FILTERS

        "white cotton girls kurta",
        "white cotton girls kurtas",

        "white cotton shirts",
        "blue cotton shirts",

        "blue cotton men's shirts",

        "black leather shoes",

        "casual blue shirts",
        "formal men's shirts",

        "cotton kurtas under 2000",

        "white cotton girls kurta under 2000",

        "men's puma shoes under 10000",

        "white levi's shirts under 3000",

        "casual men's shirts under 3000",

        # STYLE / TYPE

        "casual shirts",
        "formal shirts",
        "casual shoes",
        "formal shoes",

        "button down shirts",
        "button-down shirts",

        "long sleeve shirts",
        "short sleeve shirts",

        "running shoes",
        "sports shoes",

        "party dresses",
        "formal dresses",

        # RATING

        "top rated products",
        "best rated products",
        "products above 4 stars",
        "products above 4 rating",
        "highest rated products",
        "products with good reviews",

        "best rated shoes",
        "best rated shirts",
        "highest rated phones",

        # POPULARITY

        "trending products",
        "popular products",
        "best selling products",
        "most reviewed products",
        "latest products",
        "new arrivals",

        # RECOMMENDATION

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

        # FILTERS

        "size 8 shoes",
        "size 9 shoes",
        "large tshirt",
        "large t shirt",
        "medium shirt",
        "small dress",

        "long sleeve shirts",
        "short sleeve shirts",

        "casual shirts",
        "formal shirts",

        "button down shirts",
        "button-down shirts",

        # SORTING

        "sort by price",
        "sort by rating",
        "lowest price first",
        "highest price first",
        "newest first",

        "cheapest products",
        "cheapest shoes",
        "cheapest phone",

        "most expensive products",

        # COMPARISON

        "compare products",
        "compare iphone and samsung",
        "which phone is better",
        "difference between products",
        "compare two phones",
        "compare shoes",

        # AVAILABILITY

        "in stock products",
        "out of stock products",
        "available shoes",
        "available shirts",
        "available phones",

        # NATURAL PRODUCT QUERIES

        "i need a laptop",
        "i need headphones",
        "i need running shoes",
        "i need men's shoes",
        "i need women's shoes",

        "i need a shirt",
        "i need a kurta",
        "i need a dress",

        "help me find a product",
        "find me a gift",

        "i am looking for a smartwatch",
        "i want a new phone",

        "show me laptops under 50000",
        "find nike shoes under 3000",

        "find white cotton girls kurta",
        "find men's puma shoes under 10000",
        "find blue cotton shirts",
        "find casual men's shirts",
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
    query = state["rewritten_query"]
    router_ans = router(query)

    route_name = router_ans.name if router_ans.name is not None else "fallback"

    return {
        "router_output": [AIMessage(content=route_name)]
    }
        
if __name__ == "__main__":
    print(test_router("Find female watches under 2000"))
