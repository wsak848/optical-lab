"""Thai-first Lab 3 UI; each trial reveals its reference only after submission."""
import pandas as pd
import streamlit as st

from core.optical_power import (
    DEFAULT_PROFILE, LENGTH_TRIALS, POWER_TRIALS, TEACHING_PROFILES,
    check_db_answer, check_fiber_trial, dbm_to_mw, fiber_loss, mw_to_dbm,
    output_power, summarize,
)

QUESTIONS = [
    '0 dBm เท่ากับกี่ mW?',
    'dB และ dBm แตกต่างกันอย่างไร?',
    'เมื่อระยะทาง Fiber เพิ่มขึ้น Total Loss เปลี่ยนอย่างไร?',
    'เมื่อ Loss เพิ่มขึ้น Output Power เปลี่ยนอย่างไร?',
    'ค่า attenuation มีผลต่อระยะทางการส่งสัญญาณอย่างไร?',
    'เหตุใดระบบ Fiber ระยะไกลจึงให้ความสำคัญกับช่วง wavelength ที่มี attenuation ต่ำ?',
]
PROFILE_NOTE = ('ค่าตัวอย่างสำหรับการเรียนรู้ — attenuation จริงขึ้นอยู่กับชนิดใยแก้ว '
                'wavelength ผู้ผลิต สภาพสาย connectors, splices และปัจจัยอื่น ๆ '
                'จึงไม่ใช่ค่าคงที่สากล แบบจำลองนี้คิดเฉพาะการลดทอนในเนื้อใยแก้ว')


def evaluation(result):
    return '✓ ถูกต้อง' if result['correct'] else 'ตรวจสอบการคำนวณอีกครั้ง'


def power_rows(results):
    return [{
        'ครั้งที่': i, 'กำลังแสง (mW)': power,
        'ค่าอ้างอิง (dBm)': f"{results[power]['reference']:.3f}" if power in results else 'ยังไม่เปิดเผย',
        'ค่าที่นักศึกษาคำนวณ (dBm)': f"{results[power]['answer']:.3f}" if power in results else 'ยังไม่กรอก',
        'ผลต่าง (dB)': f"{results[power]['error']:.3f}" if power in results else 'รอตรวจ',
        'ผลการตรวจ': evaluation(results[power]) if power in results else 'รอตรวจ',
    } for i, power in enumerate(POWER_TRIALS, 1)]


def experiment_rows(results):
    rows = []
    for i, length in enumerate(LENGTH_TRIALS, 1):
        r = results.get(length)
        rows.append({
            'ครั้งที่': i, 'Wavelength/Profile': DEFAULT_PROFILE, 'Pin (dBm)': 0,
            'Fiber Length (km)': length, 'alpha (dB/km)': 0.20,
            'Loss ที่นักศึกษาคำนวณ (dB)': f"{r['loss']['answer']:.3f}" if r else 'ยังไม่กรอก',
            'Pout จาก Simulation (dBm)': f"{r['reference']:.3f}" if r else 'ยังไม่เปิดเผย',
            'Pout ที่นักศึกษาคำนวณ (dBm)': f"{r['answer']:.3f}" if r else 'ยังไม่กรอก',
            'Error (dB)': f"{r['error']:.3f}" if r else 'รอตรวจ',
            'ผลการตรวจ': evaluation(r) if r else 'รอตรวจ',
        })
    return rows


def show_table(rows):
    st.caption('เลื่อนภายในตารางในแนวนอนเพื่อดูทุกคอลัมน์')
    st.dataframe(rows, hide_index=True, width='stretch')


def show_result(result):
    st.write(evaluation(result))
    st.write(f"ค่าอ้างอิง: **{result['reference']:.3f} dBm** · ค่าของนักศึกษา: **{result['answer']:.3f} dBm**")
    st.write(f"ผลต่างสัมบูรณ์: **{result['error']:.3f} dB**")
    if 'loss' in result:
        loss = result['loss']
        st.write(f"Loss อ้างอิง: {loss['reference']:.3f} dB · ค่าของนักศึกษา: {loss['answer']:.3f} dB · "
                 f"ผลต่าง: {loss['error']:.3f} dB · {evaluation(loss)}")


def save_response(index):
    st.session_state['lab3_responses'][index] = st.session_state[f'lab3_response_{index}']


