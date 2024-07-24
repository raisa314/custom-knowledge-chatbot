from semantic_router import Route
from dotenv import dotenv_values
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from utils.helper import model

config = dotenv_values(".env")
openai_api_key=config['OPENAI_API_KEY']

encoder = OpenAIEncoder() 

# Define the "hi" route
hi = Route(
    name="hi",
    utterances=[
        "Hi",
        "Hello",
        "Hey",
        "Great to be back",
        "How are you?",
        "How are you doing?",
        "What's up?",
        "How's it going?",
        "Hi there",
        "Greetings",
        "Hey, how's everything?",
    ],
    description="Route for greeting messages. The chatbot responds with a friendly greeting or inquiry about the user's well-being."
    # llm=model
)

# Define the "bye" route
bye = Route(
    name="bye",
    utterances=[
        "Goodbye",
        "Bye",
        "See you later",
        "Take care",
        "Catch you later",
        "Farewell",
        "Talk to you soon",
        "Have a good day",
        "Later",
        "See you around",
    ],
    description="Route for farewell messages. The chatbot responds with a courteous goodbye or well-wishing."
    # llm=model
)

# Define the "instruction manuals" route with more questions
instruction_manuals = Route(
    name="instruction_manuals",
    utterances=[
        "install",
        "setup",
        "set up",
        "USE",
        "Installation Procedure",
        "instruction manuals",
        "How to use X",
        "Can you give me the instruction manual for this product?",
        "I need the user guide for this device.",
        "Where can I find the instruction manual?",
        "Can you provide the manual for this product?",
        "I need help with the instructions for this item.",
        "How do I get the user manual for this gadget?",
        "Please provide the instruction manual.",
        "Can you show me the manual for this product?",
        "Where can I download the instruction manual?",
        "I need the instructions for this device.",
        "How do I install this product?",
        "How to set up this product?",
        "Where can I find the setup guide for this device?",
        "Can you help me with the set up instructions for this product?",
        "I need the installation guide for this gadget.",
        "Can you guide me through the installation process?",
        "I am looking for the setup instructions.",
        "How do I assemble this product?",
        "Show me the user manual for this item.",
        "Where is the user guide for this product?",
        "Help me with the user manual.",
        "What are the setup steps for this product?",
        "How do I configure this product?",
        "What is the procedure to set up this device?",
        "Can you walk me through the installation steps?",
        "I need the setup instructions.",
        "Where can I find the installation steps?",
        "How to initialize this product?",
        "Give me the setup guide.",
        "How do I start using this product?",
        "Step-by-step guide for installation.",
        "Detailed setup instructions needed.",
        "How to get started with this product?",
        "Can you provide the configuration guide?",
        "Instructions for assembling this product.",
        "Where can I get the user instructions?",
        "How to operate this device?",
        "Provide the installation process.",
        "What are the user manual steps?",
        "I need to set this up.",
        "How to set this device?",
        "Where can I read the user guide?",
        "What is the setup process?",
        "Can you show me how to use this product?",
        "Explain the setup procedure.",
        "I need the manual for this gadget.",
        "How to follow the installation steps?",
        "Where to find the setup instructions?",
        "Provide the installation details.",
        "How to proceed with the setup?",
        "What is the user manual for this item?",
        "Guide me with the installation.",
        "Show the user instructions.",
        "How to do the setup?",
        "Where are the installation guidelines?",
    ],
    description="Route for requests related to product usage, setup, installation, and instruction manuals. The chatbot provides relevant guides, manuals, and setup instructions."
    # llm=model
)

# Combine all routes into a single list
routes = [hi, bye]
routes1=[instruction_manuals]
# Create the RouteLayer with the encoder and routes
rl = RouteLayer(encoder=encoder, routes=routes,llm=model)
rl1 = RouteLayer(encoder=encoder, routes=routes1,llm=model)
