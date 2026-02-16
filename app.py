from fastapi import FastAPI, Request, HTTPException
from google import genai
import os
import re
import json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS

app = FastAPI() 
load_dotenv()
key = os.getenv("GEMINI_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any UI to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_json(text):
    # מסיר בלוקים של ```json ... ```
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # מוצא את ה־JSON הראשון שמתחיל ב-{ ומסתיים ב-}
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0).strip()

    raise ValueError("No JSON found in model response")


@app.post("/chat_topic")
async def chat(request: Request):
    data_req = await request.json()
    topic = data_req.get("topic", "")
    prompt = f"""Assume the role of a subject-matter expert.
                Based on the topic provided, construct three well-formulated questions at progressively increasing levels of difficulty:

                Easy: Assess fundamental comprehension (definitions, core principles).
                Medium: Require application, structured reasoning, or multi-step problem solving.
                Hard: Demand rigorous analysis, formal proof, critical evaluation, or synthesis of multiple concepts.

                Additional requirements:
                Questions must be precise, unambiguous, and academically rigorous.
                Do not provide solutions or hints.
                Ensure a clear and meaningful distinction between the three difficulty levels.

                Topic: {topic}

                Return ONLY valid JSON in this exact structure:

                {{
                "easy": "text",
                "medium": "text",
                "hard": "text"
                }}

                with no additional commentary, formatting, or text outside the JSON. The values should be the questions you generate only!
                Your Answer should be in hebrew!
                """
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
       # ניקוי markdown אם קיים
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    #  raw = response.text.strip()
    # clean = extract_json(raw)
    # data = json.loads(clean)
    print("RAW:", response)
    print("TEXT:", response.text)

    return {
        "easy": data.get("easy", ""),
        "medium": data.get("medium", ""),
        "hard": data.get("hard", "")
    }


@app.post("/chat_answers")
async def chat(request: Request):
    data_req = await request.json()
    topic = data_req.get("question", "answer")
    prompt = f"""You are an objective and professional evaluator.
                I will provide a question and a student’s answer.
                
                Your task is to evaluate whether the answer successfully addresses the question.
                Evaluation criteria:
                Accuracy and correctness
                Completeness (did it fully answer the question?)
                Clarity and structure
                Depth of explanation (when relevant)
                
                Your response must be returned only in valid JSON format with the following structure:
                {{
                "score": <integer from 0 to 10>,
                "feedback": "<detailed feedback here>"
                }}
                
                Feedback requirements:
                Begin with a brief, respectful compliment about what was done well.
                Maintain a professional, calm, and encouraging tone.
                Clearly explain any mistakes, missing elements, or inaccuracies.
                Provide concrete suggestions for improvement.
                End with a short encouraging sentence.
                Do not include any text outside the JSON.
                Your Answer should be in hebrew!

                Question: {topic.get("question", "")}
                Student Answer: {topic.get("answer", "")}"""

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # ניקוי markdown אם קיים
    raw = response.text.strip()
    clean = extract_json(raw)
    data = json.loads(clean)
    print("RAW:", response)
    print("TEXT:", response.text)

    return {
        "score": data.get("score", 0),
        "feedback": data.get("feedback", ""),
    }