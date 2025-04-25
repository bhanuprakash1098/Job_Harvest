import os
import re

import pandas as pd
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load your OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")


def evaluate_job_matches(jobs_df, resume_text):
    """
        Evaluates how well a given resume matches each job listing in a DataFrame using OpenAI embeddings and GPT-4o.
        Returns a new DataFrame with match percentage, skill gaps, and resume tailoring suggestions.
        """
    # -------------------------------
    # STEP 1: Split the resume into overlapping text chunks for better vector representation
    # -------------------------------
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len
    )
    resume_chunks = text_splitter.split_text(resume_text)

    # -------------------------------
    # STEP 2: Embed the resume chunks into a FAISS vector store using OpenAI embeddings
    # -------------------------------
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    docsearch = FAISS.from_texts(resume_chunks, embeddings)

    # -------------------------------
    # STEP 3: Load the LLM (ChatOpenAI using GPT-4o) and QA chain
    # -------------------------------
    llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
    chain = load_qa_chain(llm, chain_type="stuff")

    results = []

    # -------------------------------
    # STEP 4: Iterate over each job listing in the DataFrame
    # -------------------------------
    for _, row in jobs_df.iterrows():
        # Create a textual context using job metadata and description
        job_context = (
            f"Platform: {row['Platform']}\n"
            f"Job Title: {row['Job Title']}\n"
            f"Company: {row['Company']}\n"
            f"Location: {row['Location']}\n"
            f"Job Description: {row['Job Description']}\n"
            f"Job URL: {row['Job URL']}\n"
        )

        # -------------------------------
        # STEP 5: Perform vector similarity search against the resume chunks
        # -------------------------------
        docs = docsearch.similarity_search(job_context)

        # -------------------------------
        # STEP 6: Ask the LLM to evaluate the match between resume and job
        # -------------------------------
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

        # -------------------------------
        # STEP 7: Extract structured data (match %, skill gaps, suggestions) from LLM output
        # -------------------------------
        response_text = response["output_text"].strip()

        # Use regex to extract structured data from LLM response
        match = re.search(r"1\.\s*([\d.]+)", response_text)
        skills = re.search(r"2\.\s*(.*)", response_text)
        suggestions = re.search(r"3\.\s*(.*)", response_text)

        match_percentage = float(match.group(1)) if match else 0.0
        missing_skills = skills.group(1).strip() if skills else "Could not extract skills"
        tailoring_suggestions = suggestions.group(1).strip() if suggestions else "Could not extract suggestions"

        # Store results for each job
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

    # -------------------------------
    # STEP 8: Convert all evaluation results into a DataFrame
    # -------------------------------
    match_df = pd.DataFrame(results)
    return match_df
