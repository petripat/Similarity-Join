import cv2
import math
import streamlit as st

PHOTO_HEIGHT = 500
COUNT_DESCRIPTORS = 500


# gets ration of successfull matches
def get_ratio(count_matches, count_desc1, count_desc2):
    if count_desc1 < count_desc2:
        print("Descriptors", count_desc1)
        return count_matches / count_desc1
    else:
        print("Descriptors", count_desc2)
        return count_matches / count_desc2


# rescales photo if it is too big
def rescalePhoto(image, printWeb: bool = False):
    if printWeb:
        desired_height = 200
    else:
        desired_height = PHOTO_HEIGHT
    if image.shape[1] > desired_height:
        height = desired_height
        scale = desired_height / image.shape[1]
        width = image.shape[0] * scale
        return cv2.resize(image, (int(height), int(width)), interpolation=cv2.INTER_CUBIC)
    else:
        return image


# counts distance between two descriptors
# modul prirazeni podobnosti - Euclidian distance cast 1/2
def Euclidian_distance(vector_photo1, vector_photo2):
    return math.sqrt(sum([(i - j) ** 2 for i, j in zip(vector_photo1, vector_photo2)]))


# returns similarity of two photos based on Euclidian distance using number of matches their distance
# and ration between successfull matching and descriptors in image
# modul prirazeni podobnosti obrazku - zpracovani EC cast 2/2
def similarFromEuclidian(sum, len, ratio):
    return ((sum / (len + 1)) / (len + 1)) - ratio


# main function that gets similarity for all photos from folder 2 to one photo in folder 1 and returns
# dictionary of {name of photo, similarity value}
# MODUL extrakce a vyuziti deskriptoru z obraku
@st.cache
def getSimilarPhotos(original, uploaded_file):
    img1 = rescalePhoto(cv2.imread(original.name))
    ret_dict = {}
    sift = cv2.SIFT_create(COUNT_DESCRIPTORS, contrastThreshold=0.08, edgeThreshold=8)
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    treshold = 0.7
    for i in uploaded_file:
        photo2 = i.name
        img2 = rescalePhoto(cv2.imread(photo2))
        keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
        # two best matches = smallest distance
        e_distance = []
        min_distance = -1
        sum_matches = 0
        matches_len = 0
        for i in descriptors1:
            e_distance.clear()
            setUpMin2 = False
            setUpMin = False
            for j in descriptors2:
                # the higher value, the more similar picture, pro 1 -> stejny obrazek
                distance = Euclidian_distance(i, j)
                # zefektivněni, nepridavam kazdou euklidovskou vzdalenost, ale jiz pouze mensi, abych nemusela tolik sortit
                if setUpMin2 is False:
                    if setUpMin is False:
                        setUpMin = True
                        min_distance = distance
                        e_distance.append(distance)
                    else:
                        setUpMin2 = True
                        e_distance.append(distance)
                        if distance < min_distance:
                            min_distance = distance
                else:
                    if distance < min_distance:
                        e_distance.append(distance)
                        min_distance = distance
            e_distance.sort()
            if e_distance[1] == 0:
                match = 0
            else:
                match = e_distance[0] / e_distance[1]
            if match < treshold:
                matches_len += 1
                sum_matches += match
        if matches_len == 0:
            ret_dict[photo2] = 1
        else:
            ret_dict[photo2] = similarFromEuclidian(sum_matches, matches_len,
                                                    get_ratio(matches_len, len(descriptors2), len(descriptors1)))
    return ret_dict


# transform given range to my similarity value
def giveRangeValue(similarity_value):
    if similarity_value >= 1:
        return -1
    if similarity_value >= 0.9:
        return -0.8
    if similarity_value >= 0.8:
        return -0.6
    if similarity_value >= 0.7:
        return -0.4
    if similarity_value >= 0.6:
        return -0.2
    if similarity_value >= 0.5:
        return 0.0
    if similarity_value >= 0.4:
        return 0.2
    if similarity_value >= 0.3:
        return 0.4
    if similarity_value >= 0.2:
        return 0.6
    if similarity_value >= 0.1:
        return 0.8
    if similarity_value >= 0:
        return 1


# decides if photo is similar based on given range value and my counted similar value
def isInRange(similarityValue, rangeValue):
    if similarityValue < rangeValue:
        return True
    return False
