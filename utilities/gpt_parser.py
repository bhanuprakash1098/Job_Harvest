import os
import re

import pandas as pd
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")


def evaluate_job_matches(jobs_df, resume_text):
    # Split resume into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    resume_chunks = text_splitter.split_text(resume_text)

    # Create FAISS vector database from resume chunks
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    docsearch = FAISS.from_texts(resume_chunks, embeddings)

    # Set up LLM and chain (use ChatOpenAI for GPT-4 models)
    llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
    chain = load_qa_chain(llm, chain_type="stuff")

    results = []

    # Iterate over each job description
    for _, row in jobs_df.iterrows():
        job_context = (
            f"Platform: {row['Platform']}\n"
            f"Job Title: {row['Job Title']}\n"
            f"Company: {row['Company']}\n"
            f"Location: {row['Location']}\n"
            f"Job Description: {row['Job Description']}\n"
            f"Job URL: {row['Job URL']}\n"
        )

        # Perform similarity search on resume chunks
        docs = docsearch.similarity_search(job_context)

        # Use LLM to evaluate match percentage, missing skills, and suggestions
        prompt_query = (
            "Evaluate the relevance of the provided resume (in chunks) to the following job description.\n\n"
            "Return the following outputs strictly in this order:\n"
            "1. **Match Percentage** (only a number between 0-100, no extra text).\n"
            "2. **Skill Gaps** (a comma-separated list of missing or weak skills).\n"
            "3. **Resume Tailoring Suggestions** (a brief but detailed recommendation on how to tailor the resume for this job).\n\n"
            f"{job_context}"
        )

        response = chain.invoke({
            "input_documents": docs,
            "question": prompt_query
        })

        # Extract response text
        response_text = response["output_text"].strip()

        # Use regex to extract structured data from LLM response
        match = re.search(r"1\.\s*([\d.]+)", response_text)
        skills = re.search(r"2\.\s*(.*)", response_text)
        suggestions = re.search(r"3\.\s*(.*)", response_text)

        match_percentage = float(match.group(1)) if match else 0.0
        missing_skills = skills.group(1).strip() if skills else "Could not extract skills"
        tailoring_suggestions = suggestions.group(1).strip() if suggestions else "Could not extract suggestions"

        # Collect result
        results.append({
            "Platform": row["Platform"],
            "Job Title": row["Job Title"],
            "Company": row["Company"],
            "Location": row["Location"],
            "Job Description": row["Job Description"],
            "Job URL": row["Job URL"],
            "Match Percentage": match_percentage,
            "Skill Gaps": missing_skills,
            "Resume Tailoring Suggestions": tailoring_suggestions
        })

    # Convert results to DataFrame
    match_df = pd.DataFrame(results)
    return match_df
