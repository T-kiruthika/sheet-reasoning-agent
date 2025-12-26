import os
import re
import pandas as pd
from flask import Flask, request, jsonify, render_template, session
import cohere  
from pandasql import sqldf
from dotenv import load_dotenv
import numpy as np
import warnings

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

try:
    co = cohere.Client(os.environ.get("COHERE_API_KEY"))
    COHERE_API_KEY_CONFIGURED = True
except Exception as e:
    print(f"Error: Cohere API key not configured. {e}")
    COHERE_API_KEY_CONFIGURED = False

df = None

def pysqldf(q):
    return sqldf(q, globals())

def get_column_info(dataframe):
    return "\n".join([f"- '{col}' (type: {dataframe[col].dtype})" for col in dataframe.columns])

def get_system_prompt(file_schema, dataframe):
    summary_parts = [f"This dataset contains {dataframe.shape[0]} records and {dataframe.shape[1]} columns."]
    
    dept_col = next((col for col in dataframe.columns if 'dept' in col.lower()), None)
    if dept_col:
        summary_parts.append(f"- **Top Department:** The department with the most employees is '{dataframe[dept_col].mode()[0]}'.")

    sal_col = next((col for col in dataframe.columns if 'sal' in col.lower()), None)
    if sal_col and pd.api.types.is_numeric_dtype(dataframe[sal_col]):
        summary_parts.append(f"- **Salary Range:** Gross salaries range from {dataframe[sal_col].min():,.2f} to {dataframe[sal_col].max():,.2f}.")

    smart_summary_code = f'`"{"\\n".join(summary_parts)}"`'

    return f"""
        You are a master data analyst AI. Your only purpose is to generate a single, correct line of Python code to answer a user's question about a pandas DataFrame named `df`.

        **THE MOST IMPORTANT RULE:**
        - Your response MUST BE a single line of pure, valid Python code and NOTHING ELSE.
        - DO NOT include `python`, backticks, explanations, or any conversational text.

        The DataFrame `df` has this schema:
        {file_schema}
        **IMPORTANT:** Columns for names (`clean_emp_name`) and salaries have been pre-cleaned. Use them directly.

        **LOGIC GUIDELINES:**
        1. TEXT SEARCH: Use `clean_emp_name` and lowercase values.
           Example: `df[df['clean_emp_name'].str.contains('keyword', na=False)]`
        2. FULL LOOKUP: Return the entire filtered DataFrame for "details" or "tell me about".
        3. NUMERIC: Use `df.query()` for direct filtering.
        4. COUNTS: Use `value_counts().reset_index()`.
        5. GENERAL: For count/summary, return strings: {smart_summary_code}.
        """

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global df
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv')):
        try:
            df = pd.read_csv(file, encoding='utf-8', low_memory=False) if file.filename.endswith('.csv') else pd.read_excel(file)
            df.columns = df.columns.str.strip().str.lower()

            name_col = next((col for col in df.columns if 'name' in col), None)
            if name_col:
                df['clean_emp_name'] = df[name_col].astype(str).str.replace(r'^(mr\.?|ms\.?|mrs\.?|dr\.?|miss|m/s)\s*', '', regex=True, case=False).str.strip().str.lower()

            for col in df.columns:
                if any(k in col for k in ['sal', 'amount', 'price', 'cost', 'value']):
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                        df[col] = pd.to_numeric(df[col], errors='coerce')

            session.clear()
            session['chat_history'] = []
            session['file_schema'] = get_column_info(df)
            return jsonify({"success": f"File '{file.filename}' uploaded successfully."})
        except Exception as e:
            return jsonify({"error": f"Error processing file: {e}"}), 500
    return jsonify({"error": "Invalid file type."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    global df
    if not COHERE_API_KEY_CONFIGURED: return jsonify({"error": "Backend AI is not configured."}), 500
    if df is None or 'file_schema' not in session: return jsonify({"error": "Please upload a file first."}), 400
    
    user_question = request.json.get('question')
    if not user_question: return jsonify({"error": "No question provided."}), 400

    system_prompt = get_system_prompt(session['file_schema'], df)
    chat_history = session.get('chat_history', [])
    cohere_history = [{'role': 'CHATBOT' if m['role'] == 'assistant' else 'USER', 'message': m['content']} for m in chat_history]

    try:
        response = co.chat(
            message=user_question,
            preamble=system_prompt,
            chat_history=cohere_history[-4:],
            temperature=0
        )

        generated_code = response.text.strip().replace('`', '')

        try:
            result = eval(generated_code, {'df': df, 'pd': pd, 'np': np})
        except Exception:
            match = re.search(r"(df\.query\(.*\)|df\[.*\]|len\(.*\)|f?\".*?\")", generated_code)
            if match:
                result = eval(match.group(1), {'df': df, 'pd': pd, 'np': np})
            else:
                return jsonify({"answer": f"Code execution failed: <code>{generated_code}</code>"})

        if isinstance(result, pd.DataFrame):
            if result.empty:
                sal_col = next((col for col in df.columns if 'sal' in col.lower()), None)
                if sal_col and sal_col in generated_code and pd.api.types.is_numeric_dtype(df[sal_col]):
                    response_html = f"No records match. Max value in dataset: **{df[sal_col].max():,.2f}**."
                else:
                    response_html = "No records found matching that query."
            else:
                response_html = "<div class='table-responsive'>" + result.to_html(classes='table table-striped', index=False) + "</div>"

        elif isinstance(result, pd.Series):
            series_df = result.reset_index()
            series_df.columns = [result.index.name or 'Value', result.name or 'Count']
            response_html = "<div class='table-responsive'>" + series_df.to_html(classes='table table-striped', index=False) + "</div>"

        elif isinstance(result, list):
            response_html = "No results found." if not result else "<div class='table-responsive'>" + pd.DataFrame(result, columns=['Results']).to_html(classes='table table-striped', index=False) + "</div>"

        else:
            response_html = str(result).replace('\n', '<br>')

        chat_history.append({"role": "user", "content": user_question})
        chat_history.append({"role": "assistant", "content": generated_code})
        session['chat_history'] = chat_history
        return jsonify({"answer": response_html})

    except Exception as e:
        return jsonify({"answer": f"An error occurred: {e}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
