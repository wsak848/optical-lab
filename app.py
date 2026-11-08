import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from core.optical_calculations import SPEED_OF_LIGHT_M_S, wavelength_to_frequency
from core.experiment_ui import render_experiment, render_summary


st.set_page_config(
    page_title="Optical Communication Laboratory",
    page_icon="💡",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7f4; color: #111827; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 900px; padding-top: 2rem; padding-bottom: 3rem; }
    .stApp h1 { color: #0F2A44; }
    .stApp h2, .stApp h3, .stApp h4 { color: #163B65; }
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stExpander"] summary,
    .stApp [data-testid="stButton"] button,
    .stApp [data-testid="stLatex"] { color: #111827; }
    .lab-kicker { color: #163B65; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; }
    .stApp [data-testid="stMarkdownContainer"] p.instructor,
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] * { color: #374151; }
    .stApp [data-testid="stCaptionContainer"] { opacity: 1; }
    .instructor { margin-top: -0.5rem; }
    [data-testid="stMetric"] { background: #ffffff; border-left: 4px solid #e68a48; padding: 1rem; }
    .stApp [data-testid="stMetricValue"],
    .stApp [data-testid="stMetricValue"] * { color: #0F2A44; font-weight: 700; }
    .stApp [data-testid="stSliderThumbValue"],
    .stApp [data-testid="stSliderTickBarMin"],
    .stApp [data-testid="stSliderTickBarMax"] { color: #111827; }
    [data-testid="stPlotlyChart"], [data-testid="stImage"] { max-width: 100%; }
    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button,
    .stApp [role="tab"] { min-height: 44px; color: #111827; }
    .stApp [data-testid="stNumberInput"] input,
    .stApp [data-testid="stTextArea"] textarea { color: #111827; }
    .stApp [role="tablist"] { max-width: 100%; overflow-x: auto; }
    .stApp [role="tabpanel"] { min-width: 0; }
    .stApp [data-testid="stDataFrame"] { max-width: 100%; }

    @media (max-width: 480px) {
      .block-container { padding: 1.2rem 1rem 2rem; }
      h1 { font-size: 1.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="lab-kicker">OPTICAL COMMUNICATION · TEACHING LAB</div>', unsafe_allow_html=True)
st.title("Optical Communication Laboratory")
st.markdown("**ผู้สอน:** Sakda Wongadyarin", unsafe_allow_html=False)
st.markdown('<p class="instructor">ห้องทดลองการสื่อสารทางแสง</p>', unsafe_allow_html=True)
st.divider()

st.markdown("### Lab 1 · ความถี่และความยาวคลื่นของแสง")
st.write("สำรวจความสัมพันธ์ระหว่างความยาวคลื่นกับความถี่ของแสงในระบบสื่อสารใยแก้วนำแสง")

theory_tab, simulation_tab, experiment_tab, summary_tab = st.tabs(
    ["📘 ทฤษฎี", "🌊 Simulation", "🧪 การทดลองและบันทึกผล", "📊 สรุปผล"]
)

with theory_tab:
    with st.container(border=True):
        st.markdown("**ทฤษฎี**")
        st.latex(r"c = f \times \lambda \qquad f = \frac{c}{\lambda}")
        st.write("โดยที่ความเร็วแสงในสุญญากาศ")
        st.latex(r"c = 3.0 \times 10^8\ \mathrm{m/s}")
        st.caption(
            "ค่าความยาวคลื่นที่ใช้ในระบบสื่อสารด้วยแสง เช่น 850, 1310 และ 1550 nm "
            "โดยทั่วไปอ้างอิงความยาวคลื่นในสุญญากาศ "
            "เมื่อแสงเข้าสู่ใยแก้ว ความเร็วและความยาวคลื่นจะเปลี่ยนตามดัชนีหักเห "
            "แต่ความถี่ของแสงยังคงเดิม"
        )


def apply_quick_selection(wavelength_nm):
    st.session_state["wavelength_nm"] = wavelength_nm


with simulation_tab:
    st.session_state.setdefault("wavelength_nm", 1310)
    st.markdown("#### เลือกความยาวคลื่น")
    for column, preset_nm in zip(st.columns(3), (850, 1310, 1550)):
        column.button(
            f"{preset_nm} nm",
            on_click=apply_quick_selection,
            args=(preset_nm,),
            width="stretch",
        )
    wavelength_nm = st.slider(
        "ความยาวคลื่น (nm)",
        min_value=400,
        max_value=1700,
        step=1,
        key="wavelength_nm",
    )
    
    wavelength_m, frequency_hz, frequency_thz = wavelength_to_frequency(wavelength_nm)
    st.metric("ความถี่ของแสง", f"{frequency_thz:,.2f} THz")
    st.caption(
        f"λ = {wavelength_nm:,} nm = {wavelength_m:.3e} m　 ·　 "
        f"f = {frequency_hz:.3e} Hz　 ·　 c = {SPEED_OF_LIGHT_M_S:.1e} m/s"
    )
    st.write(
        f"ความยาวคลื่นในสุญญากาศ {wavelength_nm:,} nm "
        f"มีความถี่ {frequency_thz:,.2f} THz ตามความสัมพันธ์ f = c / λ; "
        "เมื่อความยาวคลื่นเพิ่มขึ้น ความถี่จะลดลง"
    )
    if wavelength_nm == 1310:
        st.caption(
            "หมายเหตุ: เมื่อใช้ c = 3.0 × 10^8 m/s จะได้ 229.01 THz; "
            "ค่า 228.85 THz ใช้ค่าความเร็วแสง c ≈ 299,792,458 m/s"
        )
    
    st.markdown("#### ภาพจำลองเชิงแนวคิดของความยาวคลื่น (Schematic spatial waveform)")
    st.caption(
        "แนวนอน = ระยะทางเชิงพื้นที่สัมพัทธ์ · แนวตั้ง = แอมพลิจูดที่ปรับเป็นมาตรฐาน "
        "(normalized amplitude) ภาพนี้เป็นภาพนิ่งเพื่อการเรียนรู้ "
        "ไม่แสดงกำลังแสงหรือระยะทางการแพร่จริง และสีของเส้นไม่ได้แทนสีของแสง"
    )
    cycle_count = 8 * 400 / wavelength_nm
    position = np.linspace(0, 1, 1000)
    amplitude = np.sin(2 * np.pi * cycle_count * position)
    figure, axis = plt.subplots(figsize=(9, 2.3))
    figure.patch.set_facecolor("#ffffff")
    axis.set_facecolor("#ffffff")
    axis.plot(position, amplitude, color="#4b5563", linewidth=2.5)
    axis.axhline(0, color="#cbd7d3", linewidth=0.8)
    axis.set_xlim(0, 1)
    axis.set_ylim(-1.25, 1.25)
    axis.axis("off")
    figure.tight_layout(pad=0.2)
    st.pyplot(figure, width="stretch")
    plt.close(figure)
    st.caption("ความยาวคลื่นสั้น → คลื่นอยู่ชิดกัน　 ·　 ความยาวคลื่นยาว → คลื่นอยู่ห่างกัน")
    
    st.markdown("#### ย่านความยาวคลื่นที่ใช้ในระบบสื่อสาร")
    st.caption("ตัวอย่างต่อไปนี้เป็นย่านใช้งานสำคัญ ไม่ได้จำกัดการใช้งานเฉพาะค่าความยาวคลื่นทั้งสามนี้")
    with st.expander("850 nm · ระยะสั้น"):
        st.write("มักใช้กับแหล่งกำเนิดแสง LED หรือ VCSEL และใยแก้วนำแสงชนิดหลายโหมดในระยะทางสั้น")
    with st.expander("1310 nm · ย่านสื่อสารสำคัญ"):
        st.write("เป็นย่านสื่อสารด้วยแสงที่สำคัญ มีการกระจายสี (chromatic dispersion) ต่ำในใยแก้วนำแสงชนิดโหมดเดี่ยวมาตรฐาน")
    with st.expander("1550 nm · การสูญเสียต่ำ"):
        st.write("เป็นย่านสื่อสารด้วยแสงที่สำคัญ ใยแก้วนำแสงชนิดโหมดเดี่ยวมาตรฐานมีการลดทอนต่ำในย่านนี้ จึงนิยมใช้ในการส่งสัญญาณระยะไกล")
    
    with st.expander("Labs ถัดไป"):
        st.markdown(
            """
        2. การลดทอนในใยแก้วนำแสง  
        3. กำลังแสงและหน่วย dBm  
        4. Optical Link Budget  
        5. Dispersion  
        6. LED และ Laser Diode  
        7. Photodetector  
        8. SNR และ BER
        """
        )

with experiment_tab:
    render_experiment(wavelength_nm)

with summary_tab:
    render_summary()