def render_theory():
    """Learning controls have their own keys and never write experiment results."""
    st.markdown('''<style>
    .st-key-lab3_theory_content [data-testid="stAlert"],
    .st-key-lab3_theory_content [data-testid="stAlertContainer"] {
        background: #132238; border: 1px solid #38516d;
    }
    </style>''', unsafe_allow_html=True)
    st.caption('เรียนรู้จากสูตร → ดูตัวอย่าง → ทดลองเปลี่ยนค่า → สังเกตผล '
               'กิจกรรมในแท็บนี้ไม่บันทึกเป็นครั้งทดลองและไม่เปลี่ยนคะแนน')
    st.markdown('#### 1. dBm และกำลังแสง')
    st.write('**dBm** คือระดับกำลังแสงแบบสัมบูรณ์ อ้างอิงกับ **1 mW**')
    st.info('0 dBm = 1 mW · dBm เป็นบวก: กำลังมากกว่า 1 mW · '
            'dBm เป็นลบ: กำลังน้อยกว่า 1 mW ไม่ใช่กำลังแสงติดลบ')
    st.markdown('**สูตร**')
    st.latex(r'P(\mathrm{dBm}) = 10\log_{10}(P_{\mathrm{mW}})')
    st.latex(r'P_{\mathrm{mW}} = 10^{P(\mathrm{dBm})/10}')
    st.caption('PmW ในสูตรคือค่าตัวเลขของกำลังในหน่วย mW โดยกำลังต้องมากกว่าศูนย์')
    st.markdown('**ตัวอย่างการคำนวณ**')
    with st.container(border=True):
        st.write('กำหนดให้ P = **10 mW** แทนค่าในสูตรแล้วคำนวณทีละขั้น')
        st.latex(r'\begin{aligned}P(\mathrm{dBm}) &= 10\log_{10}(10) \\'
                 r'&= 10\times 1 \\ &= 10\ \mathrm{dBm}\end{aligned}')
        st.write('อีกตัวอย่าง: P = **0.5 mW** ซึ่งน้อยกว่า 1 mW จึงได้ dBm เป็นลบ')
        st.latex(r'10\log_{10}(0.5)\approx -3.01\ \mathrm{dBm}')
    st.markdown('**ทดลองเปลี่ยนค่า — กำลังแสง mW เป็น dBm**')
    st.write('ทดลองเปลี่ยนค่ากำลังแสง แล้วดูผลทันที')
    mw = st.number_input('กำลังแสง P (mW)', min_value=0.001, max_value=1_000_000.0,
                         value=1.0, step=0.1, format='%.3f', key='lab3_theory_mw')
    st.metric('P(dBm)', f'{mw_to_dbm(mw):.2f} dBm')
    st.caption('ลอง 1 → 0 dBm · 2 → +3.01 dBm · 0.5 → −3.01 dBm · 10 → +10 dBm')

    st.markdown('**ทดลองเปลี่ยนค่า — dBm กลับเป็น mW**')
    st.write('ใช้สูตรผกผัน: นำค่า dBm หาร 10 แล้วใช้เป็นเลขชี้กำลังของ 10')
    dbm = st.number_input('ระดับกำลังแสง P (dBm)', min_value=-100.0, max_value=60.0,
                          value=0.0, step=1.0, key='lab3_theory_dbm')
    st.latex(r'P(\mathrm{mW}) = 10^{P(\mathrm{dBm})/10}')
    st.metric('P(mW)', f'{dbm_to_mw(dbm):.6g} mW')
    st.caption('ลอง 0 → 1 mW · +3 → ประมาณ 1.995 mW · −3 → ประมาณ 0.501 mW · +10 → 10 mW')

    st.divider()
    st.markdown('#### 2. dB คืออัตราส่วนกำลัง')
    st.write('**dB** เปรียบเทียบกำลังสองค่าแบบสัมพัทธ์ ต่างจาก dBm ที่อ้างอิงกับ 1 mW '
             'ให้ P1 เป็นกำลังก่อนหน้า และ P2 เป็นกำลังหลังจากนั้น โดยใช้หน่วยเดียวกัน')
    st.markdown('**สูตร**')
    st.latex(r'R = \frac{P_2}{P_1}')
    st.latex(r'\mathrm{dB} = 10\log_{10}\left(\frac{P_2}{P_1}\right)')
    st.markdown('- **0 dB** → กำลังเท่าเดิม\n'
                '- **+3 dB** → กำลังประมาณ 2 เท่า\n'
                '- **−3 dB** → กำลังประมาณครึ่งหนึ่ง\n'
                '- **+10 dB** → กำลัง 10 เท่า\n'
                '- **−10 dB** → กำลัง 1/10 เท่า')
    st.markdown('**ตัวอย่างการคำนวณ**')
    with st.container(border=True):
        st.write('กำหนดให้ P1 = **1 mW** และ P2 = **2 mW**')
        st.latex(r'R = \frac{2}{1} = 2')
        st.latex(r'10\log_{10}(2)\approx +3.01\ \mathrm{dB}')
        st.write('กำลังเพิ่มขึ้น 2 เท่า จึงเป็น Gain ประมาณ +3.01 dB')
    st.markdown('**ทดลองเปลี่ยนค่า — เปรียบเทียบกำลังสองค่า**')
    p1 = st.number_input('กำลังก่อนหน้า P1 (mW)', min_value=0.001, max_value=1_000_000.0,
                         value=1.0, step=0.1, format='%.3f', key='lab3_theory_p1')
    p2 = st.number_input('กำลังหลังจากนั้น P2 (mW)', min_value=0.001, max_value=1_000_000.0,
                         value=2.0, step=0.1, format='%.3f', key='lab3_theory_p2')
    ratio = p2 / p1
    gain_db = mw_to_dbm(ratio)
    st.metric('อัตราส่วนกำลัง R = P2/P1', f'{ratio:.6g} เท่า')
    st.metric('Gain/Loss (dB)', f'{gain_db:+.2f} dB')
    if gain_db > 0:
        st.info('Gain: P2 มากกว่า P1 จึงได้ dB เป็นบวก')
    elif gain_db < 0:
        st.info(f'Loss: P2 น้อยกว่า P1 จึงได้ dB เป็นลบ '
                f'(เทียบเป็นค่าการสูญเสียบวกได้ {abs(gain_db):.2f} dB)')
    else:
        st.info('0 dB: P2 เท่ากับ P1 กำลังไม่เปลี่ยนแปลง')

    st.divider()
    st.markdown('#### 3. การลดทอนในใยแก้วนำแสง')
    st.write('**α (dB/km)** คือการลดทอนต่อระยะทางหนึ่งกิโลเมตร และ **L (km)** '
             'คือความยาวใยแก้ว ในสูตรนี้ Loss ใช้ค่าบวกสำหรับการสูญเสีย '
             'จึงนำไปลบออกจากกำลังขาเข้า Pin เพื่อหากำลังขาออก Pout')
    st.markdown('**สูตร**')
    st.latex(r'\mathrm{Loss(dB)} = \alpha\mathrm{(dB/km)}\times L\mathrm{(km)}')
    st.latex(r'P_{out}\mathrm{(dBm)} = P_{in}\mathrm{(dBm)} - \mathrm{Loss(dB)}')
    st.markdown('**ตัวอย่างการคำนวณ**')
    with st.container(border=True):
        st.write('กำหนดให้ **Pin = 0 dBm**, **α = 0.20 dB/km**, **L = 10 km**')
        st.latex(r'\mathrm{Loss} = 0.20\times 10 = 2\ \mathrm{dB}')
        st.latex(r'P_{out} = 0 - 2 = -2\ \mathrm{dBm}')
        st.write('กำลังขาออกต่ำกว่า 1 mW เพราะสูญเสียกำลังไประหว่างทาง')
    st.markdown('**ทดลองเปลี่ยนค่า — ระยะทางและการลดทอน**')
    pin = st.number_input('กำลังขาเข้า Pin (dBm)', -60.0, 30.0, 0.0,
                          step=0.1, key='lab3_theory_pin')
    alpha = st.number_input('การลดทอน α (dB/km)', 0.0, 5.0, 0.20,
                            step=0.01, format='%.2f', key='lab3_theory_alpha')
    length = st.number_input('ความยาวใยแก้ว L (km)', 0.0, 100.0, 10.0,
                             step=1.0, key='lab3_theory_length')
    loss = fiber_loss(alpha, length)
    pout = output_power(pin, alpha, length)
    st.metric('Loss (dB)', f'{loss:.2f} dB')
    st.metric('Pout (dBm)', f'{pout:.2f} dBm')
    st.metric('Pout (mW)', f'{dbm_to_mw(pout):.6g} mW')
    st.caption(PROFILE_NOTE)
    st.markdown('#### สรุปความสัมพันธ์')
    st.info('L ↑ → Loss ↑ → Pout ↓\n\nα ↑ → Loss ↑ → Pout ↓')
    st.caption('เมื่อคงตัวแปรอื่นไว้: เพิ่ม L จะเพิ่ม Loss เมื่อ α > 0; '
               'เพิ่ม α จะเพิ่ม Loss เมื่อ L > 0 หาก L หรือ α เป็นศูนย์ Loss จะเป็นศูนย์')


