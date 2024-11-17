# Diet Plan Recommendation For Chronic Health Conditions using LLM and RAG
This project is an AI based chatbot for diet plan recommendation created to detect and manage chronic health conditions mainly focusing on Thyroid, Diabetes and Heart disease.
## Input
The input is symptom or disease. Predict the chronic health conditions if any based on symptoms/disease provided and suggest diet plans for user. 
## Dataset
The dataset for this project are research papers available in Google Scholar and PubMed. We collected research papers on diet plan recommendation and disease prediction from these websites. We also collected foundation food data from USDA Food data central site. This project repository contains sample data folder with foundation food data and research papers. Follow the same folder structure (data/) when adding more data.
## Implementation
This project is implemented using open source LLM and RAG. We have used LLAMA 3.1 8b model to generate responses. When user sends a query, internally we query the vector database to predict disease and generate diet plans using diet plan vector db as retriever and LLAMA LLM.

# Steps to run this project
