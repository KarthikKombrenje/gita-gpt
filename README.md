Goal:-

Gita-GPT is a self-help chatbot that gives suggestions based on verses and commentaries from the Bhagavad Gita by various gurus.

Input:- 

1. PDFs of the Bhagavad Gita are embedded

2. Text is extracted from the PDFs

3. The text is split into chunks

4. Each chunk is converted into embeddings using OpenAI API

5. Embeddings are stored in ChromaDB (vector database)

Output:- 

1. User enters a prompt

2. Prompt is matched with the closest chunks from ChromaDB

3. Matching chunks + user prompt = final input to OpenAI API

4. Response is generated based on that context

