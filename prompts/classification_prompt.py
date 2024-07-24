classification_template = """
Given the user question, provide the response source classification as  output.

Your task is to classify the question it as either to be responded from `sql` or `pdf` resource.\

Conditions for classification:
    1. If user question is about any information of any product (like product image, description or details or features, categories, url, code),
    the question should be answered from `sql`.
    2. If user question doesn't specify the exact product name , product code or product category, classify the question to be answered from `pdf`.
    3. If the question is about flow rate ,size,colors or description of any product, the question should be answered from `pdf`. 
    4. If the user ask question about the company, warranty, other descriptive information (Nikles Eco, Nikles Luxury, Technology)- the question should be answered from `pdf`. 
    5. If the user ask any generic greetings, kepp the question same and classify as to be answered from `pdf`. 
    6. If user is specifically mentioning any product name or product code, you must answer it from `sql`.
    7. If the user asks for list of products mentioning any product category or tag or label, classify the question to be answered from `sql`. If product category is not mentioned, classify as `pdf`.

User question: {question}

You must return one variable, `Classification`.
Do not respond with more than one word for the response classification.
    
    Examples:
        Input: 'Hello'
        Output: 'Classification: pdf'

        Input: 'Quali sono le caratteristiche del prodotto KIT SYSTEM 1 TELESCOPICO CROMO?'
        Output: 'Classification: sql'

        Input: 'How many colors are available in the Nikles Luxury Finish?'
        Output: 'Classification: pdf'

        Input: 'What are the colors available in Nikles Luxury Finish series?'
        Output: 'Classification: pdf'

        Input: 'Wat is het debiet van HANDDOUCHE AVANTI ROND 120 UNO ECO CHROME?'
        Output: 'Classification: sql'
        
        Input: 'Can you tell me about product KIT SYSTEM 1 TELESCOPIC CHROME?'
        Output: 'Classification: sql'
        
        Input: 'Can you show me the details of the product with the code BLS.001.07N ?'
        Output: 'Classification: sql'        
        
        Input: 'Thanks'
        Output: 'Classification: pdf'

        Input: 'Which products do you have on the ECO Line?' 
        Output: 'Classification: sql'
        
        Input: 'do you sell water saving showers?' 
        Output: 'Classification: pdf'
        
        Input: 'what sizes do you have in hand showers?' 
        Output: 'Classification: pdf'
                
        Input: 'give me the url of the product with the code BLS.001.07N ?' 
        Output: 'Classification: sql'
        
            
        
    """
