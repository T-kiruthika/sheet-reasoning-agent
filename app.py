import os
import re
import pandas as pd
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import cohere
from pandasql import sqldf
from dotenv import load_dotenv
import numpy as np
import warnings

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

try:
    co = cohere.Client(os.environ.get("COHERE_API_KEY"))
    COHERE_API_KEY_CONFIGURED = True
    print("Cohere API key configured successfully.")
except Exception as e:
    print(f"Warning: Cohere API key not configured. {e}")
    COHERE_API_KEY_CONFIGURED = False

df = None

def get_column_info(dataframe):
    return "\n".join([f"- '{col}' (type: {dataframe[col].dtype})" for col in dataframe.columns])

def get_system_prompt(file_schema, dataframe):
    summary_parts = [f"This dataset contains {dataframe.shape[0]} records and {dataframe.shape[1]} columns."]
    dept_col = next((col for col in dataframe.columns if 'dept' in col.lower()), None)
    if dept_col:
        summary_parts.append(f"- **Top Department:** '{dataframe[dept_col].mode()[0]}'.")
    
    sal_col = next((col for col in dataframe.columns if 'sal' in col.lower()), None)
    if sal_col and pd.api.types.is_numeric_dtype(dataframe[sal_col]):
        summary_parts.append(f"- **Salary Range:** {dataframe[sal_col].min():,.2f} to {dataframe[sal_col].max():,.2f}.")

    smart_summary_code = f'`"{"\\n".join(summary_parts)}"`'

    return f"""
    You are a master data analyst AI. Generate a single, correct line of Python code to answer questions about a pandas DataFrame named `df`.
    
    **RULES:**
    - Response MUST be a single line of pure Python code.
    - NO backticks, NO "python" markdown, NO explanations.
    
    DataFrame Schema:
    {file_schema}
    
    TEXT SEARCH RULE: Use 'clean_emp_name' and lowercase search strings.
    Example: df[df['clean_emp_name'].str.contains('keyword', na=False)]
    
    SUMMARY RULE: {smart_summary_code}
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

    try:
        df = pd.read_csv(file, encoding='utf-8', low_memory=False) if file.filename.endswith('.csv') else pd.read_excel(file)
        df.columns = df.columns.str.strip().str.lower()

        name_col = next((col for col in df.columns if 'name' in col), None)
        if name_col:
            df['clean_emp_name'] = df[name_col].astype(str).str.replace(r'^(mr\.?|ms\.?|mrs\.?|dr\.?|miss|m/s)\s*', '', regex=True, case=False).str.strip().str.lower()

        for col in df.columns:
            if any(k in col for k in ['sal', 'amount', 'price', 'cost', 'value']):
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')

        session['file_schema'] = get_column_info(df)
        session['chat_history'] = []
        return jsonify({"success": f"File '{file.filename}' ready."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global df
    if df is None: return jsonify({"error": "Upload file first."}), 400
    user_question = request.json.get('question')
    
    max_retries = 2
    attempt = 0
    error_feedback = None
    last_failed_code = None

    while attempt < max_retries:
        if attempt == 0:
            current_prompt = get_system_prompt(session['file_schema'], df)
            message_to_send = user_question
        else:
            current_prompt = f"RETRY MODE: Your previous code failed. Fix it.\nSchema: {session['file_schema']}"
            message_to_send = f"""
            User Question: {user_question}
            Failing Code: {last_failed_code}
            Python Error: {error_feedback}
            
            Instruction: Correct the code. Provide ONLY the fixed 1-line Python code.
            """

        try:
            response = co.chat(
                message=message_to_send,
                preamble=current_prompt,
                temperature=0
            )
            generated_code = response.text.strip().replace('`', '').replace('python', '')
            
            if generated_code.startswith('df['): pass 
            elif 'df[' in generated_code:
                generated_code = re.search(r"df\[.*\]", generated_code).group(0)

            result = eval(generated_code, {'df': df, 'pd': pd, 'np': np})
            
            break

        except Exception as e:
            attempt += 1
            error_feedback = str(e)
            last_failed_code = generated_code
            print(f"Agent Attempt {attempt} failed: {error_feedback}")
            
            if attempt == max_retries:
                return jsonify({"answer": f"The Agent tried to fix the code {max_retries} times but failed.<br>Error: <code>{e}</code>"})
                
    response_html = ""
    if isinstance(result, pd.DataFrame):
        if result.empty:
            response_html = "I couldn't find any records that match your query."
        else:
            response_html = "<div class='table-responsive'>" + result.to_html(classes='table table-striped', index=False) + "</div>"
    elif isinstance(result, (pd.Series, list)):
        res_df = pd.DataFrame(result)
        response_html = "<div class='table-responsive'>" + res_df.to_html(classes='table table-striped', index=False) + "</div>"
    else:
        response_html = str(result).replace('\n', '<br>')

    history = session.get('chat_history', [])
    history.append({"role": "user", "content": user_question})
    history.append({"role": "assistant", "content": generated_code})
    session['chat_history'] = history
    
    return jsonify({"answer": response_html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
