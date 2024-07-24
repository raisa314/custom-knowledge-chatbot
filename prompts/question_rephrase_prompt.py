regeneration_template = """
Given the previous conversation history and a follow up question, 
provide the rephrased question translated into {target_language} as output.

Rephrase the given question to be a standalone question.\

Conditions for rephrasing:
    1. Make sure to return the standalone question in the target language.  
    2. If the question is not related to the previous questions, then you must keep the question same as it is.
    3. You must use chat history if the current question is related to the previous questions. If the current question has the requirements (product/feature/details/url) and name/code mentioned, do not change the requirement or product name/code.
    4. If the user question mention any keywords like 'this'/'it', then you should rephrase the current question with last question in chat history.
    5. If any question mentions 'you'/'your', they are talking about Nikles as you. Rephrase the question accordingly with 'Nikles' mentioned in the question.
    6. If the question is about install,instruction manual , setup , or how to use the product 'X' then use this question Give me instruction manual of the product 'X'.
    7. If the user only gives u a product code 'X' then use this Give me instruction manual of 'X'.
Chat History: {chat_history}
Follow up question: {question}

You must return one variables, `Standalone question`.    
    
    Examples:
    
        Input: 'Hi'
        Output: 'Standalone question: Hi'      
  
        Input: 'Bye'
        Output: 'Standalone question: Bye'
        
        Input: 'Bye'
        Output: 'Standalone question: Bye'

        Input: 'Thanks'
        Output: 'Standalone question: Thanks'
    
        Input: 'Quali sono le sue caratteristiche?'
        Output: 'Standalone question: Quali sono le caratteristiche del prodotto KIT SYSTEM 1 TELESCOPICO CROMO?'

        Input: 'How many colors are available in the Nikles Luxury Finish?'
        Output: 'Standalone question: How many colors are available in the Nikles Luxury Finish?'

        Input: 'What are the colors available in this series?'
        Output: 'Standalone question: What are the colors available in Nikles Luxury Finish series?'
        
        Input: 'Can you show me the details of the product with this code?'
        Output: 'Standalone question: Can you show me the details of the product with the code 'BLS.001.07N'?'        
        
        Input: 'Which products do you have on your ECO Line?' 
        Output: 'Standalone question: Which products are in the Nikles ECO Line?'

        Input: 'show me the product with the code G000105N'
        Output: 'Standalone question: show me the product with the code G000105N'
        
        Input: 'how to install  HAND SHOWER NOVA ROUND 120 3S SWIRL ECO CHROME '
        Output: 'Standalone question: Give me the instruction manual of HAND SHOWER NOVA ROUND 120 3S SWIRL ECO CHROME '
        
        Input: 'how to setup HAND SHOWER NOVA ROUND 120 3S SWIRL ECO CHROME '
        Output: 'Standalone question: Give me the instruction manual of HAND SHOWER NOVA ROUND 120 3S SWIRL ECO CHROME ' 
        
        Input: 'how to use A48.C10.000.05N'
        Output: 'Standalone question: Give me the instruction manual of A48.C10.000.05N' 
        
        Input: 'How do I install my product: A48.C10.000.05N'
        Output: 'Standalone question: Give me the instruction manual of A48.C10.000.05N' 
        
        Input: 'what products do you have?'
        Output: 'Standalone question: what products does nikles offer' 
        
        Input: 'How do I care for my  HAND SHOWER AVANTI 110 DUO CHROME? '
        Output: 'Standalone question: Give me the instruction manual of HAND SHOWER AVANTI 110 DUO CHROME' 
        
        Input: 'D3605F'
        Output: 'Standalone question: Give me the instruction manual of D3605F' 
        
        Input: 'A48.C10.000.05N'
        Output: 'Standalone question: Give me the instruction manual of A48.C10.000.05N' 
          
    """