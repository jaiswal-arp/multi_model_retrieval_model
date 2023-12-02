import snowflake.connector
from dotenv import load_dotenv
import os
import streamlit as st
import shutil
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from llama_index.indices.multi_modal.base import MultiModalVectorStoreIndex
from llama_index.vector_stores import QdrantVectorStore
from llama_index import SimpleDirectoryReader, StorageContext
import qdrant_client
from llama_index import (
    SimpleDirectoryReader,
)

load_dotenv()

st.title('Edhoti')

snowflake_connection_params = {
    'user': os.environ.get("snowflake_user"),
    'password': os.environ.get("snowflake_password"),
    'account': os.environ.get("snowflake_account"),
    'warehouse': os.environ.get("snowflake_warehouse"),
    'database': os.environ.get("annotations"),
    'schema': os.environ.get("snowflake_schema"),
}

conn = snowflake.connector.connect(**snowflake_connection_params)

query = "SELECT image, response_content FROM annotations.public.annotations"
cursor = conn.cursor()
cursor.execute(query)

image_data = cursor.fetchall()

# aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
# s3_bucket_name = 'fashionimages05'

existing_images_directory = Path("./Images")

mixed_wiki_directory = Path("mixed_wiki")
mixed_wiki_directory.mkdir(exist_ok=True)

def fetch_annotations(image_path):

    query = f"SELECT response_content FROM annotations.public.annotations WHERE image = 'https://fashionimages05.s3.amazonaws.com/{image_path}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0] if result else None

def process_directory(directory):
    for item in directory.iterdir():
        if item.is_dir():
            process_directory(item)
        elif item.suffix.lower() in {".jpg", ".png", ".svg"}:
            image = Image.open(item)

            image_path = item.relative_to(existing_images_directory)
            image_path = str(image_path)
            image_path_updated = image_path.replace("/", "_")
            image_path_updated = image_path_updated.replace(".jpg", "")

            image_copy_path = mixed_wiki_directory / f"{image_path_updated}.jpg"
            image_copy_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, image_copy_path)


            print(image_path_updated)

            annotations = fetch_annotations(str(image_path))

            mixed_wiki_file_path = mixed_wiki_directory / f"{image_path_updated}.txt"

            with open(mixed_wiki_file_path, "w") as mixed_wiki_file:
                mixed_wiki_file.write(f"Annotations: {annotations}\n")

# process_directory(existing_images_directory)

conn.close()

@st.cache(allow_output_mutation=True)
def initialize_qdrant_client():
    client = qdrant_client.QdrantClient(path = 'qdrant_mm_db')
    return client


text_store = QdrantVectorStore(
    client=initialize_qdrant_client(), collection_name="text_collection"
)

image_store = QdrantVectorStore(
    client=initialize_qdrant_client(), collection_name="image_collection"
)

storage_context = StorageContext.from_defaults(vector_store=text_store)

documents = SimpleDirectoryReader("./mixed_wiki/").load_data()

index = MultiModalVectorStoreIndex.from_documents(
    documents, storage_context=storage_context, image_vector_store=image_store
)

tab1, tab2 = st.tabs(['Text', 'Upload'])
with tab1:
    retriever_engine = index.as_retriever(
        similarity_top_k=1, image_similarity_top_k=1
    )
    texttt = st.text_input("Enter a text to search similar images", key = "text1")
    if texttt:
        retrieval_results = retriever_engine.retrieve(texttt)
        # st.write(retrieval_results)
        from llama_index.response.notebook_utils import display_source_node
        from llama_index.schema import ImageNode, TextNode

        retrieved_image = []
        for res_node in retrieval_results:
            if isinstance(res_node.node, ImageNode):
                retrieved_image.append(res_node.node.metadata["file_path"])
            elif isinstance(res_node.node, TextNode):
                file_path =  res_node.node.metadata["file_path"]
                file_path = file_path.replace(".txt", ".jpg")
                retrieved_image.append(file_path)
            else:
                display_source_node(res_node, source_length=200)

        for i in retrieved_image:
            st.image(i, caption='Your Image', use_column_width=True)
with tab2:
    retriever_engine1 = index.as_retriever(image_similarity_top_k=1)
    texttt = st.text_input("Enter a text to search similar images", key="text2")
    if texttt:
        retrieval_results1 = retriever_engine1.image_to_image_retrieve(
            texttt
        )
        st.write(retrieval_results1)
        retrieved_images = []
        for res in retrieval_results1:
            retrieved_images.append(res.node.metadata["file_path"])

        for i in retrieved_images:
            st.image(i, caption='Your Image', use_column_width=True)