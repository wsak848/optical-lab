"""Thai-first Lab 2; reference answers are revealed per submitted medium only."""
import streamlit as st

from core.optical_calculations import SPEED_OF_LIGHT_M_S
from core.refractive_index import MEDIA, check_calculation, summarize

QUESTIONS = [
    'ตัวกลางใดทำให้แสงเดินทางเร็วที่สุด?',
    'ตัวกลางใดทำให้แสงเดินทางช้าที่สุด?',
    'เมื่อค่า n เพิ่มขึ้น ความเร็วของแสงเปลี่ยนอย่างไร?',
    'เพราะเหตุใดแสงใน Optical Fiber จึงเดินทางช้ากว่าในอากาศ?',
    'Fused Silica มีความเร็วแสงประมาณกี่เปอร์เซ็นต์ของ c?',
]


def experiment_rows(results):
    """Build a complete five-trial table without exposing pending answers."""
    rows = []
    for index, (medium, n) in enumerate(MEDIA.items(), 1):
        result = results.get(medium)
        rows.append({
            'ครั้งที่': index, 'ตัวกลาง': medium, 'Refractive Index (n)': n,
            'ความเร็วจาก Simulation (m/s)': result['reference'] if result else None,
            'ความเร็วที่นักศึกษาคำนวณ (m/s)': result['answer'] if result else None,
            'Error (%)': result['error'] if result else None,
            'ผลการตรวจ': evaluation(result) if result else 'รอคำตอบ',
        })
    return rows


def evaluation(result):
    return '✓ ถูกต้อง' if result['correct'] else 'ตรวจสอบการคำนวณอีกครั้ง'


def show_table(results):
    st.caption('เลื่อนตารางในแนวนอนเพื่อดูทุกคอลัมน์ · ซ่อนค่าอ้างอิงจนกว่าจะส่งคำตอบของตัวกลางนั้น')
    st.dataframe(experiment_rows(results), hide_index=True, width='stretch',
                 column_config={
                     'ความเร็วจาก Simulation (m/s)': st.column_config.NumberColumn(format='%.2f'),
                     'ความเร็วที่นักศึกษาคำนวณ (m/s)': st.column_config.NumberColumn(format='%.2f'),
                     'Error (%)': st.column_config.NumberColumn(format='%.4f'),
                 })


