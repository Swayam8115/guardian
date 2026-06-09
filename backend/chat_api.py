from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy import text
from config.settings import settings
from database.db import SessionLocal

router = APIRouter()

# ── Schema hint injected into the SQL-generation prompt ──────────────────────
DB_SCHEMA = """
Table: fir_records
Columns:
  id                      INTEGER  (primary key)
  fir_number              TEXT
  police_station          TEXT
  district                TEXT
  state                   TEXT
  date_of_incident        TEXT     (YYYY-MM-DD)
  date_of_filing          TEXT     (YYYY-MM-DD)
  complainant_name        TEXT
  complainant_contact     TEXT
  accused_names           JSON     (array of strings)
  victim_names            JSON     (array of strings)
  crime_categories        JSON     (array of strings, e.g. ["Theft","Robbery"])
  sections_invoked        JSON     (array of strings)
  location                TEXT
  generalised_location    TEXT
  latitude                FLOAT
  longitude               FLOAT
  incident_summary        TEXT
  actions_taken           TEXT
  created_at              TIMESTAMP

Querying JSON arrays (PostgreSQL):
  -- match a value inside crime_categories:
  WHERE crime_categories::text ILIKE '%Theft%'
  -- count rows per district:
  SELECT district, COUNT(*) FROM fir_records GROUP BY district ORDER BY COUNT(*) DESC
"""


# ── Structured output schemas ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class SQLQuery(BaseModel):
    sql: str = Field(description=(
        "A safe PostgreSQL SELECT query to answer the user's question. "
        "Must start with SELECT. Never use INSERT, UPDATE, DELETE, or DROP."
    ))


class AssistantReply(BaseModel):
    reply: str = Field(description=(
        "A clear, structured natural language answer derived from the SQL results. "
        "Use bullet points or a short table where it helps readability."
    ))


# ── Endpoint ──────────────────────────────────────────────────────────────────
@router.post("/chat")
def chat(body: ChatRequest):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=settings.GOOGLE_API_KEY_1,
    )

    # ── Step 1: natural language → SQL ────────────────────────────────────────
    sql_llm = llm.with_structured_output(SQLQuery)
    sql_result: SQLQuery = sql_llm.invoke([
        SystemMessage(content=(
            "You are a PostgreSQL expert. Convert the user's question into a single safe SELECT query.\n"
            "Rules:\n"
            "- Only SELECT statements. Never mutate data.\n"
            "- Limit results to at most 50 rows (add LIMIT 50 unless the query is an aggregate).\n"
            "- Use ILIKE for case-insensitive text matching.\n\n"
            "Schema:\n" + DB_SCHEMA
        )),
        HumanMessage(content=body.message),
    ])

    sql = sql_result.sql.strip()

    # Safety gate — reject anything that isn't a SELECT
    if not sql.upper().lstrip().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are permitted.")

    # ── Step 2: execute SQL ───────────────────────────────────────────────────
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchmany(50)
        data = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL error: {e}")
    finally:
        db.close()

    # ── Step 3: SQL results → structured natural language answer ──────────────
    answer_llm = llm.with_structured_output(AssistantReply)
    answer: AssistantReply = answer_llm.invoke([
        SystemMessage(content=(
            "You are Guardian Assist, an AI crime analysis assistant for the GUARDIAN platform. "
            "You have retrieved live data from the database. "
            "Give a concise, well-structured answer to the user's question based solely on the data provided. "
            "If the data is empty, say so clearly."
        )),
        HumanMessage(content=(
            f"User question: {body.message}\n\n"
            f"SQL used: {sql}\n\n"
            f"Results ({len(data)} row(s)):\n{data}"
        )),
    ])

    return {
        "reply": answer.reply,
        "sql": sql,
        "row_count": len(data),
    }
