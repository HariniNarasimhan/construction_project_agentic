---
title: "Problem 2: An Agentic Architecture for Construction Meeting Intelligence"
layout: default
---
Modern construction projects generate and rely on a large volume of documentation — from **tenders**, **bids**, to the **final signed contracts**. Once construction begins, **stakeholder meetings** are held regularly via platforms like **Microsoft Teams** and **Zoom**.

> The task: Design a software architecture for an intelligent agent that participates in these meetings, listens to discussions, observes screen shares or visual content, and cross-verifies conversations against the official project documents.

---

### 🎯 Agent Objectives

The AI meeting agent is designed to:

1. 🧾 **Identify contractual discussions**: Detect when topics in the meeting relate to clauses or requirements in the signed contract.
2. ❗ **Validate alignment**: Confirm whether discussed items are already documented or require additions/changes.
3. ✍️ **Propose changes**: If additional work is discussed, the agent should suggest:
   - Amendments to existing contracts/specifications
   - Creation of **new contracts** or **addenda**

---
### 🔧 Tech stack

- **Cloud platform** - AWS
- **Language** - Python
- **Services** - AWS S3, AWS Lambda, AWS EventBridge, AWS SQS, Amazon SageMaker, Amazon Bedrock, Amazon OpenSearch Service, AWS EKS
- **Other tools** - MCP servers

#### 💡 AI Stack
- **LLM**: GPT-4 / Claude / Azure OpenAI / Bedrock
- **Embeddings**: OpenAI / Cohere / HuggingFace / Bedrock
- **Vector DB**: Opensource (FAISS / Weaviate / Pinecone) / AWS Opnsearch
- **Agent**: LangChain / Autogen


### 🧱 Proposed Solution Architecture
An application deploying infrastructure for a generative AI cross-platform online meeting insights agent. The agent is designed to be compatible with online meeting apps such as Microsoft Teams, Zoom, etc 
![Post-meeting-architecture](/assets/post-meeting-architecture.png)



## 📂 **Document Ingestion & Knowledge Base**
![Data-ingestion](/assets/data-ingestion.png)

