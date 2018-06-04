import os
import re
import subprocess
import time

import numpy as np

class AuxFunctions(object):
    def __fix_inconsistency(self, inconsistent_obj_path):

        # Read file
        with open(inconsistent_obj_path, "r") as infile:
            inconsistent_obj_lines = infile.readlines()

        # Revise the lines by replacing spaces with / for face lines
        revised_lines = [re.sub("f (\d+)\s+(\d+)\s+(\d+)", r"f \1/\2/\3", line) for line in inconsistent_obj_lines]

        # Write revised obj file to temp for obj loading
        with open(inconsistent_obj_path, "w") as outfile:
            outfile.writelines(revised_lines)

    def __run_meshlab_server(self, obj_path):
        prev_dir = os.getcwd()
        try:

            meshlab_server_dir = r"C:\Program Files\VCG\MeshLab"

            # Change directory to meshlab server directory
            os.chdir(meshlab_server_dir)

            # Set file locations
            input_file_path = obj_path
            output_file_path = obj_path
            script_file_path = r"C:\Users\t-miiuzz\Desktop\test\recalculate_normals.mlx"

            # Setup subprocess command to meshlab server
            command = ["meshlabserver.exe"]
            command += ['-i', input_file_path]
            command += ['-o', output_file_path]
            command += ['-m', 'vn'] # Flag to save vertex normals
            command += ['-s', script_file_path]

            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            p.wait()
        except:
            pass

        os.chdir(prev_dir)

    def __recalculate_vertex_normals(self, obj_path, meshlab=True):
        """
            Recalculate the vertex normals for inconsistent obj files
            Time it!
        """
        # Read file
        with open(obj_path, "r") as infile:
            obj_lines = infile.readlines()

        # Init time
        t0 = time.time()

        # Calculate normals
        # ------------------------------------------
        if meshlab:
            self.__run_meshlab_server(obj_path)
        else:
            # Get list of vertices
            vertices = [[float(ele_i) for ele_i in ele.split()[1:]] for ele in obj_lines if re.compile(r'v \d+').search(ele)]

            # Get list of faces
            faces = [ele.split()[1:] for ele in obj_lines if re.compile(r'f \d+').search(ele)]

            # Calculate face norms
            face_norms = []
            for face in faces:
                # Vertices
                # --------------------------------------------------------------------
                face_vertices_i = [int(ele.split("/")[0]) for ele in face]

                face_i_vertices = [np.array(vertices[vertex_i-1]) for vertex_i in face_vertices_i]
                # --------------------------------------------------------------------

                # Textures
                # --------------------------------------------------------------------
                try:
                    face_i_vertex_textures = [int(ele.split("/")[1]) for ele in face]
                except:
                    pass
                # --------------------------------------------------------------------

                # Vertex normals
                # --------------------------------------------------------------------
                try:
                    face_i_vertex_normals = [int(ele.split("/")[2]) for ele in face]
                except:
                    pass
                # --------------------------------------------------------------------

                v1 = face_i_vertices[0] - face_i_vertices[1]
                v2 = face_i_vertices[0] - face_i_vertices[2]
                face_norm_vec = np.cross(v1, v2)
                face_norm_magnitude = np.linalg.norm(face_norm_vec)
                normalized_face_norm = face_norm_vec / float(face_norm_magnitude + 1e-9)

                face_norms.append(normalized_face_norm)
            # ------------------------------------------

        # Total runtime
        t_total = time.time() - t0
