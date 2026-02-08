import streamlit as st
import os
import time
import re
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

st.set_page_config(
    page_title="Advocate's Bench",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Background */
    .stApp {
        background: radial-gradient(circle at top left, #1a2a6c, #b21f1f, #fdbb2d);
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        background-attachment: fixed;
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #f8fafc !important;
        letter-spacing: 0.5px;
    }
    p, li, div, span, label, input, button {
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
        line-height: 1.6 !important; /* Better readability */
    }

    /* Main Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        height: 100%;
    }

    /* Argument List Items (The Fix) */
    .arg-item {
        margin-bottom: 16px !important; /* Big Gap between items */
        background: rgba(255, 255, 255, 0.04);
        padding: 16px !important; /* More breathing room inside */
        border-radius: 10px;
        border-left: 4px solid; /* Thicker accent line */
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    .arg-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(3px); /* Subtle interaction */
    }

    /* Accents Colors */
    .pro-accent { border-top: 4px solid #3b82f6; }
    .con-accent { border-top: 4px solid #ef4444; }
    .verdict-accent { border-top: 4px solid #eab308; background: rgba(234, 179, 8, 0.05); }
    .action-accent { border-top: 4px solid #10b981; }

    .arg-pro { border-color: #3b82f6; }
    .arg-con { border-color: #ef4444; }

    /* Input Box */
    .stTextInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 12px;
        padding: 16px;
        font-size: 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 40px !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 118, 255, 0.3) !important;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }
    .badge-pro { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-con { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-verdict { background: rgba(234, 179, 8, 0.15); color: #fde047; border: 1px solid rgba(234, 179, 8, 0.3); }
    .badge-action { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }

    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def typewriter(text: str, speed: float = 0.02):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(f"<h1 style='text-align: center; margin-bottom: 5px;'>{curr_full_text}</h1>", unsafe_allow_html=True)
        time.sleep(speed)

class DebateAgent:
    def __init__(self, groq_key, tavily_key):
        self.groq = Groq(api_key=groq_key)
        self.tavily = TavilyClient(api_key=tavily_key)

    def search(self, query):
        try:
            enhanced_query = f"{query} landmark supreme court judgments india NCRB statistics real life case studies legal precedent global laws comparison"
            response = self.tavily.search(query=enhanced_query, search_depth="advanced", max_results=5)
            return "\n".join([f"- {r['content']}" for r in response['results']])
        except:
            return "No specific evidence found."

    def clean_text(self, text):
        text = re.sub(r"```(html|xml|markdown)?", "", text, flags=re.IGNORECASE)
        text = text.replace("```", "")
        return text.strip()

    def generate(self, system_prompt, user_content):
        completion = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3, 
            max_tokens=1500
        )
        raw_response = completion.choices[0].message.content
        return self.clean_text(raw_response)

    def run_proponent(self, topic):
        evidence = self.search(f"benefits, laws, and landmark judgments supporting {topic}")
        prompt = """
        You are a Senior Advocate representing the Petitioner.
        
        INSTRUCTIONS:
        1. Generate EXACTLY 5 distinct, powerful legal arguments.
        2. Each argument MUST cite a specific Law, Case (e.g. 'X vs Y'), or Statistic.
        
        OUTPUT RAW HTML ONLY (NO MARKDOWN):
        <div>
            <p style='font-size: 1.1rem; font-weight: 500; margin-bottom: 20px; color: #cbd5e1; font-style: italic;'>
                "My Lord, the weight of evidence is overwhelming..."
            </p>
            <ul style='list-style-type: none; padding-left: 0;'>
                <li class='arg-item arg-pro'>
                    <strong style='color: #60a5fa; display: block; margin-bottom: 4px;'>1. Constitutional Basis</strong> 
                    [Argument citing specific Article or Fundamental Right]
                </li>
                <li class='arg-item arg-pro'>
                    <strong style='color: #60a5fa; display: block; margin-bottom: 4px;'>2. Binding Precedent</strong> 
                    [Cite a Landmark Supreme Court/High Court Case Name]
                </li>
                <li class='arg-item arg-pro'>
                    <strong style='color: #60a5fa; display: block; margin-bottom: 4px;'>3. Statistical Evidence</strong> 
                    [Cite NCRB/Global Data or Study Percentage]
                </li>
                 <li class='arg-item arg-pro'>
                    <strong style='color: #60a5fa; display: block; margin-bottom: 4px;'>4. Global Best Practice</strong> 
                    [Compare with laws in EU/USA or International Conventions]
                </li>
                 <li class='arg-item arg-pro'>
                    <strong style='color: #60a5fa; display: block; margin-bottom: 4px;'>5. Socio-Legal Impact</strong> 
                    [Argument about public interest or innovation]
                </li>
            </ul>
        </div>
        """
        return self.generate(prompt, f"Topic: {topic}\n\nEvidence: {evidence}")

    def run_critic(self, topic):
        evidence = self.search(f"dangers, risks, and legal failures opposing {topic}")
        prompt = """
        You are the Solicitor General representing the Opposition.
        
        INSTRUCTIONS:
        1. Generate EXACTLY 5 distinct, sharp legal arguments.
        2. Each argument MUST cite a Failure, Risk, Dissenting Judgment, or Statistic.
        
        OUTPUT RAW HTML ONLY (NO MARKDOWN):
        <div>
            <p style='font-size: 1.1rem; font-weight: 500; margin-bottom: 20px; color: #cbd5e1; font-style: italic;'>
                "Your Honor, we must look at the disastrous consequences..."
            </p>
            <ul style='list-style-type: none; padding-left: 0;'>
                 <li class='arg-item arg-con'>
                    <strong style='color: #f87171; display: block; margin-bottom: 4px;'>1. Violation of Rights</strong> 
                    [Argument citing specific Article or Privacy/Safety violation]
                </li>
                <li class='arg-item arg-con'>
                    <strong style='color: #f87171; display: block; margin-bottom: 4px;'>2. Evidence of Failure</strong> 
                    [Cite a Real-World Disaster, Scandal, or Misuse Case]
                </li>
                <li class='arg-item arg-con'>
                    <strong style='color: #f87171; display: block; margin-bottom: 4px;'>3. Legal Loophole</strong> 
                    [Cite specific section of IPC/IT Act that is weak]
                </li>
                 <li class='arg-item arg-con'>
                    <strong style='color: #f87171; display: block; margin-bottom: 4px;'>4. Ethical & Moral Risk</strong> 
                    [Argument about bias, discrimination, or humanity]
                </li>
                 <li class='arg-item arg-con'>
                    <strong style='color: #f87171; display: block; margin-bottom: 4px;'>5. Economic/Social Cost</strong> 
                    [Cite potential job loss, financial fraud stats, or social unrest]
                </li>
            </ul>
        </div>
        """
        return self.generate(prompt, f"Topic: {topic}\n\nEvidence: {evidence}")

    def run_judge_and_actions(self, topic, pro, con):
        prompt = """
        You are the Chief Justice of India.
        
        CRITICAL INSTRUCTION:
        Pick a WINNER. Do not be balanced. If it violates rights, strike it down. If it is legal, uphold it.
        
        INSTRUCTIONS:
        1. Generate Verdict HTML.
        2. Type "|||" (three pipes).
        3. Generate Actionable Directives HTML.
        
        OUTPUT FORMAT (STRICT):
        <div>
            <p style='margin-top: 10px; font-size: 1.2rem; line-height: 1.6;'><b>ORDER: [UPHELD / STRUCK DOWN / PARTIALLY ALLOWED]</b>. [Decisive Reasoning Paragraph]</p>
        </div>
        |||
        <div>
            <ul style='display: flex; gap: 15px; list-style: none; padding: 0; flex-wrap: wrap;'>
                <li style='flex: 1; min-width: 250px; background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #10b981;'>
                    <strong style='color: #34d399; font-size: 1.1rem; display: block; margin-bottom: 8px;'>Directive 1</strong> 
                    [Specific Action]
                </li>
                 <li style='flex: 1; min-width: 250px; background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #10b981;'>
                    <strong style='color: #34d399; font-size: 1.1rem; display: block; margin-bottom: 8px;'>Directive 2</strong> 
                    [Specific Action]
                </li>
                 <li style='flex: 1; min-width: 250px; background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #10b981;'>
                    <strong style='color: #34d399; font-size: 1.1rem; display: block; margin-bottom: 8px;'>Directive 3</strong> 
                    [Specific Action]
                </li>
            </ul>
        </div>
        """
        full_response = self.generate(prompt, f"Topic: {topic}\n\nPro: {pro}\n\nCon: {con}")
        

        parts = re.split(r"\|{2,3}", full_response)
        
        if len(parts) > 1:
             return parts[0].strip(), parts[1].strip()
        else:

            return full_response, "<div>No specific directives generated.</div>"

def main():
    env_groq = os.getenv("GROQ_API_KEY")
    env_tavily = os.getenv("TAVILY_API_KEY")
    
    if not env_groq or not env_tavily:
        st.error("🚨 System Error: API Keys not found. Please check your .env file.")
        st.stop()

    st.markdown("<br>", unsafe_allow_html=True)
    if "first_load" not in st.session_state:
        typewriter("⚖️ Advocate's Bench")
        st.session_state.first_load = True
    else:
        st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>⚖️ Advocate's Bench</h1>", unsafe_allow_html=True)
        
    st.markdown("<p style='text-align: center; color: #94a3b8 !important; font-size: 16px; margin-bottom: 40px;'>The AI Courtroom: Where Logic Meets Law.</p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        with st.form("debate_form"):
            topic = st.text_input("Enter a Legal Query", placeholder="e.g. Is the 90-day notice period legal in India?", label_visibility="collapsed")
            start_btn = st.form_submit_button("Start Proceedings")

    if start_btn and topic:
        agent = DebateAgent(env_groq, env_tavily)
        
        st.markdown("<br>", unsafe_allow_html=True)
        progress_text = "Searching Constitutional Precedents..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        my_bar.empty()

        with st.spinner("The Court is in session..."):
            pro_text = agent.run_proponent(topic)
            con_text = agent.run_critic(topic)
            verdict, actions = agent.run_judge_and_actions(topic, pro_text, con_text)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown(f"""<div class='glass-card pro-accent'><div class='badge badge-pro'>PETITIONER</div>{pro_text}</div>""", unsafe_allow_html=True)
        with row1_col2:
            st.markdown(f"""<div class='glass-card con-accent'><div class='badge badge-con'>OPPOSITION</div>{con_text}</div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='glass-card verdict-accent' style='text-align: center;'>
            <div class='badge badge-verdict' style='margin-bottom: 15px;'>SUPREME COURT VERDICT</div>
            {verdict}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='glass-card action-accent'>
            <div class='badge badge-action'>ACTIONABLE DIRECTIVES</div>
            {actions}
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()