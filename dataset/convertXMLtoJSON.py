"""
converterXMLtoJSON
Detect all annotations in xml files (bounding boxes) and convert to json (polygon shape)
It works for one class in Mask R-CNN

@author Adonis Gonzalez

"""

import xml.etree.cElementTree as ET
import json
import os
from os import listdir
from os.path import join

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
train_dir = os.path.join(ROOT_DIR, "train")
val_dir = os.path.join(ROOT_DIR, "val")
paths = [train_dir, val_dir]


def has_files(path: str) -> bool:
    """
    Checks if there is any file in the given path.
    If not files, is not possible continue.

    :param path: A str like /to/path/
    :return: A bool True/False
    """
    return any([j for j in listdir(path) if j.endswith('.jpg')])


def list_images(path: str) -> list:
    """
    Return a list of files that ends with .txt extension

    :param path: A str like /to/path/
    :return: A list that contains all found files
    """
    return [j for j in listdir(path) if j.endswith('.jpg')]


def save_images_log(path: str):
    """
    Save a list of images in a specific path.

    :param path: A str like /to/path/
    """
    if not has_files(path):
        print("Not images found, try using other path or adding images")
        exit(0)
    else:
        images = list_images(path)
        f = open(join(path, "image.txt"), 'w')
        [f.write("%s\n" % x) for x in images]
        f.close()


def convert_xml_to_json(path: str):
    images, bndbox, size, polygon, all_json = {}, {}, {}, {}, {}
    imgs_list = open(path + '/image.txt', 'r').read().splitlines()

    for img in imgs_list:
        name_xml = img.split('.jpg')[0] + '.xml'
        images.update({"filename": img})
        root = ET.ElementTree(file=path + '/' + name_xml).getroot()
        counterObject, xmin, xmax, ymin, ymax, regionsTemp, regi = {}, {}, {}, {}, {}, {}, {}
        number = 0
        for child_of_root in root:
            if child_of_root.tag == 'filename':
                image_id = (child_of_root.text)
                sizetmp = os.path.getsize(path + '/' + image_id)
            if child_of_root.tag == 'object':
                for child_of_object in child_of_root:
                    if child_of_object.tag == 'name':
                        category_id = child_of_object.text
                        counterObject[category_id] = number
                    if child_of_object.tag == 'bndbox':
                        for child_of_root in child_of_object:
                            if child_of_root.tag == 'xmin':
                                xmin[category_id] = int(child_of_root.text)
                            if child_of_root.tag == 'xmax':
                                xmax[category_id] = int(child_of_root.text)
                            if child_of_root.tag == 'ymin':
                                ymin[category_id] = int(child_of_root.text)
                            if child_of_root.tag == 'ymax':
                                ymax[category_id] = int(child_of_root.text)

                xmintmp = int(xmax[category_id] - xmin[category_id]) / 2
                xvalue = int(xmin[category_id] + xmintmp)
                ymintemp = int(ymax[category_id] - ymin[category_id]) / 2
                yvalue = int(ymin[category_id] + ymintemp)

                regions = {}
                regionsTemp = ({"all_points_x": (
                    xmin[category_id], xvalue, xmax[category_id], xmax[category_id], xmax[category_id], xvalue,
                    xmin[category_id], xmin[category_id], xmin[category_id]),
                    "all_points_y": (
                        ymin[category_id], ymin[category_id], ymin[category_id], yvalue,
                        ymax[category_id], ymax[category_id], ymax[category_id], yvalue,
                        ymin[category_id])})

                category_id_name = (
                    category_id.split(' ')[0])  # cause some <name>SD 1<name>, just use SD
                regions.update({"region_attributes": {"name": category_id_name}})
                shapes = {"shape_attributes": regionsTemp}
                regions.update(shapes)
                polygon.update({"name": "polygon"})
                regions.update(shapes)
                regions.update(polygon)
                regi[number] = regions.copy()
                regions = {"regions": regi}
                images.update(regions)
                images.update({"size": sizetmp})
                all_json[img] = images.copy()
                number += 1

    with open(path + '/' + "dataset.json", "a") as outfile:
        json.dump(all_json, outfile)
        print("File dataset.json was save in: ", path)


def read_json(dir_path: str, filename: str):
    with open(dir_path + '/' + filename) as json_file:
        data = json.load(json_file)
    return data


def remove_file(file_name: str):
    if os.path.isfile(file_name):
        os.remove(file_name)
        print("Deleting file %s" % file_name)
    else:
        print("It does not exist  %s" % file_name)


if __name__ == "__main__":

    # Json file for both train and val dir
    file_train = os.path.join(train_dir, "dataset.json")
    file_val = os.path.join(val_dir, "dataset.json")

    # Remove if exist dataset.json in both train and val
    remove_file(file_train)
    remove_file(file_val)

    # Save a log in both train and val
    save_images_log(train_dir)
    save_images_log(val_dir)

    # Convert from xml to json in both train and val
    convert_xml_to_json(train_dir)
    convert_xml_to_json(val_dir)

    # json1 = json.dumps(read_json(train_dir, "dataset.json"), sort_keys=True)
    # json2 = json.dumps(read_json(train_dir, "dataset_good.json"), sort_keys=True)
    # if json1 == json2:
    #     print("Equals!")
