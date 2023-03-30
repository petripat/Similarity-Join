import streamlit as st
import cv2
import euclidian


@st.cache
def getColumnFromMap(map_photos, uploaded_file1, currentPhoto):
    tmp = {}
    for i in uploaded_file1:
        tmp[i.name] = map_photos[i.name][currentPhoto]
    return tmp

# modul identifikace spojeni a vykresleni obrazku podle rozsahoveho a kNN predikatu
def showSimilar(map, file, type, value):
    for photo in file:
        st.write("Photo")
        st.image(euclidian.rescalePhoto(cv2.imread(photo.name), True), channels='BGR', output_format='JPEG')
        st.write("Similar")
        tmp = map[photo.name]
        print("dectionary for " + photo.name)
        print(tmp)  # todo is it sorted correctly - min to max
        keys = sorted(tmp)
        print("Sorted closest pictures")
        print(keys)
        if type == 'kNN':
            keys = keys[:value]
        else:
            range_val = euclidian.giveRangeValue(value)
            i = 0
            for key in keys:
                if euclidian.isInRange(tmp[key], range_val):
                    i += 1
                else:
                    break
            keys = keys[:i]
        st.image([euclidian.rescalePhoto(cv2.imread(i), True) for i in keys], channels='BGR', output_format='JPEG')


def run():
    dict1 = {}
    map_photos = {}
    map_photos2 = {}
    st.info("Upload two databases of photos - folders.")
    #MODUL vlozeni dvou datovych sad obrazku
    uploaded_file1 = st.file_uploader('Upload first set of images', accept_multiple_files=True)
    uploaded_file2 = st.file_uploader('Upload second set of images', accept_multiple_files=True)
    if len(uploaded_file1) != 0 and len(uploaded_file2) != 0:
        sim = st.radio("Select type of query", ['range', 'kNN'], 1)
        if sim == 'kNN':
            value = st.slider('What kNN?', min_value=0, max_value=10, step=1)
        else:
            value = st.slider('What range?', min_value=float(0), max_value=float(1), step=0.1)
        for photo in uploaded_file1:
            map_photos[photo.name] = euclidian.getSimilarPhotos(photo, uploaded_file2)
        for i in uploaded_file2:
            map_photos2[i.name] = getColumnFromMap(map_photos, uploaded_file1, i.name)
        print("Map2: ")
        print(map_photos2)
        agree1 = st.checkbox('Show similar images based on first folder')
        agree2 = st.checkbox('Show similar images based on second folder')
        if agree1:
            showSimilar(map_photos, uploaded_file1, sim, value)
        if agree2:
            showSimilar(map_photos2, uploaded_file2, sim, value)
        # if st.button('Show similar images based on first folder'):
        #     showSimilar(map_photos, uploaded_file1, sim, value)
        # if st.button('Show similar images based on second folder'):
        #     showSimilar(map_photos2, uploaded_file2, sim, value)
