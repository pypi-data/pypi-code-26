import os
import sys
import tarfile
import numpy as np
import json
import glob2
import cv2
import shutil
from PIL import Image
import PIL.ImageOps
from itertools import combinations

from ShapeNetHandler import ShapeNetHandler
from .Render import ModernGL_Wrapper
from .colors import *

class RenderHandler(object):
    def __init__(self, kwargs):

        # Set render params
        self.VIEWPORT_WIDTH = kwargs["VIEWPORT_WIDTH"]
        self.VIEWPORT_HEIGHT = kwargs["VIEWPORT_HEIGHT"]
        self.IMG_SCALE_FACTOR = kwargs["IMG_SCALE_FACTOR"]
        self._random_point_noise = kwargs["random_point_noise"]

        # Define colors
        self.__init_colors(kwargs)

        # Set directories
        self.SAVE_DIR = os.path.join(kwargs["save_dir"], "render_source")
        self.SHAPENET_DIR = kwargs["shapenet_dir"]
        self._geodesic_dir = kwargs["geodesic_dir"]
        self._background_textures_dir = kwargs["background_dir"]
        self._shaders_dir = kwargs["shaders_dir"]

        # Set training and test sizes
        self._training_size = kwargs["train_size"]
        self._test_size = kwargs["test_size"]

        # Initializers
        self.__init_save_dirs()
        self.__init_shapenet_handler()
        self.__sample_model_objs()
        self.__generate_thetas(kwargs["num_thetas"])
        self.__generate_camera_points()
        self.__generate_reference_render_points()
        self.__generate_class_ids()
        self.__generate_random_background_textures(kwargs["num_backgrounds"], kwargs["load_specific_MB"])
        self.__preload_model_objs()
        self.__init_moderngl_wrapper()

    def __init_colors(self, kwargs):
        try:
            self._background_color = BACKGROUND_COLORS[kwargs.get("background_color", "black")]
        except KeyError as e:
            print("Invalid color choice. Please choose from the following available colors:")
            for color_i, available_color in enumerate(BACKGROUND_COLORS.keys(), 1):
                print("{}. {}".format(color_i, available_color))
            raise e
        try:
            self._obj_color = OBJECT_COLORS[kwargs.get("obj_color", "white")]
        except KeyError as e:
            print("Invalid color choice. Please choose from the following available colors:")
            for color_i, available_color in enumerate(OBJECT_COLORS.keys(), 1):
                print("{}. {}".format(color_i, available_color))
            raise e

    def __init_moderngl_wrapper(self):
        # Setup wrapper params
        render_params = {
            "viewport_width"    : self.VIEWPORT_WIDTH,
            "viewport_height"   : self.VIEWPORT_HEIGHT,
            "shader_dir"        : self._shaders_dir,
            "background"        : {
                "background_obj_dir"    : self._background_textures_dir,
                "preloaded_textures"    : self._preloaded_backgrounds,
                "color"                 : self._background_color,
                "lighting"              : {
                    "ambient"               : {
                        "random"                : True,
                        "default"               : 0.7,
                        "min"                   : 0.4,
                        "max"                   : 0.7
                    }
                }
            },
            "object"            : {
                "color"                 : self._obj_color,
                "lighting"              : {
                    "ambient"               : {
                        "random"                : True,
                        "default"               : 0.7,
                        "min"                   : 0.4,
                        "max"                   : 0.7
                    }
                }
            }
        }

        # Create moderngl wrapper object
        self.moderngl_wrapper = ModernGL_Wrapper(params=render_params)

    def __init_save_dirs(self):
        """
            Initialize train / test save directories
        """
        self._training_dir = os.path.join(self.SAVE_DIR, "training")
        self._test_dir = os.path.join(self.SAVE_DIR, "test")

        self._load_saved = False
        if os.path.exists(self.SAVE_DIR):

            while True:
                user_input = input("Render source already exists. Overwrite (y/n)? ")

                if "y" in user_input.lower():
                    shutil.rmtree(self.SAVE_DIR)
                    self._load_saved = False
                    break
                elif "n" in user_input.lower():
                    print("Loading from saved render source...")
                    self._load_saved = True
                    break
                else:
                    print("Invalid entry. Try again with 'y' or 'n'")

        if not self._load_saved:
            print("Creating new render source...")
            # Make directories
            os.makedirs(self.SAVE_DIR)
            os.makedirs(self._training_dir)
            os.makedirs(self._test_dir)

            self._load_saved = False

    def __preload_model_objs(self):
        self._preloaded_model_objs = {"training" : {}, "test" : {}}
        memory_used = 0
        num_models_loaded = 0
        for train_or_test_set, dataset in self.sampled_shapenet_instance_ids.items():
            for instance_i, preload_instance_id in enumerate(dataset):

                model_obj = self.__load_model(self.SNhandler, preload_instance_id, train_or_test_set)

                memory_used += sys.getsizeof(model_obj[0])
                for texture_item in model_obj[1]:
                    memory_used += sys.getsizeof(texture_item)

                self._preloaded_model_objs[train_or_test_set][preload_instance_id] = model_obj

                num_models_loaded += 1

                sys.stdout.write("\rLoading and packing model obj {}/{} -- Memory: {:0.2f} MB".format(instance_i+1, len(dataset), memory_used/1e6))
                sys.stdout.flush()

        print("\n{} Preloaded Models consumed {:0.2f} MB memory".format(num_models_loaded, memory_used/1e6))

    def __generate_class_ids(self):
        self._total_num_renders = self._total_num_renders_per_instance * self._training_size
        self.class_ids = np.arange(self._total_num_renders)

    def __calculate_unit_vector(self, vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def __calculate_angle_between(self, v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2':: """
        v1_u = self.__calculate_unit_vector(v1)
        v2_u = self.__calculate_unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    def __calculate_spherical_points(self, cartesian_points):
        self.reference_spherical_points = np.zeros_like(cartesian_points)
        for point_i, (x, y, z) in enumerate(cartesian_points):
            r = np.sqrt(x**2 + y**2 + z**2)
            azimuth = np.arccos(z / float(r))
            elevation = np.arcsin(y / np.sqrt(x**2 + y**2))

            self.reference_spherical_points[point_i] = np.array([r, azimuth, elevation])

        # Calculate minimum angle separation
        vec_combs = combinations(cartesian_points, 2)

        angles = [self.__calculate_angle_between(*vec_comb) for vec_comb in vec_combs]
        self.GEODESIC_NEAREST_NEIGHBOR_ANGLE = np.min(angles)

    def __generate_reference_render_points(self):

        if self._load_saved:
            with open("{}/render_point_data.json".format(self.SAVE_DIR), "r") as infile:
                loaded_points = json.load(infile)

            for key, val in loaded_points.items():
                if isinstance(val, list):
                    val = np.array(val)

                self.__dict__[key] = val

        else:
            num_render_points_per_instance = self.reference_spherical_points.shape[0] * self.NUM_THETAS
            self.reference_render_points = np.zeros((num_render_points_per_instance, 3))

            render_i = 0
            for r, azimuth, elevation in self.reference_spherical_points:
                for theta in self.theta_range:
                    self.reference_render_points[render_i] = np.array([azimuth, elevation, theta])
                    render_i += 1

            # Save Parameters
            save_data = {
                "geodesic_obj_file"                 : self.geodesic_obj_file,
                "_num_geodesic_points"              : int(self._num_geodesic_points),
                "_total_num_renders_per_instance"   : int(self._total_num_renders_per_instance),
                "reference_spherical_points"        : [list([float(e) for e in ele]) for ele in self.reference_spherical_points],
                "reference_render_points"           : [list([float(e) for e in ele]) for ele in self.reference_render_points],
                "GEODESIC_NEAREST_NEIGHBOR_ANGLE"   : float(self.GEODESIC_NEAREST_NEIGHBOR_ANGLE)
            }

            # Save params
            with open("{}/render_point_data.json".format(self.SAVE_DIR), "w") as outfile:
                json.dump(save_data, outfile)


    def __get_angle_noise(self, aet, amplitude):
        return aet - amplitude * (0.5 - np.random.random(aet.shape))

    def __generate_random_render_point(self, reference_point):

        # calculate new azimuth, elevation, and thetas
        amp = self.GEODESIC_NEAREST_NEIGHBOR_ANGLE / 2 * self._random_point_noise # radians
        random_point = self.__get_angle_noise(reference_point, amplitude=amp)

        return random_point

    def __load_model(self, handler, instance_id, train_or_test_set):
        """
            Used in def render() for online mode
        """
        try:
            save_dir = self._training_dir if train_or_test_set == "training" else self._test_dir
            save_path = None if self._load_saved else save_dir # Do not resave model if already saved
            model, textures = handler.load_instance(instance_id, base_dir=r"C:", save_path=save_path)
            packed_model = model.pack('vx vy vz nx ny nz tx ty tz')
        except IndexError as e:
            print("\n** EXCEPTION: Model Load/Pack error.")
            print("Details: {}".format(e))
            print("\n")
            input("Failed. Press any key to exit")
            exit(1)

        return packed_model, textures

    def __sample_random_light_position(self, geodesic_points):
        random_i = np.random.choice([i for i, j in enumerate(geodesic_points)])
        return tuple(geodesic_points[random_i])

    def __init_shapenet_handler(self):
        # Load Shapenet
        self.SNhandler = ShapeNetHandler(shapenet_location=self.SHAPENET_DIR, display_objects=None)

    def __sample_model_objs(self):

        if self._load_saved:
            with open("{}/shapenet_model_instance_ids.json".format(self._training_dir), "r") as infile:
                training_shapenet_ids = np.array(json.load(infile))

            with open("{}/shapenet_model_instance_ids.json".format(self._test_dir), "r") as infile:
                test_shapenet_ids = np.array(json.load(infile))
        else:
            total_num_models_to_sample = self._training_size + self._test_size
            sampled_shapenet = self.SNhandler.sample_instances(total_num_models_to_sample)
            training_shapenet_ids = sampled_shapenet[:self._training_size]
            test_shapenet_ids = sampled_shapenet[self._training_size:]

            # Save to dirs
            with open("{}/shapenet_model_instance_ids.json".format(self._training_dir), "w") as outfile:
                json.dump(list(training_shapenet_ids), outfile)

            with open("{}/shapenet_model_instance_ids.json".format(self._test_dir), "w") as outfile:
                json.dump(list(test_shapenet_ids), outfile)

        self.sampled_shapenet_instance_ids = {
            "training"  : training_shapenet_ids,
            "test"      : test_shapenet_ids
        }

    def __generate_thetas(self, num_desired_thetas=5, verbose=False):
        DEGREE_INCREMENTS = 360 // num_desired_thetas

        init_theta_range = np.arange(0, 360, DEGREE_INCREMENTS)

        self.theta_range = np.array(list(map(np.radians, init_theta_range)))
        self.NUM_THETAS = self.theta_range.shape[0]

        if verbose:
            print("Degree Increments with {} num points: {}".format(num_desired_thetas, DEGREE_INCREMENTS))
            print("theta_range: {}".format(self.theta_range))
            print("NUM_THETAS: {}".format(self.NUM_THETAS))

    def __generate_camera_points(self, verbose=False):
        # Generate Camera Points
        geodesic_options = [ele for ele in glob2.glob("{}/*.obj".format(self._geodesic_dir))]
        self.geodesic_obj_file = geodesic_options[3]

        # Open geodesic object
        with open(self.geodesic_obj_file, "r") as infile:
            geodesic_data = infile.readlines()

        # Parse out the vertex points in the obj file
        reference_cartesian_points = np.array([list(map(np.float32, d.strip().split()[1:])) for d in geodesic_data if "v " in d])

        # Calculate the spherical points from cartesian, and sep angle
        self.__calculate_spherical_points(reference_cartesian_points)

        self._num_geodesic_points = reference_cartesian_points.shape[0]
        self._total_num_renders_per_instance = self.reference_spherical_points.shape[0] * self.NUM_THETAS

        if verbose:
            print("Number of geodesic points in '{}': {}".format(geodesic_obj_file, self._num_geodesic_points))
            print("self.GEODESIC_NEAREST_NEIGHBOR_ANGLE: {:0.4f} rads / {:0.4f} degs".format(self.GEODESIC_NEAREST_NEIGHBOR_ANGLE, np.degrees(self.GEODESIC_NEAREST_NEIGHBOR_ANGLE)))
            print("Total render points per instance: {}".format(self._total_num_renders_per_instance))

    def __generate_random_background_textures(self, num_samples, load_specific_MB, target_dir="places"):
        """
            target_dir options:
            dtd
            Brodatz_colored
            Brodatz_multiband
            iccv09Data
            places
        """

        if self._load_saved:
            saved_background_textures = {
                "training"  : [ele for ele in glob2.glob("{}/val_large/*".format(os.path.join(self._training_dir, "backgrounds"))) if ".jpg" in ele],
                "test"      : [ele for ele in glob2.glob("{}/val_large/*".format(os.path.join(self._test_dir, "backgrounds")))  if ".jpg" in ele]
            }

            training_samples = len(saved_background_textures["training"])
            test_samples = len(saved_background_textures["test"])
            total_num_samples = training_samples + test_samples

            print("Preparing to load {} background textures ({} training -- {} test) into memory...".format(total_num_samples, training_samples, test_samples))

            background_textures_dict = {}

            for train_or_test_set, dataset_path in saved_background_textures.items():
                extract_dir = os.path.join(self.__dict__["_{}_dir".format(train_or_test_set)], "backgrounds")
                background_textures = []

                for img_path in dataset_path:
                    with Image.open(img_path) as im:
                        texture = im.transpose(Image.FLIP_TOP_BOTTOM)
                        texture = PIL.ImageOps.invert(texture)
                        texture_size = texture.size
                        texture_bytes = texture.tobytes()

                    preloaded_background_texture = (texture, texture_size, texture_bytes)
                    background_textures.append(preloaded_background_texture)

                background_textures_dict[train_or_test_set] = background_textures
        else:
            training_samples = num_samples["training"]
            test_samples = num_samples["test"]
            total_num_samples = training_samples + test_samples

            print("Preparing to load {} background textures into memory...".format(total_num_samples))

            with tarfile.open("{}/val_large.tar".format(self._background_textures_dir)) as infile:
                names = infile.getnames()
                names = [ele for ele in names if ".jpg" in ele]

                total_num_background_files_available = len(names)
                print("total_num_background_files_available: {}".format(total_num_background_files_available))

                random_names = np.random.choice(names, total_num_samples, replace=False)

                training_background_names = random_names[:training_samples]
                test_background_names = random_names[training_samples:]

                preloaded_background_textures = []

                background_textures_space_used = 0
                background_extract_dir = os.path.join(self._training_dir, "backgrounds")
                for img_i, random_name in enumerate(random_names):

                    if img_i >= training_samples:
                        background_extract_dir = os.path.join(self._test_dir, "backgrounds")

                    # Update console
                    sys.stdout.write("\r\tPreloading background texture {:{length}d}/{:{length}d} -- Memory: {:0.4f} MB...".format(img_i+1, len(random_names), background_textures_space_used/1e6, length=len(str(len(random_names)))))
                    sys.stdout.flush()

                    # Extract the file
                    infile.extract(random_name, "{}/".format(background_extract_dir))

                    # Set the path to the extracted file
                    img_path = os.path.join("{}/".format(background_extract_dir), random_name)

                    # Open image and check if it is "bad"
                    # ***************************************
                    bad_image = True # Assume to be bad
                    while bad_image:
                        # Open image
                        with Image.open(img_path) as im:
                            im = im.transpose(Image.FLIP_TOP_BOTTOM)
                            im = PIL.ImageOps.invert(im)

                        # If dimensionality of image == 3 (i.e., color channel exists), then image is good.
                        if len(np.array(im).shape) == 3:
                            bad_image = False
                        # Else, image is bad, resample, extract new sample, and reset img path to open on next loop through while
                        else:
                            # Sample new potential background texture
                            new_sample = np.random.choice(names)

                            # Extract
                            infile.extract(new_sample, "{}/".format(background_extract_dir))

                            # Set path to extract
                            img_path = os.path.join("{}/".format(background_extract_dir), new_sample)
                    # ***************************************

                    # Resize to double resolution
                    resize_w = self.VIEWPORT_WIDTH*2
                    resize_h = self.VIEWPORT_HEIGHT*2
                    im = cv2.resize(np.array(im), (resize_w, resize_h))

                    # CROP the image randomly
                    # ------------------------------------------------------------------------
                    x_upper = np.random.randint(self.VIEWPORT_WIDTH, self.VIEWPORT_WIDTH*2)
                    x_lower = x_upper - self.VIEWPORT_WIDTH

                    y_upper = np.random.randint(self.VIEWPORT_HEIGHT, self.VIEWPORT_HEIGHT*2)
                    y_lower = y_upper - self.VIEWPORT_HEIGHT

                    im = im[y_lower:y_upper, x_lower:x_upper]
                    # ------------------------------------------------------------------------

                    # Set texture info
                    texture = Image.fromarray(im)
                    texture_size = texture.size
                    texture_bytes = texture.tobytes()

                    preloaded_background_texture = (texture, texture_size, texture_bytes)
                    background_textures_space_used += sys.getsizeof(np.array(list(map(np.array, preloaded_background_texture))))
                    preloaded_background_textures.append(preloaded_background_texture)

                    # If loading by specific amount of memory, check exceeding limit and break if true
                    if load_specific_MB != None and background_textures_space_used/1e6 > load_specific_MB:
                        break

            print("\n")
            print("Finished loading background textures.")
            print("{:0.2f} MB of memory consumed.".format(background_textures_space_used / 1e6))


            background_textures_dict = {
                "training"  : preloaded_background_textures[:training_samples],
                "test"      : preloaded_background_textures[training_samples:]
            }

        self._preloaded_backgrounds = background_textures_dict

    def get_batch(self, batch_size, train_or_test_set):
        """
            Input:
                batch_size  (int)
                train_or_test_set    (str)  ["test" or "training"]

            Output:
                Primary Returns
                ----------------
                sorted_reference_imgs, sorted_query_imgs, sorted_class_ids, target

                (0) sorted_reference_imgs   (int) dimensions: [VIEWPORT_WIDTH, VIEWPORT_HEIGHT, 3]
                (1) sorted_query_imgs       (int) dimensions: [VIEWPORT_WIDTH, VIEWPORT_HEIGHT, 3]
                (2) sorted_class_ids        ((int) list) dimensions: [batch_size]
                (3) instance_ids            ((int) list) dimensions: [batch_size]
                (4) target                  (int) dimensions: [1, batch_size, batch_size, 1]

                Secondary Returns available via self.secondary_returns
                --------------------
                (5) shapenet_ids            ((str) list) dimensions: [batch_size]
                (6) reference_AETs          ((int) list) dimensions: [batch_size, 3]
                (7) query_AETs              ((int) list) dimensions: [batch_size, 3]
        """

        # Initialize containers for render result
        class_ids = np.zeros(batch_size)
        batch_query_imgs = np.zeros((batch_size, self.VIEWPORT_WIDTH, self.VIEWPORT_HEIGHT, 3))
        batch_reference_imgs = np.zeros((batch_size, self.VIEWPORT_WIDTH, self.VIEWPORT_HEIGHT, 3))
        instance_ids = np.zeros(batch_size)
        shapenet_ids = np.zeros(batch_size, dtype='<U64')
        reference_AETs = np.zeros((batch_size, 3))
        query_AETs = np.zeros((batch_size, 3))

        # Iterate over each batch item and render
        for batch_i in range(batch_size):
            # Run the render
            # ****************************************
            batch_i_data = self.run(train_or_test_set)
            # ****************************************

            # Set primary returns
            batch_reference_imgs[batch_i] = batch_i_data["reference_img"]
            batch_query_imgs[batch_i] = batch_i_data["query_img"]
            class_ids[batch_i] = batch_i_data["class_id"]
            instance_ids[batch_i] = batch_i_data["instance_id"]

            # Set secondary returns
            shapenet_ids[batch_i] = batch_i_data["shapenet_id"]
            reference_AETs[batch_i] = batch_i_data["reference_AET"]
            query_AETs[batch_i] = batch_i_data["query_AET"]

        # Generate target
        sorted_class_id_indices = class_ids.argsort()

        # Sort items
        sorted_class_ids = class_ids[sorted_class_id_indices]
        sorted_query_imgs = batch_query_imgs[sorted_class_id_indices]
        sorted_reference_imgs = batch_reference_imgs[sorted_class_id_indices]
        sorted_instance_ids = instance_ids[sorted_class_id_indices]
        sorted_shapenet_ids = shapenet_ids[sorted_class_id_indices]
        sorted_reference_AETs = reference_AETs[sorted_class_id_indices]
        sorted_query_AETs = query_AETs[sorted_class_id_indices]

        # Create target
        ids_tiled_over_columns = np.tile(np.reshape(sorted_class_ids, [1, -1]), [batch_size, 1])
        ids_tiled_over_rows = np.tile(np.reshape(sorted_class_ids, [-1, 1]), [1, batch_size])
        target = (ids_tiled_over_columns == ids_tiled_over_rows).astype(np.float32)

        self.primary_returns = [sorted_reference_imgs, sorted_query_imgs, sorted_class_ids, sorted_instance_ids, target[np.newaxis, ..., np.newaxis]]
        self.secondary_returns = [sorted_shapenet_ids, sorted_reference_AETs, sorted_query_AETs]

        return self.primary_returns

    def run(self, train_or_test_set):

        # Randomly select a reference render point index
        reference_point_i = np.random.randint(self.reference_render_points.shape[0])

        # Get the reference point
        reference_render_point = self.reference_render_points[reference_point_i]

        # Randomly Select a shapenet instance id index
        shapenet_instance_i = np.random.randint(self.sampled_shapenet_instance_ids[train_or_test_set].shape[0])

        # Get the shapenet instance id
        shapenet_instance_id = self.sampled_shapenet_instance_ids[train_or_test_set][shapenet_instance_i]

        # Determine the class id:    class_id = instance_i * num_renders_per_instance + reference_point_i
        class_id = shapenet_instance_i * self._total_num_renders_per_instance + reference_point_i

        # Generate the query render point
        random_render_point = self.__generate_random_render_point(reference_render_point)

        # Generate source lighting
        source_light_position = self.__sample_random_light_position(self.reference_render_points)

        tuple_render_params = {
            "train_or_test_set"         : train_or_test_set,
            "render"                    : self.moderngl_wrapper,
            "handler"                   : self.SNhandler,
            "test_instance_id"          : shapenet_instance_id,
            "reference_render_point"    : reference_render_point,
            "random_render_point"       : random_render_point,
            "source_light_position"     : source_light_position,
            "scale_factor"              : self.IMG_SCALE_FACTOR,
            "background_dir"            : self._background_textures_dir,
            "online_mode"               : False
        }

        ref_img, rand_img = self.render_tuple(**tuple_render_params)

        return_data = {
            "reference_img"     : ref_img,
            "query_img"         : rand_img,
            "class_id"          : class_id,
            "instance_id"       : shapenet_instance_i,
            "shapenet_id"       : shapenet_instance_id,
            "reference_AET"     : reference_render_point,
            "query_AET"         : random_render_point
        }

        return return_data

    def render_tuple(self, train_or_test_set, render, handler, test_instance_id, reference_render_point, random_render_point, source_light_position, scale_factor, background_dir, online_mode):

        # Grab the model object
        model_object = self._preloaded_model_objs[train_or_test_set][test_instance_id]

        # Render Reference Point
        # ----------------------------------------------------------------------
        reference_render_params = {
            "model_object"              : model_object,
            "render_point"              : reference_render_point,
            "source_light_position"     : source_light_position,
            "scale_factor"              : scale_factor,
            "use_texture"               : False,
            "texture_background"        : False
        }

        render.render(**reference_render_params)
        reference_img = render.get_image()
        # ----------------------------------------------------------------------

        # Render Random Point
        # ----------------------------------------------------------------------
        query_render_params = {
            "model_object"              : model_object,
            "render_point"              : random_render_point,
            "source_light_position"     : source_light_position,
            "scale_factor"              : scale_factor,
            "train_or_test_set"         : train_or_test_set,
            "use_texture"               : True,
            "texture_background"        : True
        }

        render.render(**query_render_params)
        random_img = render.get_image()
        # ----------------------------------------------------------------------

        return (reference_img, random_img)
