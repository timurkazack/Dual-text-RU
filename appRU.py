import cadquery as cq
import streamlit as st
import os
import time
from streamlit_stl import stl_from_file


def letter(let, angle, fontPath=""):
    """Extrude a letter, center it and rotate of the input angle"""
    wp = (cq.Workplane('XZ')
          .text(let, fontsize, extr, fontPath=fontPath, valign='bottom')
          )
    b_box = wp.combine().objects[0].BoundingBox()
    x_shift = -(b_box.xlen / 2 + b_box.xmin)
    wp = (wp.translate([x_shift, extr / 2, 0])
          .rotate((0, 0, 0), (0, 0, 1), angle)
          )
    return wp


def dual_text(text1, text2, fontPath='', save='stl', b_h=2, b_pad=2, b_fil_per=0.8, space_per=0.3, export_name='file'):
    """Generate the dual letter illusion from the two text and save it"""
    space = fontsize * space_per
    res = cq.Assembly()
    last_ymax = 0
    for ind, ab in enumerate(zip(text1, text2)):
        try:
            a = letter(ab[0], 45, fontPath=fontPath)
            b = letter(ab[1], 135, fontPath=fontPath, )
            a_inter_b = a & b
            b_box = a_inter_b.objects[0].BoundingBox()
            a_inter_b = a_inter_b.translate([0, -b_box.ymin, 0])
            if ind:
                a_inter_b = a_inter_b.translate([0, last_ymax + space, 0])
            last_ymax = a_inter_b.objects[0].BoundingBox().ymax
            res.add(a_inter_b)
        except:
            last_ymax += space * 1.5

    b_box = res.toCompound().BoundingBox()
    res.add(cq.Workplane()
            .box(b_box.xlen + b_pad * 2, b_box.ylen + b_pad * 2, b_h, centered=(1, 0, 0))
            .translate([0, -b_pad, -b_h])
            .edges('|Z')
            .fillet(b_box.xlen / 2 * b_fil_per)
            )

    res = res.toCompound()
    res = res.translate([0, -b_box.ylen / 2, 0])

    cq.exporters.export(res, f'file_display.stl')
    cq.exporters.export(res, f"{export_name}.{save}")


if __name__ == "__main__":
    for file in os.listdir():
        if 'file' in file:
            try:
                os.remove(file)
            except:
                print(f'Cannot remove file {file}')

    st.title('Dual Text RU: Илюзия двойного текста')
    st.write("Создайте собственную иллюзию из двух слов, 3d-амбиграмму! Если вам понравился проект [поддержите меня "
             "средствами на дошик]"
             "(https://boosty.to/timurcode/donate))!",
             unsafe_allow_html=True)
    st.write("Веб-приложение поддерживает все [шрифты Google] (https://fonts.google.com/).",
             unsafe_allow_html=True)
    st.write("Афтор [TimurCode](https://github.com/timurkazack).",
             unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        text1 = st.text_input('Первый текст', value="HAPPY")
    with col2:
        text2 = st.text_input('Второй текст', value="2025!")
    with col3:
        fontsize = st.number_input('Размер шрифта', min_value=1, max_value=None, value=20)
        extr = fontsize * 2

    if len(text1) != len(text2):
        st.warning("Эти два текста не имеют одинаковой длины, лишние буквы будут вырезаны", icon="⚠️")
    if not text1.isupper() or not text2.isupper():
        st.warning("Незаглавные буквы и буквы разной высоты приводят к плохим результатам", icon="⚠️")

    col1, col2, col3 = st.columns(3)

    font_dir = os.listdir('fonts')
    with col1:
        font_name = st.selectbox('Выберите шрифт', ['lato'] + sorted(font_dir))
    with col2:
        font_type_list = [f for f in os.listdir('fonts' + os.sep + font_name) if '.ttf' in f and '-' in f]

        if font_type_list:
            font_start_name = font_type_list[0].split('-')[0]
            font_type_list_name = [f.split('-')[1].strip('.ttf') for f in font_type_list]
            font_type = st.selectbox('Тип шрифта', sorted(font_type_list_name))
            font_type_pathname = font_start_name + '-' + font_type + '.ttf'
            font_path = 'fonts' + os.sep + font_name + os.sep + font_type_pathname
        else:
            font_type_list = [f for f in os.listdir('fonts' + os.sep + font_name) if '.ttf' in f]
            font_type = st.selectbox('Тип шрифта', sorted(font_type_list))
            font_path = 'fonts' + os.sep + font_name + os.sep + font_type
    with col3:
        space = st.slider('Пробел в буквах (%)', 0, 200, step=1, value=30) / 100

    col1, col2, col3 = st.columns(3)
    with col1:
        b_h = st.slider('Высота базового основания', 0.0, fontsize / 2, step=0.1, value=1.0)
    with col2:
        b_pad = st.slider('Размах базового основания', 0.0, fontsize / 2, step=0.1, value=2.0)
    with col3:
        b_fil_per = st.slider('Скруглённость базового основания (%)', 0, 100, step=1, value=80) / 100

    col1, _, _ = st.columns(3)
    with col1:
        out = st.selectbox('Тип выходного файла', ['stl', 'step'])

    if st.button('Рендер'):
        start = time.time()
        with st.spinner('Пожалуйста подождите...'):
            dual_text(text1, text2, fontPath=font_path, save=out, b_h=b_h, b_pad=b_pad, b_fil_per=b_fil_per,
                      space_per=space)
        end = time.time()
        if f'file.{out}' not in os.listdir():
            st.error('Программа не смогла создать сетку.', icon="🚨")
        else:
            st.success(f'Отрендеренно за {int(end - start)} с.', icon="✅")
            with open(f'file.{out}', "rb") as file:
                btn = st.download_button(
                    label=f"Скачать {out}",
                    data=file,
                    file_name=f'TextTangoRu_{text1}_{text2}_{font_name}-{font_type}.{out}',
                    mime=f"model/{out}"
                )

            stl_from_file('file_display.stl')