def render_lab3():
    st.markdown('''<style>
    .stApp { background: #080f1c; color: #e5edf7; }
    .stApp h1,.stApp h2,.stApp h3,.stApp h4 { color: #b9d8ff; }
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"],.stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stLatex"],.stApp [data-testid="stCaptionContainer"] *,
    .stApp .lab-kicker,.stApp [data-testid="stMarkdownContainer"] p.instructor { color: #e5edf7; }
    .stApp [data-testid="stMetric"] { background: #132238; }
    .stApp [data-testid="stMetricValue"],.stApp [data-testid="stMetricValue"] * { color: #b9d8ff; }
    .stApp [role="tab"] { background: #132238; color: #e5edf7; padding: 0.5rem; }
    .stApp [role="tablist"] { overflow-x: auto; }
    .stApp [data-testid="stFormSubmitButton"] button { min-height: 44px; }
    .stApp [data-testid="stVerticalBlock"], .stApp [data-testid="stElementContainer"] { min-width: 0; }
    .stApp [data-testid="stMetricValue"] { overflow-wrap: anywhere; }
    </style>''', unsafe_allow_html=True)
    st.markdown('### การทดลองที่ 3 กำลังแสง dB, dBm และการลดทอนในใยแก้วนำแสง')
    st.caption('Optical Power, dB, dBm and Fiber Attenuation')
    powers = st.session_state.setdefault('lab3_power_results', {})
    fibers = st.session_state.setdefault('lab3_fiber_results', {})
    responses = st.session_state.setdefault('lab3_responses', {})
    theory, review, simulation, experiment, summary = st.tabs([
        '📘 ทฤษฎี', '🔄 ทบทวน dB/dBm', '🔦 Simulation',
        '🧪 การทดลองและบันทึกผล', '📊 สรุปผล',
    ])
    with theory:
        with st.container(key='lab3_theory_content'):
            render_theory()
    with review:
        st.write('เริ่มจากกำลังหน่วย mW → หาค่า log10 → คูณ 10 เพื่อได้ dBm')
        st.write('แปลงกลับโดยนำ dBm หาร 10 แล้วใช้เป็นเลขชี้กำลังของ 10')
        st.info('จุดอ้างอิงสำคัญ: 0 dBm = 1 mW')
        st.write('dB เปรียบเทียบกำลังสองค่า ส่วน dBm ระบุกำลังเทียบกับ 1 mW; จึงลบ Loss (dB) ออกจาก Pin (dBm) ได้')
        st.write('ลองคำนวณด้วยตนเองในแท็บการทดลอง เฉลยแต่ละข้อจะแสดงหลังส่งคำตอบ')
    with simulation:
        st.caption(PROFILE_NOTE)
        profile = st.selectbox('Wavelength/Profile — ค่าตัวอย่างสำหรับการเรียนรู้', list(TEACHING_PROFILES), index=2, key='lab3_sim_profile')
        st.write(f'ค่า alpha ตัวอย่างของโปรไฟล์นี้ = {TEACHING_PROFILES[profile]:.2f} dB/km')
        pin = st.number_input('กำลังแสงขาเข้า Pin (dBm)', -60.0, 30.0, 0.0, step=0.1, key='lab3_sim_pin')
        length = st.number_input('ระยะทาง Fiber (km)', 0.0, 100.0, 10.0, step=1.0, key='lab3_sim_length')
        alpha = st.number_input('Attenuation alpha (dB/km)', 0.0, 5.0,
                                value=TEACHING_PROFILES[profile], step=0.01,
                                key=f'lab3_sim_alpha_{profile}')
        pout = output_power(pin, alpha, length)
        st.metric('Total Loss (dB)', f'{fiber_loss(alpha, length):.3f}')
        st.metric('Output Power (dBm)', f'{pout:.3f}')
        st.metric('Output Power (mW)', f'{dbm_to_mw(pout):.5g}')
        distances = [max(20.0, length) * i / 100 for i in range(101)]
        st.line_chart(pd.DataFrame({'Fiber Length (km)': distances,
                                    'Output Power (dBm)': [output_power(pin, alpha, x) for x in distances]}),
                      x='Fiber Length (km)', y='Output Power (dBm)', width='stretch')
        st.caption('Simulation เป็นเครื่องมือสำรวจอิสระ ค่าที่นี่ไม่บันทึกเป็นผลการทดลอง')
    with experiment:
        st.write('คำนวณด้วยตนเองก่อนส่งคำตอบ ตรวจด้วยผลต่างสัมบูรณ์ ≤ 0.1 dB ทั้ง dBm และ Loss ไม่ใช้เปอร์เซ็นต์บนค่า dBm')
        st.markdown('#### ส่วนที่ 1 — mW และ dBm')
        power = st.selectbox('เลือกกำลังแสง (mW)', POWER_TRIALS, key='lab3_power_trial')
        with st.form(f'lab3_power_form_{power}'):
            answer = st.number_input('dBm ที่นักศึกษาคำนวณ', value=None, placeholder='ยังไม่กรอก', key=f'lab3_power_answer_{power}')
            submitted = st.form_submit_button('ส่งคำตอบส่วนที่ 1', width='stretch')
        if submitted:
            try:
                powers[power] = check_db_answer(answer, mw_to_dbm(power))
            except ValueError as error:
                st.error(str(error))
        if power in powers:
            show_result(powers[power])
        show_table(power_rows(powers))
        st.markdown('#### ส่วนที่ 2 — ระยะทางและการลดทอน')
        st.write(f'{DEFAULT_PROFILE} · Pin = 0 dBm · alpha = 0.20 dB/km')
        st.caption(PROFILE_NOTE)
        length = st.selectbox('เลือกระยะทางทดลอง (km)', LENGTH_TRIALS, key='lab3_length_trial')
        with st.form(f'lab3_fiber_form_{length}'):
            loss_answer = st.number_input('Loss ที่นักศึกษาคำนวณ (dB)', value=None, placeholder='ยังไม่กรอก', key=f'lab3_loss_{length}')
            pout_answer = st.number_input('Pout ที่นักศึกษาคำนวณ (dBm)', value=None, placeholder='ยังไม่กรอก', key=f'lab3_pout_{length}')
            submitted = st.form_submit_button('ส่งคำตอบส่วนที่ 2', width='stretch')
        if submitted:
            try:
                fibers[length] = check_fiber_trial(length, loss_answer, pout_answer)
            except ValueError as error:
                st.error(str(error))
        if length in fibers:
            show_result(fibers[length])
        show_table(experiment_rows(fibers))
        st.caption('ส่งซ้ำจะแทนคำตอบเดิม ไม่เพิ่มจำนวนครั้ง; ผลเก็บเฉพาะเซสชันนี้ แยกจาก Lab 1 และ Lab 2')
        st.markdown('#### คำถามวิเคราะห์ผล')
        for index, question in enumerate(QUESTIONS, 1):
            st.text_area(f'{index}. {question}', value=responses.get(index, ''),
                         key=f'lab3_response_{index}', on_change=save_response, args=(index,))
    with summary:
        all_results = {**{f'power_{k}': v for k, v in powers.items()}, **{f'fiber_{k}': v for k, v in fibers.items()}}
        completed, correct, average = summarize(all_results)
        st.metric('จำนวนครั้งที่ส่งคำตอบแล้ว', f'{completed} / 10')
        st.metric('จำนวนคำตอบถูก', f'{correct} / 10')
        st.metric('ผลต่างสัมบูรณ์เฉลี่ย (dB)', 'รอตรวจ' if average is None else f'{average:.3f}')
        st.caption('ค่าเฉลี่ยใช้คำตอบ dBm ล่าสุดทั้งสองส่วน; ส่วนที่ 2 ต้องถูกทั้ง Loss และ Pout จึงนับว่าถูก')
        show_table(power_rows(powers))
        show_table(experiment_rows(fibers))
        st.write('ระยะทางเพิ่ม → Loss เพิ่ม (เมื่อ alpha > 0)')
        st.write('alpha เพิ่ม → Loss เพิ่ม (เมื่อระยะทาง > 0)')
        st.write('Loss เพิ่ม → Output Power ลดลง')
        st.write('สรุป: เลือกช่วง wavelength และใยแก้วที่มี attenuation ต่ำ ช่วยลดการสูญเสียที่ระยะทางเท่ากันและช่วยให้ส่งได้ไกลขึ้นภายใต้ข้อจำกัดกำลังรับ')
        for index, question in enumerate(QUESTIONS, 1):
            st.write(f'**{index}. {question}**')
            st.write(responses.get(index) or 'ยังไม่กรอก')
