Goal:-

Gita-GPT is a self-help chatbot that gives suggestions based on verses and commentaries from the Bhagavad Gita by various gurus.

**Input:- **

PDFs of the Bhagavad Gita are embedded

Text is extracted from the PDFs

The text is split into chunks

Each chunk is converted into embeddings using OpenAI API

Embeddings are stored in ChromaDB (vector database)

**Output:- **

User enters a prompt

Prompt is matched with the closest chunks from ChromaDB

Matching chunks + user prompt = final input to OpenAI API

Response is generated based on that context

**To run the project :- **

Navigate to the project directory

Remove any old venv or Python 3.8 leftovers rm -rf venv rm -rf pycache rm -rf ~/.local/lib/python3.8 || mv ~/.local/lib/python3.8 ~/.local/lib/python3.8.bak

Create a new Python 3.11 virtual environment /usr/local/python311-custom/bin/python3.11 -m venv venv

Activate the virtual environment source venv/bin/activate

Upgrade pip (important) pip install --upgrade pip

Clear pip cache to avoid old Python 3.8 wheels pip cache purge

Install dependencies inside venv only

pip install fastapi uvicorn

pip install PyPDF2

pip install nltk && python -c "import nltk; nltk.download('punkt')"

pip install tiktoken

pip install sqlite-utils

pip install --no-cache-dir chromadb

pip install pydantic

pip install typing-extensions

pip install openai

pip install python-multipart

pip install sqlalchemy passlib[bcrypt] databases

After installing dependencies please run the project using the command:- uvicorn main:app --reload

Sample curls to be hit on Postman:-

curl --location 'http://localhost:8000/api/chat'
--header 'Content-Type: application/json'
--data '{ "question":"what is life" }'

curl --location 'http://localhost:8000/api/embed'
--form 'pdf_files=@"/home/karthik/Downloads/SOLVED-Values-Guide.pdf"'