Once the construction project is signed -  the final contract, tenders and bids are uploaded to S3 bucket. This triggers a Lambda function **documents-to-text**
- **Documents-to-text** - is responsible for fetching the document files from s3 such as pdf, excel and word documents. The content of the files are converted to text using OCR techniques like [Amazon textract](https://aws.amazon.com/textract/) / [Mistral OCR](https://mistral.ai/news/mistral-ocr). These text files are then saved in s3 under processed-files. For every new file created, the object file is pushed to an SQS queue.
- **SQS Queue** - The SQS queue is used for decoupling producer (**Documents-to-text**) and consumer (**text-to-embeddings**) Because if the embedding function is slow, fails, or needs to be updated, the **document-to-text** pipeline can still proceed. This allows independent scaling, error handling, and maintenance. It also enables us to implement retry and failure recovery if the **text-to-embedding** Lambda fails (e.g., due to API/model issues), SQS can retry automatically or send the message to a **dead-letter queue (DLQ)**. The s3 object files information pushed to SQS Queue is consumed by **text-to-embeddings** lambda.
- **Text-to-embeddings** - Read the processed s3 text files and implements a chunking mechanism to parse the text files and create embedding using models from **Sagemaker jumpstart / Huggingface models** and store these embedding as vector database in **AWS Opensearch service index** (can also use opensource DB like [cromadb](https://www.trychroma.com/). 

## 🛠️ **Meeting Agent Trigger**
![Meeting-Agent-Trigger](/assets/email-domain.png)

Meeting Agent is backed by a mail account with necessary license to schedule and manage meetings.
To monitor this mail account, a **Event bridge scheduler** is used to trigger the lambda **check-email** which keeps checking the receiving email and if the email is a meeting invite, then the **AI Agent** is triggered with new meeting information.
The trigger to **AI Agent** would contain the following information.
* construction project name (the knowlegdebase of that project should be available in VectorDB)
* Meeting id to join
* Meeting date and time

## 🧠 **Agentic Workflow**
![Agentic-Workflow](/assets/agentic-workflow.png)

We have an AI agent created using **Autogen/Langchain framework** where the prompt engineering is performed with any LLM to integrate with MCP tools. 
The stakeholders of this construction project can add this agent using it's **email id** and make sure all the access is given for the agent mail id to access meeting contents.
The Agent will set with **system prompts** to perform the necessary tasks. To interact with Agent, A **FastAPI** WebSocket protocol, initiated via an HTTP GET request with an ```Upgrade: websocket``` header. Once the connection is established, it switches to the WebSocket protocol. This API is hosted using **AWS EKS**.

## 🛠️ **MCP servers**
![MCP-Servers](/assets/mcp-servers.png)

The tools created for mcp servers can also be hosted as GET/POST methods using FastAPI depending on the use case. These http urls are connected to Agents to trigger the right tool.

**Meeting Tools**

🔹 Join Meeting

When the agent's email receives a meeting invite related to a construction project, the tool sets up an **Amazon EventBridge Scheduler**.  
This scheduler is configured to trigger the `check-recording` Lambda function **every 15 minutes**, starting from the meeting's scheduled **end time**.
   
   `check-recording` Lambda - This function checks the agent's inbox for an email that confirms the availability of the meeting recording.
   - ✅ **If the email is found** (indicating the recording file is ready):
     - The **EventBridge scheduler is deleted**.
     - The agent is prompted with the message:  
       `"The recording file is ready at: <download-url>. Please fetch and save the transcript and recording."`

   - ❌ **If the email is not yet received**:
     - The function continues to poll the inbox every 15 minutes until the recording status email is found.

```
Input: { "meeting title" <value>, "construction_project_name": <value>, "antendeed mail id": <value>, "meeting_start_date_time": <value>, "meeting_end_date_time": <value>}
Output: <Event bridge creation status>
```

🔹 Fetch and Save recordings / transcripts 

Using the Recording download url from `check-recording` lambda, the recordings and transcripts are fetched and stored in s3 ( transcripts are saved as text files. Recordings as saved as mp4)

```
Input: <Download url of recording and transcripts>
Output: <S3 path of  recording and transcripts>
```

🔹 Retrieve contract data 

A `SageMaker endpoint` is deployed to handle intelligent document understanding and contract validation. The process includes:

1. Transcript Ingestion & Classification
   - Transcript text files are fetched from **Amazon S3**.
   - The transcripts are **chunked** and each chunk is classified as:
     - `📁 Project Related`
     - `📁 Non-Project Related`

2. Semantic Search & Retrieval
   - For all `Project Related` chunks:
     - The system retrieves the **Top-K relevant information** from the **project documents** (contracts, tenders, bids).
     - ✅ **If relevant data is retrieved**:
        - The chunk + Top-K retrieved content is passed as **context** to the **LLM**.
        - The LLM generates a **summary** of that part of the meeting.
        - The summary includes **references to line numbers** in the original contract, bid, or tender documents.
     - ❌ **If no relevant information is found**:
        - The summary for that chunk remains **empty**.
     - Based on the **timestamp** in the transcript, the corresponding **frame from the meeting recording** is extracted and saved.

All the necessary information is stored in a nosql database like **Dynamodb**. 
```
{ “meeting_id”: <value>,
“data” : [
{“chunk_id”: <value>,
“contract summary”: <value> ,
“document line number”: <value>,
“recording_image”: <s3 path>,
“meeting_context”: <value>]}
```

🔹 Meeting Insights

Use the `meeting_id` to retrieve data from the **Knowledge Base**.

- ✅ **If `contract_summary` and `line_numbers` are available**:  
  - Extract a **list of discussion points** based on the summarized content.

- ❌ **If `contract_summary` is empty**:  
  - Use the available `meeting_context` to generate a **list of suggestions** for potential changes or additions to the **project documents**.


🔹 Send Insights to Meeting Chat

Once insights are generated,
- Use the **Meeting App API** to post the insights directly into the **meeting chat** for stakeholder visibility and follow-up.
  
## Benefits of this solution:
✅ **Compatibility with any online meeting apps** - AI agent backed by a mail-id is easy to participate in any Meeting apps.
✅ **Faster testing with different LLMs and Embedding models** - Using an agent based approach can help us test with multiple available LLMs and observe the results
✅ **Observability**: With autogen/langchain based agents, we can track cost, prompts, tokens and MCP tool tigger events.
✅ **Creation of meeting knowledge base**: A knowledge base is created based on the construction project documents and the meeting - which can help the user to interact with the meeting knowledge base for more insights.

## 🧠 Bonus Task

A minor but impactful optimization has been introduced to support **live transcription** and enable **faster AI agent responses**. Most modern meeting platforms (e.g., Zoom, Teams) provide live transcription updates when participants pause during speech. The architecture has been updated to accommodate this in near real-time.

The updated design improves the following areas:

- **📝 On Meeting Transcription Data**  
  - Continuously ingests and processes live transcript segments.
  - Enables incremental reasoning by the agent as the meeting progresses.

- **🤖 Real-Time Interaction with AI Agent**  
  - Users can **chat with the AI agent** during the meeting to query insights on ongoing discussions.

- **⚡ Post-Meeting Fast Insights**  
  - Speeds up post-processing by **filtering out non-contract-related content** (e.g., greetings, casual chit-chat).
  - Focuses the LLM summarization pipeline only on meaningful project-related conversations.


![Architecture](/assets/bonus-architecture.png)

**Changes made**

⏰ 1. EventBridge Scheduler Enhancement
- The **Join Meeting EventBridge Scheduler** is now triggered **at the start of the meeting**.
- This enables early access to both the **meeting chat** and **live transcription window** updates.

🧠 2. Real-Time Transcript Processing with RAG
- With each **live transcript update**, the Agent uses the `process_transcripts` tool only for **project-related conversations**.:
  - Implements **Retrieval-Augmented Generation (RAG)** using the **Contract database**.
  - Saves the relevant transcript chunks to a **NoSQL database** for fast querying.

📼 3. Post-Meeting Recording Ingestion
- Since recordings become available only **after the meeting ends**, a `"Recording Ready"` message is posted to the **meeting chat** by meeting apps. This message triggers the agent to:
  - **Fetch the recording**.
  - Update the frames of the transcript in the **Knowledge Base**.

🤖 4. AI Agent as an Active Participant
- The AI agent, acting as a **participant in the meeting chat**, supports attendees by:
  - Answering **contextual queries** once the **Knowledge Base** is ready.
  - Sharing real-time or post-meeting **insights** automatically with all participants.
