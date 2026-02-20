from fastapi import FastAPI, Request, HTTPException
from google import genai
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import re
import json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS


app = FastAPI() 
load_dotenv()
key = os.getenv("GEMINI_KEY")
limiter = Limiter(key_func = get_remote_address)
global rate_qes = 0.075
global rate_ans = 0.3
global current_used = 0
global limit_usd = 1
app.state.limiter = limiter

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
@limiter.limit("5/minute")
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
                Your Answer should be in the language the question was asked!
                """
    client = genai.Client(api_key=key)
    # קריאה לפונקציה שסופרת טוקנים
    count_response = client.models.count_tokens(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # שליפת מספר הטוקנים מתוך אובייקט התשובה
    total_tokens = count_response.total_tokens

    # חישוב העלות: כמות הטוקנים חלקי מיליון, כפול התעריף
    cost_in_dollars = (total_tokens / 1_000_000) * rate_qes
    current_used += cost_in_dollars
    
    if current_used >= limit_usd:
        raise HTTPException("budget exceeded!")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=(int)((limit_usd-current_used/rate_ans)*1000000), 
        )
    )
    current_used += (response.usage_metadata.candidates_token_count/1000000)*rate_ans
    
    # ניקוי markdown אם קיים
    # raw = response.text.strip()
    # raw = raw.replace("```json", "").replace("```", "").strip()
    # data = json.loads(raw)
    raw = response.text.strip()
    clean = extract_json(raw)
    data = json.loads(clean)
    print("RAW:", response)
    print("TEXT:", response.text)

    return {
        "easy": data.get("easy", ""),
        "medium": data.get("medium", ""),
        "hard": data.get("hard", "")
    }


@app.post("/chat_answers")
@limiter.limit("5/minute")
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
                Your Answer should be in the language the Student Answer was answered (the language most of the answer was written in) - not necessarily the same as the question!
                be more generous with the score if the answer is mostly correct but has minor issues, and more critical if the answer is mostly incorrect or missing key elements.

                Question: {topic.get("question", "")}
                Student Answer: {topic.get("answer", "")}"""

    client = genai.Client(api_key=key)

        # קריאה לפונקציה שסופרת טוקנים
    count_response = client.models.count_tokens(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # שליפת מספר הטוקנים מתוך אובייקט התשובה
    total_tokens = count_response.total_tokens

    # חישוב העלות: כמות הטוקנים חלקי מיליון, כפול התעריף
    cost_in_dollars = (total_tokens / 1_000_000) * rate_qes
    current_used += cost_in_dollars
    
    if current_used >= limit_usd:
        raise HTTPException("budget exceeded!")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=(int)((limit_usd-current_used/rate_ans)*1000000), 
        )
    )

     current_used += ((response.usage_metadata.candidates_token_count)/1000000)*rate_ans
    
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