def render_lab2():
    st.markdown('### การทดลองที่ 2 ดัชนีหักเหและความเร็วแสงในตัวกลาง')
    st.caption('Refractive Index and Speed of Light in Media')
    results = st.session_state.setdefault('lab2_results', {})
    epoch = st.session_state.get('lab2_epoch', 0)
    theory, indices, experiment, summary = st.tabs([
        '📘 ทฤษฎี', '🔍 ตารางดัชนีหักเห', '🧪 การทดลองและบันทึกผล', '📊 สรุปผล',
    ])
    with theory:
        with st.container(border=True):
            st.latex(r'v = \frac{c}{n}')
            st.write('v = ความเร็วแสงในตัวกลาง (m/s) · c = ความเร็วแสงในสุญญากาศ · n = ดัชนีหักเห (ไม่มีหน่วย)')
            st.latex(r'c = 3.0 \times 10^8\ \mathrm{m/s}')
            st.write('เมื่อ n เพิ่มขึ้น → ความเร็วแสง v ลดลง เพราะ v แปรผกผันกับ n')
            st.write('แสงเดินทางเร็วที่สุดในสุญญากาศ (n = 1) เมื่อเปรียบเทียบกับตัวกลางทั้งห้าในบททดลองนี้')
            st.write('ดัชนีหักเหขึ้นอยู่กับชนิดวัสดุและความยาวคลื่นของแสง')
            st.caption('ค่าดัชนีหักเหในบททดลองนี้เป็นค่าอ้างอิงโดยประมาณเพื่อการศึกษา ไม่ใช่ค่าคงที่สำหรับทุกความยาวคลื่น')
    with indices:
        st.write('ใช้ค่าดัชนีหักเหต่อไปนี้ในการคำนวณด้วยตนเอง')
        st.dataframe([{'ตัวกลาง': name, 'Refractive Index (n)': n} for name, n in MEDIA.items()],
                     hide_index=True, width='stretch', column_config={
                         'Refractive Index (n)': st.column_config.NumberColumn(format='%.4f')})
        st.caption('ค่าอ้างอิงโดยประมาณเพื่อการศึกษา · ค่า n เปลี่ยนตามวัสดุและความยาวคลื่น')
    with experiment:
        st.markdown('#### ทดลอง 5 ครั้ง: ตัวกลางละหนึ่งครั้ง')
        st.write('เลือกตัวกลาง → คำนวณ v ด้วยตนเอง → กรอกคำตอบ → ตรวจสอบผล สามารถแก้คำตอบของตัวกลางเดิมได้โดยไม่เพิ่มจำนวนครั้ง')
        medium = st.selectbox('เลือกตัวกลาง', list(MEDIA), key=f'lab2_medium_{epoch}')
        st.write(f'ตัวกลาง: **{medium}** · ดัชนีหักเห n = **{MEDIA[medium]}**')
        st.latex(r'v = \frac{c}{n},\qquad c = 3.0 \times 10^8\ \mathrm{m/s}')
        st.caption('ยอมรับการปัดเศษ: Error ≤ 0.5% · กรอกได้ทั้ง 225000000 และ 2.25e8')
        with st.form(f'lab2_form_{epoch}_{medium}'):
            answer = st.number_input('ค่าความเร็วแสงที่คำนวณได้ (m/s)', min_value=0.0,
                                     value=None, format='%.2f', placeholder='กรอกผลที่คำนวณเอง',
                                     key=f'lab2_answer_{epoch}_{medium}')
            submitted = st.form_submit_button('ตรวจสอบผลการคำนวณ', width='stretch')
        if submitted:
            try:
                results[medium] = check_calculation(medium, answer)
            except ValueError as error:
                st.error(str(error))
        if medium in results:
            result = results[medium]
            st.write(evaluation(result))
            st.write(f"ค่าอ้างอิง: {result['reference']:,.2f} m/s")
            st.write(f"ผลต่าง (ค่าสัมบูรณ์): {result['difference']:,.2f} m/s · Error: {result['error']:.4f}%")
        st.write('Error (%) = ผลต่างสัมบูรณ์ ÷ ค่าอ้างอิง × 100')
        show_table(results)
        st.markdown('#### คำถามวิเคราะห์ผล')
        for index, question in enumerate(QUESTIONS, 1):
            st.text_area(f'{index}. {question}', key=f'lab2_response_{epoch}_{index}')
        st.caption('ข้อมูลเก็บชั่วคราวในเซสชันนี้ · เริ่มใหม่จะล้างเฉพาะข้อมูล Lab 2')
        if st.button('เริ่มการทดลองใหม่', key='lab2_reset', width='stretch'):
            st.session_state['lab2_results'] = {}
            st.session_state['lab2_epoch'] = epoch + 1
            st.rerun()
    with summary:
        completed, correct, average = summarize(results)
        st.metric('จำนวนครั้งที่ส่งคำตอบแล้ว', f'{completed} / 5')
        st.metric('จำนวนครั้งที่ถูกต้อง', correct)
        st.metric('Error เฉลี่ย (%)', '—' if average is None else f'{average:.4f}%')
        st.caption('นับคำตอบล่าสุดของแต่ละตัวกลาง รวมทั้งคำตอบที่ยังต้องแก้ไข')
        show_table(results)
        st.write('สรุป: n เพิ่มขึ้น → v ลดลง (n increases → v decreases)')
        st.latex(r'\frac{v}{c} \times 100\%')
        st.write('เปรียบเทียบความเร็วแสงในแต่ละตัวกลางกับสุญญากาศ (100%) หลังส่งคำตอบของตัวกลางนั้น')
        st.dataframe([{'ตัวกลาง': medium, 'ความเร็วเทียบกับ c (%)':
                       results[medium]['reference'] / SPEED_OF_LIGHT_M_S * 100 if medium in results else None}
                      for medium in MEDIA], hide_index=True, width='stretch', column_config={
                          'ความเร็วเทียบกับ c (%)': st.column_config.NumberColumn(format='%.2f')})
