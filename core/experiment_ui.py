import streamlit as st

from core.experiment import check_trial, create_trial, summarize


QUESTIONS = [
    "เมื่อความยาวคลื่นเพิ่มขึ้น ความถี่เปลี่ยนแปลงอย่างไร?",
    "ระหว่าง 850 nm และ 1550 nm ค่าใดมีความถี่สูงกว่า เพราะเหตุใด?",
    "ความสัมพันธ์ระหว่างความยาวคลื่นและความถี่เป็นแบบแปรตรงหรือแปรผกผัน?",
    "ค่าที่คำนวณด้วยตนเองแตกต่างจาก Simulation หรือไม่ และเพราะเหตุใด?",
]


def show_table(trials):
    if not trials:
        st.info("ยังไม่มีข้อมูลการทดลอง")
        return
    rows = []
    for index, trial in enumerate(trials, 1):
        checked = trial['student_thz'] is not None
        rows.append({
            'ครั้งที่': index,
            'ความยาวคลื่นจากการทดลอง λ (nm)': trial['wavelength_nm'],
            'ความยาวคลื่นที่แปลงเป็นเมตร (m)': f"{trial['wavelength_m']:.3e}",
            'ความถี่จาก Simulation (THz)': trial['simulation_thz'] if checked else None,
            'ความถี่ที่นักศึกษาคำนวณเอง (THz)': trial['student_thz'],
            'ผลต่าง': trial['difference'],
            'Error (%)': trial['percent_error'],
            'ผลการตรวจ': ('✓ ถูกต้อง' if trial['correct'] else 'ตรวจสอบการคำนวณอีกครั้ง') if checked else 'รอคำตอบ',
        })
    st.caption("เลื่อนตารางในแนวนอนเพื่อดูทุกคอลัมน์ · ผลต่างมีหน่วย THz · ซ่อนค่าอ้างอิงจนกว่าจะส่งคำตอบ")
    st.dataframe(rows, hide_index=True, width='stretch', column_config={
        'ความถี่จาก Simulation (THz)': st.column_config.NumberColumn(format='%.4f'),
        'ความถี่ที่นักศึกษาคำนวณเอง (THz)': st.column_config.NumberColumn(format='%.4f'),
        'ผลต่าง': st.column_config.NumberColumn(format='%.4f'),
        'Error (%)': st.column_config.NumberColumn(format='%.4f'),
    })


def render_experiment(wavelength_nm):
    trials = st.session_state.setdefault('experiment_trials', [])
    epoch = st.session_state.get('experiment_epoch', 0)
    st.markdown('#### การทดลอง: เปรียบเทียบการคำนวณด้วยตนเองกับ Simulation')
    st.write('ทดลองประมาณ 5 ครั้ง: แนะนำ 850, 1000, 1310, 1550 nm และอีกหนึ่งค่าที่เลือกเอง')
    st.write('1. ไปที่แท็บ Simulation เลือกความยาวคลื่นด้วย slider หรือปุ่ม preset เดิม แล้วกลับมาบันทึกค่า')
    st.write('2. คำนวณด้วยตนเองก่อนเปิดดูคำตอบใน Simulation แล้วกรอกและส่งคำตอบทีละการทดลอง')
    st.caption('Simulation ยังคงแสดงผลตามเดิม ส่วนตารางการทดลองจะเปิดเผยค่าอ้างอิงเฉพาะครั้งที่ส่งคำตอบแล้ว')
    st.write(f'ความยาวคลื่นที่เลือกอยู่: **{wavelength_nm:,} nm**')
    if st.button('บันทึกค่าจากการทดลอง', key='experiment_record'):
        trials.append(create_trial(wavelength_nm))
        st.session_state['experiment_trials'] = trials
    st.latex(r'f = \frac{c}{\lambda}')
    st.write('ใช้ c = 3.0 × 10⁸ m/s และ λ (m) = λ (nm) × 10⁻⁹')
    st.caption('แปลง Hz เป็น THz โดยหารด้วย 10¹² · ยอมรับความคลาดเคลื่อนจากการปัดเศษไม่เกิน 0.5%')
    if trials:
        selected = st.selectbox('เลือกครั้งที่ต้องการกรอกหรือตรวจคำตอบ', range(len(trials)),
                                format_func=lambda i: f"ครั้งที่ {i + 1} · {trials[i]['wavelength_nm']} nm",
                                key=f'experiment_selected_{epoch}')
        with st.form(f'experiment_form_{epoch}_{selected}'):
            answer = st.number_input('ค่าความถี่ที่คำนวณได้ด้วยตนเอง (THz)',
                                     value=None, min_value=0.0, step=0.01, format='%.4f',
                                     placeholder='กรอกผลที่คำนวณเอง', key=f'experiment_answer_{epoch}_{selected}')
            submitted = st.form_submit_button('ตรวจสอบผลการคำนวณ')
        if submitted:
            try:
                trials[selected] = check_trial(trials[selected], answer)
                st.session_state['experiment_trials'] = trials
            except ValueError as error:
                st.error(str(error))
        if trials[selected]['student_thz'] is not None:
            checked = trials[selected]
            st.write('✓ ถูกต้อง' if checked['correct'] else 'ตรวจสอบการคำนวณอีกครั้ง')
            st.write(f"ค่าอ้างอิง {checked['simulation_thz']:.4f} THz · ผลต่าง {checked['difference']:.4f} THz · Error {checked['percent_error']:.4f}%")
    show_table(trials)
    st.markdown('#### คำถามวิเคราะห์ผล')
    for index, question in enumerate(QUESTIONS, 1):
        st.text_area(f'{index}. {question}', key=f'experiment_response_{epoch}_{index}')
    st.caption('ข้อมูลเก็บชั่วคราวในเซสชันนี้ การเริ่มใหม่จะล้างเฉพาะข้อมูลและคำตอบการทดลอง')
    if st.button('เริ่มการทดลองใหม่', key='experiment_reset'):
        # Clear widget state before constructing the next experiment view.
        st.session_state['experiment_trials'] = []
        st.session_state['experiment_epoch'] = epoch + 1
        st.rerun()


def render_summary():
    trials = st.session_state.get('experiment_trials', [])
    completed, correct, average = summarize(trials)
    st.markdown('#### สรุปผลการทดลอง')
    st.metric('จำนวนครั้งที่ส่งคำตอบแล้ว', completed)
    st.metric('จำนวนครั้งที่ถูกต้อง', correct)
    st.metric('Error เฉลี่ย (%)', '—' if average is None else f'{average:.4f}%')
    st.caption('นับเฉพาะครั้งที่ส่งคำตอบสำเร็จ · ใช้คำตอบที่ส่งล่าสุดของแต่ละครั้ง')
    show_table(trials)
    st.write('สรุปการเรียนรู้: เมื่อ c = 3.0 × 10⁸ m/s คงที่ ความยาวคลื่นและความถี่แปรผกผันกัน')
    st.write('ความยาวคลื่นเพิ่มขึ้น → ความถี่ลดลง · ความยาวคลื่นลดลง → ความถี่เพิ่มขึ้น')
