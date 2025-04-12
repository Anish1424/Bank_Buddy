# 🚀 AI-Driven Secure Banking Chatbot with Fraud Prevention

An advanced, AI-powered banking assistant that helps users manage their finances while proactively detecting and preventing fraud in real-time. This secure and smart chatbot uses cutting-edge AI and voice technologies to deliver fast, intuitive, and safe digital banking experiences.

---

## 🧠 Key Features

### ✅ 1. AI Chatbot for Banking Assistance
- Handles user queries like:
  - 🔍 Balance checks
  - 💸 Fund transfers
  - 💳 Credit card applications (ongoing)
  - 📄 Loan eligibility
  - 📊 Transaction history
- Offers personalized financial advice using AI.
- Supports **multilingual voice and text** interaction.

### ✅ 2. AI-Powered Real-Time Fraud Detection
- Uses **Machine Learning (ML)** to analyze user behavior and detect anomalies.
- Monitors transactions in real-time.
- Flags risky activities and asks for additional verification.

### ✅ 3. Voice-Based Secure Transactions
- Implements **Voice Biometrics** to authenticate high-value transactions.
- Analyzes tone, pitch, and frequency to verify identity.
- Ensures only the rightful user can complete sensitive actions.

### ✅ 4. Auto-Freezing of Compromised Accounts (ongoing)
- Detects suspicious behavior such as:
  - Unusual login locations
  - Repeated failed attempts
- Instantly **locks compromised accounts**.
- Requests **OTP or Face ID verification**.
- Notifies both the user and the bank.

---

## 🛠️ Tech Stack

| Layer            | Technologies Used                                      |
|------------------|--------------------------------------------------------|
| **Frontend**     | React.js, Tailwind CSS                                 |
| **AI Layer**     | LangChain, NLP, ML Models for Fraud Detection          |
| **Authentication** | Voice Biometrics, OTP, Face ID                       |
| **Backend / Logic** | LangChain agents, Custom APIs                      |
| **Database**     | Firebase (Firestore, Authentication)                   |
| **Deployment**   | Firebase Hosting / Vercel / Netlify (optional)         |

---

## 📊 System Flowchart

A complete flowchart that visualizes how the chatbot interacts with users, detects fraud, authenticates voice, and prevents unauthorized access.

![AI Banking Chatbot Flowchart](./AI_Banking_Chatbot_Flowchart.png)

---

## 📁 Project Structure

```bash
.
├── README.md
├── AI_Banking_Chatbot_Flowchart.png
├── public
|   src/
|      |-components       # React + Tailwind CSS
│      |-Pages
├── package-lock.json
├── package.json
|
├── /backend             # LangChain agents and logic
│   ├── app.py/
│   └── serviceActivation.json/
└── /firebase(inside src/)            # Firestore config & rules
 
