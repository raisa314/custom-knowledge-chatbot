from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import re
from utils.logger import logger
from dotenv import dotenv_values
import datetime
from utils.prod_data_process import concatenate_row_values, df_to_pdf, remove_old_pdfs

config = dotenv_values(".env")
mysql_connector=config['MYSQL_CONNECTOR']
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

def create_tables():
    DATABASE_URL = mysql_connector
    engine = create_engine(DATABASE_URL)
    
    sql_commands = [
        """DROP TABLE IF EXISTS cb_products;""",
        """
        CREATE TABLE IF NOT EXISTS cb_history (
            query_id INT AUTO_INCREMENT PRIMARY KEY,
            session_id CHAR(36) NOT NULL,
            user_question VARCHAR(255) NOT NULL,
            bot_response TEXT NULL,
            query_time DATETIME NOT NULL,
            cost FLOAT NOT NULL,
            feedback TINYINT(1) NULL,
            response_source VARCHAR(255) NULL,
            response_type VARCHAR(255) NULL
        );
        """,
        """
        CREATE TABLE cb_products (
            ID BIGINT UNSIGNED PRIMARY KEY,
            code VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
            name TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            description TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            image_url TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            category_names TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            category_label TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            tag_names TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            FULLTEXT(name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS cb_manuals (
            code VARCHAR(255) NOT NULL,
            name_description VARCHAR(255) NOT NULL,
            installation_file VARCHAR(255) NULL,
            maintenance_file VARCHAR(255) NULL,
            yt_link VARCHAR(255) NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS cb_kb_index (
            category VARCHAR(255) NOT NULL,
            pdf_link VARCHAR(255) NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    try:
        # Execute each SQL command within a database connection context
        with engine.connect() as conn:
            for command in sql_commands:
                conn.execute(text(command))
                logger.info("Executed SQL command.")
    except SQLAlchemyError as e:
        logger.info(f"An error occurred: {e}")

def clean_text(text):
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text()
    clean_text = re.sub(r'\b[A-Za-z0-9.-]+\r\n', '', clean_text).strip()
    
    return clean_text

def product_data():
    DATABASE_URL = mysql_connector
    
    # Establishing the database connection
    engine = create_engine(DATABASE_URL)
    query = """SELECT
                    p.ID as `ID`,
                    CASE
                        WHEN m1.meta_value IS NULL THEN
                            SUBSTRING_INDEX(SUBSTRING_INDEX(p.post_content, '\n', 1), ':', -1)
                        ELSE
                            m1.meta_value
                    END AS `code`,
                    p.post_title AS `name`,
                    p.post_content AS `description`,
                    CONCAT_WS('/', 'https://www.nikles.com/product', p.post_name) AS `url`,
                    CONCAT_WS('/', 'https://www.nikles.com', CONCAT('wp-content/uploads/', im1.meta_value)) AS `image_url`,
                    cat_data.parent_term_name AS category_names,
                    cat_data.child_term_name AS category_label,
                    tag_data.tag_names
                FROM
                    wp_posts p
                LEFT JOIN
                    wp_postmeta m1 ON p.ID = m1.post_id AND m1.meta_key = '_sku'
                LEFT JOIN
                    wp_postmeta m2 ON p.ID = m2.post_id AND m2.meta_key = '_thumbnail_id'
                LEFT JOIN
                    wp_postmeta im1 ON m2.meta_value = im1.post_id AND im1.meta_key = '_wp_attached_file'
                LEFT JOIN (
                    SELECT
                        tr.object_id AS ID,
                        MAX(COALESCE(parent.name, child.name)) AS parent_term_name,
                        MAX(CASE WHEN parent.name IS NULL THEN NULL ELSE child.name END) AS child_term_name
                    FROM
                        wp_term_relationships tr
                    INNER JOIN
                        wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
                    INNER JOIN
                        wp_terms child ON tt.term_id = child.term_id
                    LEFT JOIN
                        wp_terms parent ON tt.parent = parent.term_id
                    WHERE
                        tt.taxonomy = 'product_cat'
                    GROUP BY
                        tr.object_id
                ) AS cat_data ON p.ID = cat_data.ID
                LEFT JOIN (
                    SELECT
                        tr.object_id AS ID,
                        GROUP_CONCAT(DISTINCT tag.name ORDER BY tag.name SEPARATOR ', ') AS tag_names
                    FROM
                        wp_term_relationships tr
                    INNER JOIN
                        wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
                    INNER JOIN
                        wp_terms tag ON tt.term_id = tag.term_id
                    WHERE
                        tt.taxonomy = 'product_tag'
                    GROUP BY
                        tr.object_id
                ) AS tag_data ON p.ID = tag_data.ID
                WHERE
                    p.post_type = 'product'
                    AND p.post_status = 'publish'
                ORDER BY
                    p.post_date;
            """

    # Fetching the data
    raw_data = pd.read_sql(query, engine)    
    logger.info("Labrnicag_wordpress product data fetched.")

    # Clean and translate the text
    raw_data['name'] = raw_data['name'] 
    raw_data['description'] = raw_data['description'].apply(clean_text)

    processed_data = raw_data.drop_duplicates(subset=['code'])

    processed_data.to_sql('cb_products', engine, if_exists='append', index=False)   

    prod_df = processed_data.copy()
    directory = './data/pdf'
    prod_df.loc[:, 'merged_prod_info'] = prod_df.apply(concatenate_row_values, axis=1)
    pdf_filename = f'./data/pdf/merged_sql_data_{formatted_datetime}.pdf'
    remove_old_pdfs(directory, pdf_filename)
    df_to_pdf(prod_df, pdf_filename)
    
    return pdf_filename