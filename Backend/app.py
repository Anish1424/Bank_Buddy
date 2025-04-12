import os
import traceback
import firebase_admin
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from fuzzywuzzy import fuzz
import re
from datetime import datetime

# ✅ Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("⚠ GEMINI_API_KEY is missing. Set it in the .env file.")

genai.configure(api_key=gemini_api_key)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

# ✅ Initialize Firebase
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # ✅ Check Firebase connection
    db.collection("accounts").limit(1).get()
except Exception as e:
    raise ValueError(f"⚠ Firebase initialization failed: {e}")

app = Flask(__name__)
CORS(app)

# ✅ User session management
user_sessions = {}

def is_banking_related(query):
    """Uses Gemini to classify if the query is banking-related."""
    try:
        prompt = f"Is the following query related to banking? Answer with 'yes' or 'no' only.\n\nQuery: {query}"
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip().lower() == "yes"
        return False
    except Exception as e:
        print(f"⚠ Error in is_banking_related: {e}")
        return False

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Banking Chatbot Backend is Running!"})

@app.route("/chat", methods=["POST"])
def chat():
    """Handles user chat queries intelligently."""
    try:
        data = request.json
        print("Received JSON Data:", data)
        user_query = data.get("query", "").strip().lower()
        user_id = data.get("user_id", "default_user")

        if not user_query:
            return jsonify({"error": "Query is missing"}), 400

        # ✅ Handle greetings quickly
        greetings = ["hi", "hello", "hey", "hii", "good morning", "good evening"]
        if any(fuzz.ratio(user_query, g) > 80 for g in greetings):
            return jsonify({"response": "I am BankBuddy, your banking chatbot. How can I assist you today?"})
        
        if "report" in user_query:
            return jsonify({"response": report_upi_fraud(user_query, user_id)})
        
        if "statement" in user_query or "mini statement" in user_query:
            return jsonify( {"response":get_transactions_email(user_id)})
            

        # ✅ Check if the query is banking-related
        if not is_banking_related(user_query):
            return jsonify({"response": "I am a banking chatbot. Please ask me about banking-related queries."})

        # ✅ Process money transfer request
        if "send" in user_query and "to" in user_query:
            return jsonify({"response": process_money_transfer(user_query, user_id)})

        # ✅ Classify and respond to user query
        response = handle_user_query(user_query, user_id)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": f"⚠ Server Error: {traceback.format_exc()}"}), 500

def handle_user_query(user_query, user_id):
    """Routes user queries to the appropriate function using LangChain."""
    tools = [
        Tool(name="Balance Inquiry", func=lambda _: get_balance(user_id), description="Check account balance"),
        Tool(name="Transaction History", func=lambda _: get_transactions(user_id), description="Retrieve recent transactions"),
        Tool(name="Money Transfer", func=lambda _: process_money_transfer(user_query, user_id), description="Initiate a fund transfer"),
        Tool(name="Loan Inquiry", func=lambda _: "For loan details, visit your bank’s website or contact customer service.", description="Get loan information"),
        Tool(name="Customer Support", func=lambda _: "You can contact customer support at 8459854972.", description="Get bank support contact")
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        memory=ConversationBufferMemory(memory_key="chat_history"),
        handle_parsing_errors=True  # ✅ Prevents parsing-related errors
    )

    try:
        return agent.run(user_query)
    except Exception:
        return "I'm sorry, I couldn't understand that. Can you rephrase?"

# ✅ Helper functions
def get_balance(user_id):
    """Fetches account balance for the logged-in user."""
    try:
        user_doc = db.collection("Accounts").document(user_id).get()
        if not user_doc.exists:
            return "⚠ User not found."

        user_data = user_doc.to_dict()
        account_balance = user_data.get("account_balance", 0)
        return f"💰 Your current bank balance is ₹{account_balance}."

    except Exception as e:
        print(f"⚠ Error in get_balance: {traceback.format_exc()}")
        return "⚠ Unable to fetch account balance at the moment. Please try again later."

def get_transactions(user_id):
    """Retrieves all transactions directly from the user's document."""
    try:
        user_doc = db.collection("Accounts").document(user_id).get()
        if not user_doc.exists:
            return "⚠ User not found."

        user_data = user_doc.to_dict()
        transactions = user_data.get("transactions", [])
        if not transactions:
            return "🔍 No recent transactions found."

        transaction_list = "\n".join([
            f"💰 {t.get('type', 'Unknown').capitalize()}: ₹{t.get('amount', 0)} | 🆔 {t.get('txn_id', 'N/A')} | 📅 {t.get('time', 'N/A')}"
            for t in transactions
        ])

        return transaction_list

    except Exception as e:
        print(f"⚠ Error in get_transactions: {traceback.format_exc()}")
        return "⚠ Unable to fetch transactions at the moment. Please try again later."
import re
from datetime import datetime

