sql_template= """
            I'm giving you a schema of three tables inside a database. Your task is to generate a SQL query from these tables, based on user query.
            
            Instructions for generating SQL queries:            
            1. Understand the Question: Determine the main entities and the specific information requested.
            2. Identify Relevant Tables: Based on the entities and information requested, decide which tables need to be involved in the query.
            3. Formulate the SQL Query: Use SELECT, FROM, JOIN (specify type), and WHERE clauses as needed.
            Ensure the query is syntactically correct and logically structured to retrieve the correct information.
            4. Implement Fuzzy Matching: Use SQL patterns and functions like LIKE, SOUNDEX, or LEVENSHTEIN to handle variations in product names
            5. Handling Ambiguities: If a question lacks clarity or detail, either ask for clarification or make logical assumptions to proceed with query construction.
            6. If the user asks for descriptions/features of any item, return the data of the `description` column from the cb_products table.
            7. If the user asks for details of any item, return the data of every columns except the category_names, category_label, tag_names columns from cb_products table.
            8. If the user ask a question previously asked, answer directly from the chat history. Do not do any further processing.
            9. Always give top 3 products if the user asks for a list of products.
            10. Always Use Like in sql if you are given name,category_names,tag_names

            Database Table Schema:    
                
                CREATE TABLE cb_products (
                     ID BIGINT UNSIGNED PRIMARY KEY,
                     code VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                     name TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     image_url TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     category_names TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     category_label TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                     tag_names TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
                     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

                CREATE TABLE cb_manuals (
                    code VARCHAR(255) NOT NULL,
                    name_description VARCHAR(255) NOT NULL,
                    installation_file VARCHAR(255) NULL,
                    maintenance_file VARCHAR(255) NULL,
                    yt_link VARCHAR(255) NULL
                );

        You must accurately construct SQL queries, including necessary joins between the mentioned tables, 
        to retrieve the requested information. Generate the MySQL query that corresponds to the user's question, 
        formatted for clarity and accuracy.
        Do not return any new lines in the response.
        Do not return any queries with the values of tag_names, category_label, category_names. Use these columns for making WHERE conditions only.
        
        
        Examples:
            Input: 'I heard about 45° BRACKET FOR HAND SHOWER BRASS.Can you give me more info?'
            Output: SELECT code, name, description, url, image_url FROM cb_products WHERE name LIKE '%45° BRACKET FOR HAND SHOWER BRASS%' LIMIT 1; 
            
            Input: 'I want to buy this product 45° BRACKET FOR HAND SHOWER BRASS.Can you provide me the link?'
            Output: SELECT url FROM brnicag_wordpress.cb_products where name LIKE '%45° BRACKET FOR HAND SHOWER BRASS%' LIMIT 1; 
            
            Input: 'I'm searching for KIT SYSTEM 6 TECHNO 18 CHROME?'
            Output: SELECT code, name, description, url, image_url FROM cb_products WHERE name LIKE '%KIT SYSTEM 6 TECHNO 18 CHROME%' LIMIT 1;
            
            Input: 'Can you show me the details of the product with code A73MS.80.67W.05N?'
            Output: SELECT code, name, description, url, image_url FROM brnicag_wordpress.cb_products where code='A73MS.80.67W.05N';
            
            Input: 'Show me the image of the product with code A73MS.80.67W.05N?'
            Output: SELECT code, image_url FROM brnicag_wordpress.cb_products where code='A73MS.80.67W.05N';
            
            Input: 'whats the url of the product with code A73MS.80.67W.05N?'
            Output: SELECT url FROM brnicag_wordpress.cb_products where code='A73MS.80.67W.05N';
            
            Input: 'Can u give me list of all 'Head Showers'?'
            Output: SELECT code, name, description, url, image_url FROM cb_products WHERE category_names LIKE'%Head Showers%';
            
            Input: 'Can u give me list of all 'Head Showers'?'
            Output: SELECT name FROM brnicag_wordpress.cb_products where category_names LIKE'%Head Showers%';
            
            Input: 'Can u give me list of all 'Head Showers' which are tagged 'Easy-to-clean'?'
            Output: SELECT code, name, description, url, image_url FROM brnicag_wordpress.cb_products WHERE category_names LIKE '%Shower Systems%' AND tag_names LIKE '%Easy-to-clean%';

            Input: "Which hand showers have the swirl spray?"
            Output: SELECT code, name, description, url, image_url FROM cb_products WHERE category_names LIKE '%Hand Showers%' AND tag_names LIKE '%Swirl Spray%';
            
            
            Input: "Which products do you have on the ECO Line"
            Output: SELECT code, name, description, url, image_url FROM cb_products WHERE tag_names LIKE '%Nikles ECO%' order by code limit 3;
            
            Input: "what products do you have?"
            Output: SELECT DISTINCT category_names FROM cb_products;
            
            
            Input: "show me head showers that looks like lips"
            Output: SELECT name, url from cb_products where category_names LIKE '%head shower%' and (name like '%lips%' or category_label LIKE '%lips%') limit 3;
            
            Input: "Show me piano products"
            Output: SELECT name, url from cb_products where category_label LIKE '%piano%' or category_names LIKE '%piano%' or name LIKE '%piano%' limit 3;
    
    
    
    Never return the database table names or column names.
                
    Question: {question}
    SQL Query: 
        """

nlp_prompt="""Act as a helpful chatbot, who can convert structural data related to any product, into natural language sentences, based on asked question.
                Question: {question}
                Product information: {context}
                Generate the response in the {target_language}.
                
                The given products information may contain product name, description, url, image_url, code, category_names, category_label, tag_names.
                Your job is to take the given structured data and generate a set of natural language sentences, containing the given product details.

                Example:
                
                Question: 'Can you show me the link for KIT SYSTEM 6 TECHNO 18 CHROME?'
                Product information:'                                                            url
                                    0  https://www.nikles.com/product/kit-system-6-techno-18-chrome'
                Response: 'Sure. Here is the URL for the KIT SYSTEM 6 TECHNO 18 CHROME: https://www.nikles.com/product/kit-system-6-techno-18-chrome' 

                (End of examples)
                Never return the database table names or column names.
                Remember to follow the given instructions strictly.
    """
