# https://stackoverflow.com/questions/36323888/how-can-i-create-a-simple-system-wide-python-library/36332776
import os
import sys
import glob2
import zipfile
import json
import shutil
import re

from PIL import Image

# from objloader import Obj
from .custom_objloader import Obj
from .helpers import AuxFunctions
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class ShapeNetHandler(AuxFunctions):

    def __init__(self, shapenet_location, display_objects=False, shapenet_json_path="shapenet.json"):

        super(ShapeNetHandler, self).__init__()

        # Set path for location of shapenet json (created with this handler - NOT included with Shapenet original data)
        self.shapenet_json_path = shapenet_json_path

        self.SHAPENET_DIR = shapenet_location
        self.__init_archive()
        self.__load_taxonomy()
        self.__load_shapenet(display_objects)

    def __init_archive(self):
        print("Initializing Archive...")
        self.archive = zipfile.ZipFile(self.SHAPENET_DIR, "r")
        self.archive_contents = self.archive.namelist()

    def __load_taxonomy(self):
        self.taxonomy = json.load(self.archive.open([file_i for file_i in self.archive_contents if "taxonomy.json" in file_i][0]))

    def __load_shapenet(self, display_objects=3):

        # Check if shapenet files already created - if so, load it; else, generate it
        if os.path.isfile(self.shapenet_json_path):
            print("Loading Shapenet Hierarchy Structure...")
            with open(self.shapenet_json_path, "r") as infile:
                self.shapenet = json.load(infile)

        else:
            print("Generating Shapenet Hierarchy Structure...")
            self.shapenet = {}

            for taxonomy_i, taxonomy_i_data in enumerate(self.taxonomy, 1):
                # Update consle
                sys.stdout.write('\r Processing category {}/{}...'.format(taxonomy_i, len(self.taxonomy)))
                sys.stdout.flush()

                # Retrieve key attributes
                synset_ID = taxonomy_i_data["synsetId"]
                category_name = taxonomy_i_data["name"].split(",")[0] # only pick 1 name
                num_instances = taxonomy_i_data["numInstances"]

                # Lookup Unique Instance IDs
                instance_list_raw = [item_i.split("/")[2] for item_i in self.archive_contents if re.compile(synset_ID).search(item_i)]
                instance_list = list(set([item_i for item_i in instance_list_raw if item_i != '']))

                # Update shapenet
                self.shapenet[category_name] = {
                    "synset_ID" : synset_ID,
                    "num_instances" : num_instances,
                    "instances" : instance_list
                }

            # Write json
            with open(self.shapenet_json_path, "w") as outfile:
                json.dump(self.shapenet, outfile)

        # Set list of categories
        self.categories_list = list(self.shapenet.keys())

        # Synset Lookup
        self.synset_lookup = {val['synset_ID'] : key for key, val in self.shapenet.items()}

        # Display top display_objects if not None
        if display_objects:
            v_dot_count = 0
            for i, (key, val) in enumerate(shapenet.items()):
                if i < display_objects-1 or i == len(shapenet)-1:
                    print("{:4d}.{:4s} Object: {}".format(i+1, "", key))
                    print("{:12s}--> Synset ID: {}".format("", val["synset_ID"]))
                    print("{:12s}--> Num Instances: {}".format("", val["num_instances"]))
                else:
                    if v_dot_count < 3:
                        print("\t\t.")
                        v_dot_count += 1

        # Calculate dataset dist
        self.__calculate_shapenet_dataset_stats()

    def get_categories(self):
        return self.categories_list

    def get_instance_ids(self, category_name, limit=-1):
        try:
            instances = self.shapenet[category_name]["instances"]
        except:
            try:
                instances = self.shapenet[self.synset_lookup[category_name]]["instances"]
            except:
                print("Invalid Category Name!")

        return instances[:limit]

    def sample_instances(self, num_instances=1000, approach=2):

        if approach == 1:
            # Randomly sample categories list for num of instances
            sample_probabilities = [val["num_instances"] / float(self.stats["total_instances"]) for val in self.shapenet.values()]
            category_samples = np.random.choice(self.categories_list, size=num_instances, replace=True, p=sample_probabilities)

            samples = np.zeros(num_instances)
            for i, category_i in category_samples:
                print("category_i: {}".format(category_i))
                # Category Instances
                category_i_instances = self.shapenet[category_i]["instances"]

                if category_i_instances == None:
                    print("HERE")
                print("\n")

                samples[i] = np.random.choice(category_i_instances, size=1, replace=False)

        else:
            instance_list = [np.array(val_i["instances"]) for val_i in self.shapenet.values()]

            # Flatten list
            flatten = lambda l : np.array([item for sublist in l for item in sublist])
            instance_list = flatten(instance_list)

            samples = np.random.choice(instance_list, size=num_instances, replace=False)

        return samples

    def __calculate_shapenet_dataset_stats(self, show_plots=False):
        print("Generating Dataset Stats...")
        keys_df = pd.DataFrame(list(self.shapenet.keys()), columns=["objects"])
        counts_arr = [ele["num_instances"] for ele in self.shapenet.values()]
        counts_df = pd.DataFrame(counts_arr, columns=["counts"])
        self.shapenet_df = pd.concat([keys_df, counts_df], axis=1)

        # Set stats
        self.stats = {
            "num_categories" : len(self.shapenet.keys()),
            "min_instances" : np.min(counts_arr),
            "max_instances" : np.max(counts_arr),
            "mean_instances" : np.mean(counts_arr),
            "total_instances" : np.sum(counts_arr)
        }

        # Print stats
        for key, val in self.stats.items():
            print("{} : {}".format(key, val))

    def visualize(self, save_dir):

        # Sort dataframe by values
        sorted_shapenet_data = self.shapenet_df.sort_values(by=["counts"])

        # Plot counts vs. objects barplot
        fig1, ax1 = plt.subplots()

        # Figure 1
        # ---------------------------------------------------
        # the size of A4 paper
        fig1.set_size_inches(14.7, 8.27)

        g = sns.barplot(x="objects", y="counts", data=sorted_shapenet_data, ax=ax1)
        ax1.set_ylabel("Number of Instances per Object Class")
        spaced_labels = []
        for label_i, label in enumerate(ax1.get_xticklabels()):
            if label_i % 10 == 0:
                spaced_labels.append(label)
            else:
                spaced_labels.append("")

        ax1.set_xticklabels(spaced_labels, rotation=90)

        # Save figure 1
        fig_1_save_dir = os.path.join(save_dir, "fig1.png")
        fig1.savefig(fig_1_save_dir, bbox_inches='tight')
        # ---------------------------------------------------

        # Figure 2
        # ---------------------------------------------------
        fig2, ax2 = plt.subplots()
        shapenet_object_instances = [ele["num_instances"] for ele in self.shapenet.values()]
        sns.distplot(shapenet_object_instances, ax=ax2)
        ax2.set_xlabel("Object Instance Count")

        # Save figure 2
        fig_2_save_dir = os.path.join(save_dir, "fig2.png")
        fig2.savefig(fig_2_save_dir, bbox_inches='tight')
        # ---------------------------------------------------

    def list_objects(self, sort=True):

        # Print header
        # --------------------------------
        title = "Shapenet Object Classes"
        print("\n{}".format(title))
        print("{}".format("-"*len(title)))
        # --------------------------------

        if sort:
            # Sort dataframe by values
            sorted_shapenet_data = self.shapenet_df.sort_values(by=["counts"])

            for row_i, row_i_data in enumerate(sorted_shapenet_data.iterrows(), 1):
                object_i = row_i_data[1]["objects"]
                count_i = row_i_data[1]["counts"]

                print("{}. {} -- Instances: {}".format(row_i, object_i, count_i))
        else:
            # List items
            for obj_i, (obj_name, obj_vals) in enumerate(self.shapenet.items(), 1):
                print("{}. {} -- Instances: {}".format(obj_i, obj_name, obj_vals["num_instances"]))

    def load_instance(self, instance_id, base_dir='./', recalculate_vertex_normals=False, verbose=True):

        instance_path = [file_i for file_i in self.archive_contents if instance_id in file_i and '.obj' in file_i][0]

        self.load_errors = []

        with open("errors.txt", "w") as outfile:
            outfile.write("Errors\n")

        # Set destination path
        destination_path = "{}/temp/{}".format(base_dir, instance_id)

        # Extract model
        self.archive.extract(instance_path, destination_path)

        # Load model
        full_zip_path = os.path.join(destination_path, instance_path)

        # Load Textures
        texture_paths = [file_i for file_i in self.archive_contents if instance_id in file_i and "texture" in file_i and ".jpg" in file_i]
        loaded_textures = []
        print("\n\n\n")
        print("HERE HERE HERE")
        self.UPDATED = True
        for zipped_texture_path in texture_paths:
            # Unzip texture
            self.archive.extract(zipped_texture_path, destination_path)

            # Set texture path
            texture_path = os.path.join(destination_path, zipped_texture_path)

            # Open the texture
            texture = Image.open(texture_path)
            loaded_textures.append(texture)

        try:
            model_object = Obj.open("{}".format(full_zip_path))

        except Exception as e:
            error = "Error loading model at path '{}'. Exception: {}".format(full_zip_path, e)
            self.load_errors.append(error)

            # Log Error
            with open("errors.txt", "a") as outfile:
                outfile.write("{}\n".format(error))


            model_object = Obj.open("{}".format(full_zip_path))

        # Remove temp directory
        try:
            shutil.rmtree("temp/")
        except Exception as e:
            print("Exception!")
            print("e: {}".format(e))

        return model_object, loaded_textures

    def load_objects(self, object_name, num_objects=None, base_dir='./', recalculate_vertex_normals=False, fix_model_load_error=False, verbose=True):

        # Retrieve synset ID from object name
        synset_ID = self.shapenet[object_name]["synset_ID"]

        subfolder_paths = [file_i for file_i in self.archive_contents if synset_ID in file_i and '.obj' in file_i]

        if num_objects == None:
            self.model_objects = np.zeros(len(subfolder_paths))
        else:
            self.model_objects = np.zeros(num_objects)

        self.load_errors = []

        with open("errors.txt", "w") as outfile:
            outfile.write("Errors\n")

        for path_i, obj_extract_path in enumerate(subfolder_paths, 1):

            # Update user to stats if verbose
            if verbose:
                sys.stdout.write("\rLoaded Object {}/{}...".format(path_i, num_objects if num_objects else len(subfolder_paths)))
                sys.stdout.flush()

            # Set destination path
            destination_path = "{}/temp/{}".format(base_dir, object_name)

            # Extract model
            self.archive.extract(obj_extract_path, destination_path)

            # Load model
            full_zip_path = os.path.join(destination_path, obj_extract_path)

            # Save model : TEMP
            # -----------------********************-------------------------
            # shutil.copy(full_zip_path, r'C:\Users\t-miiuzz\Desktop\HERE')
            # -----------------********************-------------------------

            try:
                model_object = Obj.open("{}".format(full_zip_path))

            except Exception as e:
                error = "Error loading model at path '{}'. Exception: {}".format(full_zip_path, e)
                self.load_errors.append(error)

                # Log Error
                with open("errors.txt", "a") as outfile:
                    outfile.write("{}\n".format(error))

                if fix_model_load_error:
                    if str(e) == "inconsinstent":
                        self.__fix_inconsistency(full_zip_path)

                    try:
                        model_object = Obj.open("{}".format(full_zip_path))
                    except:
                        print("ERROR! Cannot load model object. Failed inconsistency fix.")
                        continue
                else:
                    continue

            if recalculate_vertex_normals:
                self.__recalculate_vertex_normals(full_zip_path)
                model_object = Obj.open("{}".format(full_zip_path))

            # Save model object
            self.model_objects[path_i-1] = model_object

            # Destroy path
            shutil.rmtree(destination_path)

            # Check for num object limitation set by user
            if num_objects and (len(self.model_objects) == num_objects):
                break

        # Remove temp directory
        shutil.rmtree("temp/")

        return self.model_objects