def process_money_transfer(query, user_id):
    """Extracts details from the query and processes money transfer with fraud detection and PIN verification."""
    
    # ✅ Extract details using regex
    print(query)
    match = re.search(r"send\s*(\d+)\s*rs\s*to\s*([\w@]+)\s*pin=(\d+)", query)
    if not match:
        return "⚠ Invalid transfer format. Try 'Send 100rs to abhay@upi PIN=123456'."

    amount = int(match.group(1))
    recipient_upi = match.group(2)
    entered_pin = int(match.group(3))

    # ✅ Fetch sender details
    user_doc = db.collection("Accounts").document(user_id).get()
    if not user_doc.exists:
        return "⚠ User not found."

    user_data = user_doc.to_dict()
    sender_balance = user_data.get("account_balance", 0)
    stored_pin = int(user_data.get("pin", ""))
    sender_upi = user_data.get("upi_id", "")
    
    print(stored_pin, entered_pin)

    # ✅ PIN Verification
    if entered_pin != stored_pin:
        return "⚠ Incorrect PIN. Transaction failed."

    # ✅ Check balance
    if amount > sender_balance:
        return "⚠ Insufficient balance."

    # ✅ Fetch recipient details from UPI collection
    r_upi_doc = db.collection("upi").document(recipient_upi).get()
    if not r_upi_doc.exists:
        return "⚠ UPI ID not found."

    rec_data = r_upi_doc.to_dict()
    is_fraud = rec_data.get("is_fraud", False)  # Check if recipient is marked as fraud

    # 🚨 Fraud detection check
    if is_fraud:
        return "🚨 Transaction canceled! The recipient UPI ID is flagged for fraudulent activities. Please report this to your bank."

    # ✅ Fetch recipient's user ID
    rec_user_id = rec_data.get("user_id")
    rec_user_doc = db.collection("Accounts").document(rec_user_id).get()
    rec_user_data = rec_user_doc.to_dict()
    rec_balance = rec_user_data.get("account_balance", 0)

    # ✅ Deduct amount and update sender balance
    new_balance = sender_balance - amount
    db.collection("Accounts").document(user_id).update({"account_balance": new_balance})

    # ✅ Record sender transaction
    transaction = {
        "type": "debit",
        "amount": amount,
        "txn_id": f"TXN{int(datetime.now().timestamp())}",
        "time": datetime.now().strftime("%d %b %Y, %H:%M"),
        "recipient": recipient_upi
    }
    db.collection("Accounts").document(user_id).update({"transactions": firestore.ArrayUnion([transaction])})

    # ✅ Update recipient balance
    new_rec_balance = rec_balance + amount
    db.collection("Accounts").document(rec_user_id).update({"account_balance": new_rec_balance})

    # ✅ Record recipient transaction
    rec_transaction = {
        "type": "credit",
        "amount": amount,
        "txn_id": f"TXN{int(datetime.now().timestamp())}",
        "time": datetime.now().strftime("%d %b %Y, %H:%M"),
        "sender": sender_upi
    }
    db.collection("Accounts").document(rec_user_id).update({"transactions": firestore.ArrayUnion([rec_transaction])})

    return f"✅ ₹{amount} sent successfully to {recipient_upi}. Your new balance is ₹{new_balance}."

def report_upi_fraud(query, user_id):
    """Handles the reporting of a fraudulent UPI ID."""
    try:
        # Extract UPI ID from the query using regex
        match = re.search(r"report\s*([\w@]+)", query)
        if not match:
            return "⚠ Invalid report format. Use 'report xyz@upi'."

        reported_upi = match.group(1)

        # Fetch the UPI ID from the database
        upi_doc = db.collection("upi").document(reported_upi).get()
        if not upi_doc.exists:
            return "⚠ UPI ID not found. Unable to report."

        # Update the 'is_fraud' field to True
        db.collection("upi").document(reported_upi).update({"is_fraud": True})

        return f"✅ UPI ID {reported_upi} has been marked as fraudulent."

    except Exception as e:
        print(f"⚠ Error in report_upi_fraud: {traceback.format_exc()}")
        return "⚠ An error occurred while reporting the UPI ID. Please try again later."


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Fixed email sender credentials
EMAIL_USER = "samikshakm2004@gmail.com"
EMAIL_PASS = "gpbnaukynomfidpo"  # Use an app password for security

def send_email(to_email, subject, body):
    print("Abhay")
    """Sends an email with the given subject and body from a fixed sender."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        
        return "✅ Email sent successfully."
    except Exception as e:
        print(f"⚠ Error sending email: {e}")
        return "⚠ Failed to send email."

def get_transactions_email(user_id):
    """Fetches all transactions and sends them to the user's email."""
    try:
        user_doc = db.collection("Accounts").document(user_id).get()
        if not user_doc.exists:
            return "⚠ User not found."

        user_data = user_doc.to_dict()
        transactions = user_data.get("transactions", [])
        user_email = user_data.get("email")
        
        if not transactions:
            return "🔍 No recent transactions found."
        if not user_email:
            return "⚠ User email not found."

        transaction_details = "\n".join([
            f"💰 {t.get('type', 'Unknown').capitalize()}: ₹{t.get('amount', 0)} | 🆔 {t.get('txn_id', 'N/A')} | 📅 {t.get('time', 'N/A')}"
            for t in transactions
        ])
        
        email_subject = "Your Transaction History"
        email_body = f"Hello,\n\nHere are all your transactions:\n\n{transaction_details}\n\nBest Regards,\nBankBuddy"
        return send_email(user_email, email_subject, email_body)

    except Exception as e:
        print(f"⚠ Error in get_transactions_email: {traceback.format_exc()}")
        return "⚠ Unable to fetch transactions at the moment."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)