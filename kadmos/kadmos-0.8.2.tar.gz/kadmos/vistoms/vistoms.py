# Imports
import ast
import json
import logging
import os
import shutil
import sys
import tempfile
import webbrowser
import zipfile
from copy import deepcopy
from shutil import copyfile

from flask import Flask, render_template, request, jsonify
from kadmos.cmdows.cmdows import find_cmdows_file
from kadmos.graph import load, FundamentalProblemGraph

app = Flask(__name__)

# Folder and file settings
UPLOAD_FOLDER = ''
TEMP_FILE = 'tmp'

# General functions
########################################################################################################################
@app.route('/VISTOMS')
def VISTOMS():
    """
       Function opens VISTOMS when it is called from the browser
    """
    return render_template('VISTOMS.html', new=0)


@app.route('/kadmosUploadFile', methods=['GET', 'POST'])
def kadmosUploadFile():
    """
        Function uploads a file to the temp folder and returns the graph information to VISTOMS

        :return: VISTOMS json data with graph information
    """
    try:
        if request.method == 'POST':
            # get request form
            fileType = request.form['fileType']
            newGraphID = request.form['newGraphID']
            uploaded_files = request.files.getlist("file[]")

            number_of_files = len(uploaded_files)
            if number_of_files > 2:
                return("ERROR: Max. number of files that can be uploaded is 2!")

            mpgFile = []
            dgFile = []
            for file in uploaded_files:
                if "_mpg" in file.filename:
                    mpgFile = file
                else:
                    dgFile = file

            # check if the post request has the file part
            if 'file[]' not in request.files:
               return("ERROR: No file part!")

            # if user does not select file, browser also
            # submit a empty part without filename
            if dgFile.filename == '':
                return("ERROR: No file part!")
            if dgFile:
                # Check if the right filetypes were chosen
                if fileType == 'CMDOWS file' and dgFile.filename.rsplit('.', 1)[1].lower() != "xml":
                    return ("ERROR: Wrong file type! Please use a valid CMDOWS file")
                elif fileType == 'KDMS file(s)' and dgFile.filename.rsplit('.', 1)[1].lower() != "kdms":
                    return ("ERROR: Wrong file type! Please use a valid KDMS file")
                elif fileType == 'Database' and dgFile.filename.rsplit('.', 1)[1].lower() != "zip":
                    return ("ERROR: Wrong file type! Please use a valid zip file")

                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                database_dir = ""
                if fileType == 'Database':
                    database_dir = os.path.join(UPLOAD_FOLDER, 'database_tmp')
                    zip_ref = zipfile.ZipFile(file, 'r')
                    zip_ref.extractall(database_dir)
                    zip_ref.close()
                    file_list = []
                    for file in os.listdir(database_dir):
                        file_list.append(os.path.join(database_dir, file))
                    cmdows_file = find_cmdows_file(file_list)
                    graphFileName = cmdows_file
                else:
                    graphFileName = os.path.join(UPLOAD_FOLDER, dgFile.filename)
                    dgFile.save(os.path.join(UPLOAD_FOLDER, dgFile.filename))

                loaded_graph = load(graphFileName, file_check_critical=False)
                # Remove the uploaded file (and if existing, database directory) from the temp folder
                os.remove(graphFileName)
                if os.path.exists(database_dir):
                    shutil.rmtree(database_dir)

                if isinstance(loaded_graph, tuple):
                    graph = loaded_graph[0]
                    mpg = loaded_graph[1]
                elif mpgFile:
                    # Check if the right filetype was chosen
                    if mpgFile.filename.rsplit('.', 1)[1].lower() != "kdms":
                        return ("ERROR: Wrong file type! Please use a valid KDMS file")
                    graph = loaded_graph
                    mpgFileName = mpgFile.filename
                    mpgFile.save(os.path.join(UPLOAD_FOLDER, mpgFileName))
                    mpg = load(os.path.join(UPLOAD_FOLDER, mpgFileName), file_check_critical=True)
                    # Remove the uploaded file from the temp folder
                    os.remove(os.path.join(UPLOAD_FOLDER, mpgFileName))
                else:
                    graph = loaded_graph
                    mpg = None

                #save the graph as kdms file in temp folder
                graph.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+newGraphID+'.kdms'),file_type='kdms',
                           graph_check_critical=False, mpg=mpg)

                # Use function order for VISTOMS if it is available in the graph information
                function_order = None
                if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg==None:
                    function_order = graph.graph['problem_formulation']['function_order']

                # Add the graph with the updated function order to VISTOMS
                newVistomsData = graph.vistoms_add_json(graph_id=newGraphID, function_order=function_order, mpg=mpg)

                return newVistomsData

        return("ERROR: File type " + dgFile.filename.rsplit('.', 1)[1].lower() + " not allowed!")

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosExportAllGraphs', methods=['POST'])
def kadmosExportAllGraphs():
    """
       Function exports all graphs to a folder as CMDOWS or KDMS files

       :param path: the path of the folder, the files are exported to
       :return: path
    """
    try:
        # Get request form
        path = os.path.join(request.form['path'],'')
        fileType = request.form['fileType']

        if not os.path.isdir(path):
            os.makedirs(os.path.dirname(path))

        for aFile in os.listdir(UPLOAD_FOLDER):
            if aFile.endswith(".kdms"):
                fileName = aFile.split('.')[0]
                fileName_split = fileName.split('_')
                if "mpg" not in fileName_split and "backup" not in fileName_split: # Do not loop through mpg files
                    graphFileName = fileName + ".kdms"
                    mpgFileName = fileName + "_mpg.kdms"
                    if os.path.exists(os.path.join(UPLOAD_FOLDER, mpgFileName)):
                        graph = load(os.path.join(UPLOAD_FOLDER, graphFileName), file_check_critical=False)
                        mpg = load(os.path.join(UPLOAD_FOLDER, mpgFileName), file_check_critical=False)
                    else:
                        graph = load(os.path.join(UPLOAD_FOLDER, graphFileName), file_check_critical=False)
                        mpg = None

                    # Add problem function roles if they are not already existing
                    if not hasattr(graph, 'name'):
                        graph_name = fileName
                    else:
                        graph_name = graph.name
                    # Add problem function roles if they are not already existing
                    if isinstance(graph, FundamentalProblemGraph):
                        if 'function_order' not in graph.graph['problem_formulation']:
                            graph.assert_or_add_nested_attribute(['problem_formulation', 'function_order'],
                                                             None)
                        if 'mdao_architecture' not in graph.graph['problem_formulation']:
                            graph.assert_or_add_nested_attribute(['problem_formulation', 'mdao_architecture'],
                                                             'undefined')
                        if 'allow_unconverged_couplings' not in graph.graph['problem_formulation']:
                            graph.assert_or_add_nested_attribute(['problem_formulation', 'allow_unconverged_couplings'],
                                                             False)
                        graph.add_function_problem_roles()

                    if fileType == "CMDOWS files":
                        file_type = "cmdows"
                        file = graph_name + ".xml"
                        # Save as CMDOWS file
                        graph.save(os.path.join(UPLOAD_FOLDER, graph_name), file_type=file_type, graph_check_critical=False, mpg=mpg)
                        # Copy CMDOWS file from temporary folder to user's download folder
                        copyfile(os.path.join(UPLOAD_FOLDER, file), os.path.join(path, file))
                        # remove temporary CMDOWS file
                        os.remove(os.path.join(UPLOAD_FOLDER, file))
                    elif fileType == "KDMS files":
                        file_type = "kdms"
                        # Save as kdms file
                        graph.save(os.path.join(UPLOAD_FOLDER, graph_name), file_type=file_type, graph_check_critical=False, mpg=mpg)
                        file = graph_name + ".kdms"
                        mpgfile = graph_name + "_mpg.kdms"
                        # Copy kdms file from temporary folder to user's download folder
                        copyfile(os.path.join(UPLOAD_FOLDER, file), os.path.join(path, file))
                        # remove temporary kdms file
                        os.remove(os.path.join(UPLOAD_FOLDER, file))
                        if os.path.exists(os.path.join(UPLOAD_FOLDER, mpgfile)):
                            copyfile(os.path.join(UPLOAD_FOLDER, mpgfile), os.path.join(path, mpgfile))
                            os.remove(os.path.join(UPLOAD_FOLDER, mpgfile))
        return path

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosExportGraph', methods=['POST'])
def kadmosExportGraph():
    """
       Function exports the current graph to a CMDOWS or kdms file

       :param file: a CMDOWS or kdms file that goes into the user's download folder
       :return: file
    """
    try:
        # Get request form
        path = os.path.join(request.form['path'], '')
        fileName = request.form['fileName']
        graphID = request.form['graphID']
        fileType = request.form['fileType']
        functionOrder = request.form['currentOrder'].split(',')

        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(UPLOAD_FOLDER, mpgFileName)):
            graph = load(os.path.join(UPLOAD_FOLDER, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(UPLOAD_FOLDER, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(UPLOAD_FOLDER, graphFileName), file_check_critical=False)
            mpg = None

        # Add problem function roles if they are not already existing
        if isinstance(graph, FundamentalProblemGraph):
            if 'function_order' not in graph.graph['problem_formulation']:
                graph.assert_or_add_nested_attribute(['problem_formulation', 'function_order'], None)
            if 'mdao_architecture' not in graph.graph['problem_formulation']:
                graph.assert_or_add_nested_attribute(['problem_formulation', 'mdao_architecture'], 'undefined')
            if 'allow_unconverged_couplings' not in graph.graph['problem_formulation']:
                graph.assert_or_add_nested_attribute(['problem_formulation', 'allow_unconverged_couplings'], False)
            graph.add_function_problem_roles()

        if not os.path.isdir(path):
            os.makedirs(os.path.dirname(path))

        if fileType == "kdms":
            copyfile(os.path.join(UPLOAD_FOLDER, graphFileName), os.path.join(path, fileName+".kdms"))
            if os.path.exists(os.path.join(UPLOAD_FOLDER, mpgFileName)):
                copyfile(os.path.join(UPLOAD_FOLDER, mpgFileName), os.path.join(path, fileName+'_mpg'+".kdms"))
        elif fileType == "cmdows":
            file = fileName + ".xml"
            # Save as CMDOWS file
            graph.save(os.path.join(UPLOAD_FOLDER, fileName), file_type=fileType, graph_check_critical=False, mpg=mpg)
            # Copy CMDOWS file from temporary folder to user's download folder
            copyfile(os.path.join(UPLOAD_FOLDER, file), os.path.join(path, file))
            # remove temporary CMDOWS file
            os.remove(os.path.join(UPLOAD_FOLDER, file))
        else:
            return ("ERROR: Wrong file type!!!")

        return (path)

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosSaveGraphTmp', methods=['POST'])
def kadmosSaveGraphTmp():
    """
       Function saves current graph as new VISTOMS graph and returns it to the VISTOMS package in the browser

       :return: the graph compressed as VISTOMS data
    """
    try:
        # get request form
        graphID = request.form['graphID']
        newGraphName = request.form['newGraphName']
        newGraphID = request.form['newGraphID']
        function_order = request.form['currentOrder'].split(',')

        tmpDir = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(tmpDir, mpgFileName)):
            graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
            mpg = None

        newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'
        graph.graph['name'] = newGraphName
        graph.save(os.path.join(UPLOAD_FOLDER, newFileName), file_type="kdms", graph_check_critical=False, mpg=mpg)

        newVistomsData = graph.vistoms_add_json(function_order=function_order,mpg=mpg, graph_id=newGraphID)

        return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosDeleteGraph', methods=['POST'])
def kadmosDeleteGraph():
    """
       Function finds all graphs that have been temporarily stored in the temp folder and returns them
       to the VISTOMS package in the browser. This function is always called when the browser is refreshed by the user.

       :return: the graphs compressed as VISTOMS data
    """
    try:
        # get request form
        graphID = request.form['graphID']

        tmpDir = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        backupGraphFileName = TEMP_FILE + '_' + graphID + '_backup.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        backupMpgFileName = TEMP_FILE + '_' + graphID + '_mpg_backup.kdms'
        if os.path.exists(os.path.join(tmpDir, graphFileName)):
            os.remove(os.path.join(tmpDir, graphFileName))
        if os.path.exists(os.path.join(tmpDir, backupGraphFileName)):
            os.remove(os.path.join(tmpDir, backupGraphFileName))
        if os.path.exists(os.path.join(tmpDir, mpgFileName)):
            os.remove(os.path.join(tmpDir, mpgFileName))
        if os.path.exists(os.path.join(tmpDir, backupMpgFileName)):
            os.remove(os.path.join(tmpDir, backupMpgFileName))

        return kadmosFindTempGraphs()

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosFindTempGraphs', methods=['POST'])
def kadmosFindTempGraphs():
    """
       Function finds all graphs that have been temporarily stored in the temp folder and returns them
       to the VISTOMS package in the browser. This function is always called when the browser is refreshed by the user.

       :return: the graphs compressed as VISTOMS data
    """
    try:
        # First of all, delete all graphs, that end with a _backup
        deleteBackupGraphs()

        tmpDir = UPLOAD_FOLDER
        newVIstomsDataArray = []
        file_list = os.listdir(tmpDir)
        if file_list:
            file_list.sort()
        for file in file_list:
            if file.endswith(".kdms"):
                fileName = file.split('.')[0].split('_')
                graphID = fileName[1]
                if "mpg" not in fileName: # Do not loop through mpg files
                    graphFileName = fileName[0] + "_" + graphID + ".kdms"
                    mpgFileName = fileName[0] + "_" + graphID + "_mpg.kdms"
                    if os.path.exists(os.path.join(tmpDir, mpgFileName)):
                        graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                        mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
                    else:
                        graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
                        mpg = None

                    # Use function order for VISTOMS if it is available in the graph information
                    function_order = None
                    if graph.graph_has_nested_attributes('problem_formulation', 'function_order') and mpg == None:
                        function_order = graph.graph['problem_formulation']['function_order']

                    graph.save(os.path.join(UPLOAD_FOLDER, graphFileName), file_type="kdms",
                               graph_check_critical=False, mpg=mpg)

                    newVIstomsDataArray.append(graph.vistoms_add_json(graph_id=graphID, function_order=function_order, mpg=mpg))

        return jsonify(newVIstomsDataArray)

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosRevertLastStep', methods=['POST'])
def kadmosRevertLastStep():
    """
       Function to revert the last graph manipulation step by returning the _backup file from the tepm folder
       :return: the graph compressed as VISTOMS data
    """
    try:
        # get request form
        graphID = request.form['graphID']

        tmpDir = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        backupGraphFileName = TEMP_FILE + '_' + graphID + '_backup.kdms'
        backupMpgFileName = TEMP_FILE + '_' + graphID + '_backup_mpg.kdms'

        graph = load(os.path.join(tmpDir, graphFileName), file_check_critical=False)
        backupGraph = load(os.path.join(tmpDir, backupGraphFileName), file_check_critical=False)
        if os.path.exists(os.path.join(tmpDir, mpgFileName)):
            mpg = load(os.path.join(tmpDir, mpgFileName), file_check_critical=False)
            backupMpg = load(os.path.join(tmpDir, backupMpgFileName), file_check_critical=False)
        else:
            mpg = None
            backupMpg = None

        # Switch graph and backup graph (What used to be the backup graph is now the new graph and vice versa)
        graph.save(os.path.join(UPLOAD_FOLDER, backupGraphFileName), file_type="kdms", graph_check_critical=False,
                   mpg=backupMpg)
        backupGraph.save(os.path.join(UPLOAD_FOLDER, graphFileName), file_type="kdms", graph_check_critical=False,
                         mpg=mpg)

        # Get function_oder of the backup graph
        function_order = None
        if backupGraph.graph_has_nested_attributes('problem_formulation', 'function_order'):
            function_order = backupGraph.graph['problem_formulation']['function_order']

        newVistomsData = backupGraph.vistoms_add_json(function_order=function_order,  mpg=mpg, graph_id=graphID)

        return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


def savePreviousGraph(graph_id):
    """
        Function saves the last graph, so you can revert a graph change within VISTOMS

        :param graph: Initial fundamental problem graph (FPG) to start working on the MDAO architecture definition
        :return: New VISTOMS json data with initial FPG
    """
    path = UPLOAD_FOLDER
    # current graph and mpg name
    graphFileName = TEMP_FILE + '_' + graph_id + '.kdms'
    mpgFileName = TEMP_FILE + '_' + graph_id + '_mpg.kdms'

    # Save graph as backup file
    backupGraphFileName = TEMP_FILE + '_' + graph_id + '_backup.kdms'
    copyfile(os.path.join(path, graphFileName), os.path.join(path, backupGraphFileName))
    if os.path.exists(os.path.join(path, mpgFileName)):
        # If mpg exists, save it as well
        backupMpgFileName = TEMP_FILE + '_' + graph_id + '_mpg_backup.kdms'
        copyfile(os.path.join(path, mpgFileName), os.path.join(path, backupMpgFileName))

def deleteBackupGraphs():
    """
        Function deletes all graphs that end with a _backup
    """
    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith("_backup.kdms"):
            os.remove(os.path.join(UPLOAD_FOLDER, file))
########################################################################################################################


# Graph inspection functions
########################################################################################################################
@app.route('/kadmosFindAllNodes', methods=['POST'])
def kadmosFindAllNodes():
    """
        Function to get all nodes from certain categories and return them

        :param method: The method for sorting the nodes. Specified by the user from VISTOMS
        :return: New VISTOMS json data with updated design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        category = str(request.form['category'])
        sub_category = str(request.form['sub_category'])
        attr_cond = ast.literal_eval(request.form['attr_cond'])
        attr_include = ast.literal_eval(request.form['attr_include'])
        attr_exclude = ast.literal_eval(request.form['attr_exclude'])
        xPath_include = str(request.form['xPath_include']).split(', ')
        xPath_exclude = str(request.form['xPath_exclude']).split(', ')

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        if attr_cond == []:
            attr_cond = None
        if attr_include == []:
            attr_include = None
        if attr_exclude == []:
            attr_exclude = None
        if xPath_include == [""]:
            xPath_include = None
        if xPath_exclude == [""]:
            xPath_exclude = None

        allNodes = graph.find_all_nodes(category=category,subcategory=sub_category,attr_cond=attr_cond,attr_include=attr_include,attr_exclude=attr_exclude,xpath_include=xPath_include,xpath_exclude=xPath_exclude)

        # allNodes_str = ', '.join(str(e) for e in allNodes)
        allNodes_str = json.dumps(allNodes)

        return allNodes_str

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosL1Check', methods=['POST'])
def kadmosL1Check():
    """
        Function to perform category a checks on the graph

        :return: Message, whether the check was successful or not
    """
    try:
        # Get request form
        graphID = request.form['graphID']

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        check_result = graph._check_category_a()

        if check_result[0] == True:
            return ("Check successful!")
        else:
            return "ERROR: Check was not successful. For further information, please consult the python log"

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosL2Check', methods=['POST'])
def kadmosL2Check():
    """
        Function to perform category b checks on the graph

        :return: Message, whether the check was successful or not
    """
    try:
        # Get request form
        graphID = request.form['graphID']

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        check_result = graph._check_category_b()

        if check_result[0] == True:
            return ("Check successful!")
        else:
            return "ERROR: Check was not successful. For further information, please consult the python log"

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.

@app.route('/kadmosL3Check', methods=['POST'])
def kadmosL3Check():
    """
        Function to perform category c checks on the graph

        :return: Message, whether the check was successful or not
    """
    try:
        # Get request form
        graphID = request.form['graphID']

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        check_result = graph._check_category_c()

        if check_result[0] == True:
            return ("Check successful!")
        else:
            return "ERROR: Check was not successful. For further information, please consult the python log"

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.
########################################################################################################################


# FPG manipulation functions
########################################################################################################################
@app.route('/kadmosStartDefiningMDOProblem', methods=['POST'])
def kadmosStartDefiningMDOProblem():
    """
        Function to start an MDO problem

        :param fpg_initial: Initial fundamental problem graph (FPG) to start working on the MDO problem definition
        :return: New VISTOMS json data with initial FPG
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        functionOrder = request.form['currentOrder'].split(',')
        newGraphID = request.form['newGraphID']
        newGraphName = request.form['newGraphName']

        newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: Graph is already an MDPG! FPG Cannot be initialized again!")
        else:
            mpg = None

            graph = load(os.path.join(path, graphFileName), file_check_critical=False)

            if isinstance(graph, FundamentalProblemGraph):
                return("ERROR: Graph is already an FPG and cannot be initialized again!")
            fpg_initial = graph.deepcopy_as(FundamentalProblemGraph)

            fpg_initial.graph['name'] = newGraphName
            fpg_initial.graph['description'] = 'Fundamental problem graph to solve the "' + graph.graph['name'] + '".'
            fpg_initial.graph['problem_formulation'] = dict()
            fpg_initial.graph['problem_formulation']['function_order'] = functionOrder
            fpg_initial.graph['problem_formulation']['mdao_architecture'] = "None"

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg_initial.vistoms_add_json(graph_id=newGraphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg_initial.save(os.path.join(UPLOAD_FOLDER, newFileName), file_type="kdms", graph_check_critical=False, mpg=mpg)

            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosChangeNodePos', methods=['POST'])
def kadmosChangeNodePos():
    """
        Function to change the position of a node (competence) within the graph

        :param newPos: Initial fundamental problem graph (FPG) to start working on the MDO problem definition
        :return: New VISTOMS json data with initial FPG
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        nodeName = str(request.form['nodeName'])
        function_order = request.form['currentOrder'].split(',')
        newPos = int(request.form['newPos'])

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot change a competence's position on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            # Change position of a node in th XDSM

            # Get tool list and put the coordinator in the top left corner
            function_order.remove(nodeName)
            function_order.insert(newPos, nodeName)
            if isinstance(graph, FundamentalProblemGraph):
                graph.graph['problem_formulation']['function_order'] = function_order
                if 'problem_role' in graph.nodes[function_order[0]]:
                    graph.add_function_problem_roles()

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'), file_type='kdms',
                       graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.

@app.route('/kadmosDeleteNode', methods=['POST'])
def kadmosDeleteNode():
    """
        Function deletes a node from the graph and returns the updated graph data to VISTOMS
        :param nodeName: name of the node to be deleted
        :return: VISTOMS json data with graph information
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        nodeName = str(request.form['nodeName'])
        function_order = request.form['currentOrder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot remove a competence from an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            # remove the node from the graph
            graph.remove_function_nodes(nodeName)
            # update function order
            function_order.remove(nodeName)


            # Add the graph with the updated function order to VISTOMS
            newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            graph.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'), file_type='kdms', graph_check_critical=False, mpg=mpg)

            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.

@app.route('/kadmosDeleteEdge', methods=['POST'])
def kadmosDeleteEdge():
    """
        Function deletes an edge from the graph and returns the updated graph data to VISTOMS
        :param nodeName: name of the node that is the input provider of the edge
        :param edgeName: name of the edge to be deleted
        :return: VISTOMS json data with graph information
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        nodeName = str(request.form['nodeName'])
        edgeName = str(request.form['edgeName'])
        function_order = request.form['currentOrder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = load(os.path.join(path, mpgFileName), file_check_critical=False)
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        # remove the edge
        graph.remove_edge(nodeName,edgeName)
        # Add the graph with the updated function order to VISTOMS
        newVistomsData = graph.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
        # Save the graph in temp/tmp.kdms
        graph.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'), file_type='kdms', graph_check_critical=False, mpg=mpg)

        return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosExcludeDesignCompetences', methods=['POST'])
def kadmosExcludeDesignCompetences():
    """
        Function to exclude design competences as requested by the user from VISTOMS

        :param nodeList: List of competences that shall be excluded
        :return: New VISTOMS json data with excluded design competences deleted
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        nodeList = request.form['nodeList'].split(',')
        function_order = request.form['currentOrder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot remove a competence from an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            fpg = FundamentalProblemGraph(graph)

            # Remove a node from the graph
            for nodeName in nodeList:
                fpg.remove_function_nodes(nodeName)
                function_order.remove(nodeName)
            # Assign new function order to problem formulation
            fpg.graph['problem_formulation']['function_order'] = function_order

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                       file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosMergeSeqDesignCompetences', methods=['POST'])
def kadmosMergeSeqDesignCompetences():
    """
        Function to merge design competences that run sequentially as requested by the user from VISTOMS

        :param nodeList: List of competences that shall be merged
        :return: New VISTOMS json data with merged design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        nodeList = request.form['nodeList'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None


            new_node = '-'.join(nodeList) + '--seq'

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg = fpg.merge_sequential_functions(nodeList, new_label=new_node)
            # adjust function order
            function_order = [new_node if func == nodeList[0] else func for func in function_order]
            for func in nodeList[1:]:
                function_order.remove(func)
            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                       file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosMergeParDesignCompetences', methods=['POST'])
def kadmosMergeParDesignCompetences():
    """
        Function to merge design competences that run in parallel as requested by the user from VISTOMS

        :param nodeList: List of competences that shall be merged
        :return: New VISTOMS json data with merged design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        nodeList = request.form['nodeList'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            new_node = '-'.join(nodeList) + '--par'

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg = fpg.merge_parallel_functions(nodeList, new_label=new_node)
            # adjust function order
            function_order = [new_node if func == nodeList[0] else func for func in function_order]
            for func in nodeList[1:]:
                function_order.remove(func)

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosMergeFuncModDesignCompetences', methods=['POST'])
def kadmosMergeFuncModDesignCompetences():
    """
        Function to merge design competences that run in different modes as requested by the user from VISTOMS

        :param nodeList: List of competences that shall be merged
        :return: New VISTOMS json data with merged design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        nodeList = request.form['nodeList'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            base_function = fpg.node[nodeList[0]]['name']
            modes = [str(string[string.find('[') + 1:string.find(']')]) for string in nodeList]
            suffices = [str(string[string.find('_'):string.find('[')]) for string in nodeList]
            new_node = base_function + '-merged[' + str(len(nodeList)) + 'modes]'

            fpg = fpg.merge_function_modes(base_function, modes, new_label=new_node, version='1.0', instance=1,
                                           suffices=suffices)
            # adjust function order
            function_order = [new_node if func == nodeList[0] else func for func in function_order]
            for func in nodeList[1:]:
                function_order.remove(func)

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosRemoveCollision', methods=['POST'])
def kadmosRemoveCollision():
    """
        Function to remove collisions coming from specific design competences as requested by the user from VISTOMS

        :param nodeList: List of competences for which collisions should be removed
        :return: New VISTOMS json data with updated design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        nodeList = request.form['nodeList'].split(',')
        function_order = request.form['currentorder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None


            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            for collision_source in nodeList:
                fpg.disconnect_problematic_variables_from(collision_source)

                fpg.graph['problem_formulation']['function_order'] = function_order

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosGetPossibleFunctionOrder', methods=['POST'])
def kadmosGetPossibleFunctionOrder():
    """
        Function to get a possible function order

        :param method: The method for sorting the nodes. Specified by the user from VISTOMS
        :return: New VISTOMS json data with updated design competences
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        method = request.form['sortingMethod']

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot merge comeptences on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            # Getting the possible function order with the method specified by the user
            function_order = fpg.get_possible_function_order(method)
            fpg.assert_or_add_nested_attribute(['problem_formulation', 'mdao_architecture'], 'undefined')
            fpg.graph['problem_formulation']['function_order'] = function_order
            if 'problem_role' in fpg.nodes[function_order[0]]:
                fpg.add_function_problem_roles()

            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE + '_' + graphID + '.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)

            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosMakeAllVariablesValid', methods=['POST'])
def kadmosMakeAllVariablesValid():
    """
        Function to make all variables from the graph valid --> Eliminates colissions

        :return: New VISTOMS json data with updated design competences
    """
    try:
        # get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg.graph['problem_formulation']['function_order'] = function_order

            # Function to check the graph for collisions and holes. Collisions are solved based on the function order and holes
            # will simply be removed.
            fpg.make_all_variables_valid()


            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosAddProblemFunctionRoles', methods=['POST'])
def kadmosAddProblemFunctionRoles():
    """
        Function to Add the problem function roles to the graph

        :return: New VISTOMS json data with updated design competences
    """
    try:
        # get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg.graph['problem_formulation']['function_order'] = function_order

            # Add the function problem roles (pre-coupling, coupled, post-coupling)
            fpg.add_function_problem_roles()

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.

@app.route('/kadmosMarkVariable', methods=['POST'])
def kadmosMarkVariable():
    """
        Function to mark a variable as "special variable" (constraint, objective, design variable, quantity of interest)
        :param xPath: xPath of the variable in the XML schema
        :param variableType: type of the variable it shall be marked as (constraint, objective, design variable, quantity of interest)
        :return: VISTOMS json data with graph information
    """
    try:
        # get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        variableType = request.form['variableType']
        xPath = request.form['xPath']
        operator = request.form['operator']
        upperBound = float(request.form['upperBound'])
        lowerBound = float(request.form['lowerBound'])
        nominalValue = float(request.form['nominalValue'])

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName =  TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName =  TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ('ERROR: This function can only be performed on an FPG!')
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        if isinstance(graph, FundamentalProblemGraph):
            fpg = graph
        else:
            fpg = FundamentalProblemGraph(graph)



        if (variableType=='designVariable'):
            fpg.mark_as_design_variable(xPath, nominal_value=nominalValue, upper_bound=upperBound, lower_bound=lowerBound)
        elif (variableType=='objective'):
            fpg.mark_as_objective(xPath)
        elif (variableType=='constraint'):
            fpg.mark_as_constraint(xPath,reference_value=nominalValue,operator=operator)
        elif (variableType=='quantityOfInterest'):
            fpg.mark_as_qois([xPath])
        else:
            return ("ERROR: Something went wrong in KADMOS!")

        # Add the graph with the updated function order to VISTOMS
        newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
        # Save the graph in temp/tmp.kdms
        fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'), file_type='kdms', graph_check_critical=False,mpg=mpg)

        return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosUnmarkVariable', methods=['POST'])
def kadmosUnmarkVariable():
    """
        Function to unmark a previously marked variable
        :param xPath: xPath of the variable in the XML schema
        :return: VISTOMS json data with graph information
    """
    try:
        # get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        xPath = request.form['xPath']

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName =  TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName =  TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ('ERROR: This function can only be performed on an FPG!')
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

        if isinstance(graph, FundamentalProblemGraph):
            fpg = graph
        else:
            fpg = FundamentalProblemGraph(graph)

        fpg.unmark_variable(xPath)

        # Add the graph with the updated function order to VISTOMS
        newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
        # Save the graph in temp/tmp.kdms
        fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'), file_type='kdms', graph_check_critical=False,mpg=mpg)

        return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosRemoveUnusedOutputs', methods=['POST'])
def kadmosRemoveUnusedOutputs():
    """
        Function to remove all unused variables that are output to the coordinator

        :return: New VISTOMS json data with updated design competences
    """
    try:
        # get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        cleanUp_str = request.form['cleanUp']
        if cleanUp_str == 'True':
            cleanUp = True
        else:
            cleanUp = False

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot do that on an existing MPG! Please go back to the FPG or RCG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            if isinstance(graph, FundamentalProblemGraph):
                fpg = graph
            else:
                fpg = FundamentalProblemGraph(graph)

            fpg.graph['problem_formulation']['function_order'] = function_order

            # Cleaning of the graph needs to be done in a while loop, to entirely remove all unused elements
            another_run = True
            while another_run:
                another_run = False
                # Delete unused variables
                output_nodes = fpg.find_all_nodes(subcategory='all outputs')
                for output_node in output_nodes:
                    if 'problem_role' not in fpg.node[output_node]:
                        fpg.remove_node(output_node)
                        another_run = True
                # Delete unnecessary functions automatically if the user wants to
                if cleanUp:
                    function_nodes = fpg.find_all_nodes(category='function')
                    for function_node in function_nodes:
                        if not fpg.out_edges(function_node):
                            fpg.remove_function_nodes(function_node)
                            function_order.remove(function_node)
                            another_run = True

            # Add the function problem roles (pre-coupling, coupled, post-coupling)
            fpg.add_function_problem_roles()

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = fpg.vistoms_add_json(function_order=function_order, graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            fpg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.

########################################################################################################################


# MDPG manipulation functions
########################################################################################################################
@app.route('/kadmosStartDefiningMDAOArchitecture', methods=['POST'])
def kadmosStartDefiningMDAOArchitecture():
    """
        Function to start an MDO problem definition

        :param graph: Initial fundamental problem graph (FPG) to start working on the MDAO architecture definition
        :return: New VISTOMS json data with initial FPG
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        functionOrder = request.form['currentOrder'].split(',')
        newGraphID = request.form['newGraphID']
        newGraphName = request.form['newGraphName']

        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        newFileName = TEMP_FILE + '_' + newGraphID + '.kdms'

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE+'_'+graphID+'.kdms'
        mpgFileName = TEMP_FILE+'_'+graphID+'_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: Graph is already an MDPG! FPG Cannot be initialized again!")
        else:
            mpg = None

            graph = load(os.path.join(path, graphFileName), file_check_critical=False)

            if not isinstance(graph, FundamentalProblemGraph):
                return("ERROR: Graph is not an FPG yet. Please perform the FPG Manipulation steps first!")

            # check if fpg is well defined
            check_result = graph._check_category_a()
            if check_result[0] != True:
                return("ERROR: The FPG is not well defined yet. Please perform FPG manipulation steps first and check the graph again!")


            mdg = deepcopy(graph)
            mdg.graph['name'] = newGraphName
            mdg.graph['description'] = 'MDAO data and process graph to solve the "' + graph.graph['name'] + '".'
            mdg.graph['problem_formulation'] = dict()
            mdg.graph['problem_formulation']['function_order'] = functionOrder
            mdg.graph['problem_formulation']['mdao_architecture'] = "None"

            # Add the graph with the updated function order to VISTOMS
            newVistomsData = mdg.vistoms_add_json(function_order=functionOrder, graph_id=newGraphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            mdg.save(os.path.join(UPLOAD_FOLDER, newFileName), file_type="kdms", graph_check_critical=False, mpg=mpg)

            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.


@app.route('/kadmosImposeMDAOArchitecture', methods=['POST'])
def kadmosImposeMDAOArchitecture():
    """
        Function to wrap an MDAO architecture around the MDAO problem

        :param allowUnconvergedCouplings: Bool variable whether unconverged couplings are allowed or not
        :return: New VISTOMS json data with updated MDAO data and process graphs
    """
    try:
        # Get request form
        graphID = request.form['graphID']
        function_order = request.form['currentOrder'].split(',')
        mdao_architecture = request.form['mdao_architecture']
        doe_method = request.form['doe_method']
        coupling_decomposition = request.form['coupling_decomposition']
        allow_unconverged_couplings_str = request.form['allow_unconverged_couplings']
        if allow_unconverged_couplings_str == 'True':
            allow_unconverged_couplings = True
        else:
            allow_unconverged_couplings = False


        # Save previous graph as backup before making the changes
        savePreviousGraph(graphID)

        path = UPLOAD_FOLDER
        graphFileName = TEMP_FILE + '_' + graphID + '.kdms'
        mpgFileName = TEMP_FILE + '_' + graphID + '_mpg.kdms'
        if os.path.exists(os.path.join(path, mpgFileName)):
            return ("ERROR: You cannot perform this on an existing MPG! Please go back to the FPG to do so.")
        else:
            graph = load(os.path.join(path, graphFileName), file_check_critical=False)
            mpg = None

            mdao_definition = mdao_architecture
            if coupling_decomposition == 'Gauss-Seidel':
                mdao_definition += '-GS'
            elif coupling_decomposition == 'Jacobi':
                mdao_definition += '-J'
            elif coupling_decomposition == '-':
                coupling_decomposition = None

            if not isinstance(graph, FundamentalProblemGraph):
                return "ERROR: Your graph is not an FPG yet. Please perform FPG manipulation steps before imposing an MDAO architecture!"

            fpg = graph

            mdao_definition = mdao_architecture
            if coupling_decomposition == 'Gauss-Seidel':
                mdao_definition += '-GS'
            elif coupling_decomposition == 'Jacobi':
                mdao_definition += '-J'
            elif coupling_decomposition == '-':
                coupling_decomposition = None

            # Define settings of the problem formulation
            fpg.graph['problem_formulation'] = dict()
            fpg.graph['problem_formulation']['function_order'] = function_order
            fpg.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
            fpg.graph['problem_formulation']['convergence_type'] = coupling_decomposition
            fpg.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

            if mdao_architecture in ['converged-DOE', 'unconverged-DOE']:
                if doe_method not in fpg.OPTIONS_DOE_METHODS:
                    return "ERROR: Invalid DOE method selected, please select a DOE method from the dropdown list"

                fpg.graph['problem_formulation']['doe_settings'] = {'doe_method': doe_method}
                if fpg.graph['problem_formulation']['doe_settings']['doe_method'] in ['Latin hypercube design',
                                                                                      'Monte Carlo design']:
                    fpg.graph['problem_formulation']['doe_settings']['doe_seed'] = 6
                    fpg.graph['problem_formulation']['doe_settings']['doe_runs'] = 5
                elif fpg.graph['problem_formulation']['doe_settings']['doe_method'] in ['Full factorial design']:
                    fpg.graph['problem_formulation']['doe_settings']['doe_runs'] = 5

            fpg.add_function_problem_roles()

            mdg, mpg = fpg.impose_mdao_architecture()

            mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
            mpg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                                       'problem using the strategy: {}.'.format(mdao_definition)
            # Add the graph with the updated function order to VISTOMS
            newVistomsData = mdg.vistoms_add_json(graph_id=graphID, mpg=mpg)
            # Save the graph in temp/tmp.kdms
            mdg.save(os.path.join(UPLOAD_FOLDER, TEMP_FILE+'_'+graphID+'.kdms'),
                     file_type='kdms', graph_check_critical=False, mpg=mpg)
            return newVistomsData

    except Exception as e:
        return "ERROR: " + e.message
        # Logs the error appropriately.
########################################################################################################################


# Then in the run_vistoms handle the folder and open_vistoms
# arguments as follows:
def run_vistoms(folder=None, write_log=True, open_vistoms=True):
    global UPLOAD_FOLDER
    if open_vistoms:
        # Open VISTOMS when running the app.py in the beginning
        webbrowser.open_new('http://127.0.0.1:5000/VISTOMS')

    if write_log:
        # Settings for logging
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    if folder is None:
        # Create temporary directory
        UPLOAD_FOLDER = tempfile.mkdtemp()
    else:
        # Assert given folder
        assert isinstance(folder, basestring), 'Folder should be a string.'
        # If folder does not exist, then create it recursively
        UPLOAD_FOLDER = folder
        if not os.path.isdir(UPLOAD_FOLDER):
            os.makedirs(os.path.dirname(UPLOAD_FOLDER))
    # Run the app
    app.run()


# In the app.py (or vistoms.py) I would do it like this at
# the end of the file (so you can run it directly from the
# vistoms.py file.
#
# Examples for running vistoms.py are then:
# python vistoms.py
# python vistoms.py -folder C:/Users/aigner/Desktop/vistoms_tmp
# python vistoms.py -open y -folder C:/Users/aigner/Desktop/vistoms_tmp
# python vistoms.py -open y -folder C:/Users/aigner/Desktop/vistoms_tmp -write_log y
if __name__ == '__main__':
    # Get system arguments
    args = sys.argv
    # Check if folder is given in args
    if '-folder' in args:
        folder = os.path.join(args[args.index('-folder') + 1],'')
        assert isinstance(folder, basestring), 'Folder should be a string.'
    else:
        folder = None
    # Check if open_vistoms is given in args
    if '-open' in args:
        open_vistoms = args[args.index('-open') + 1]
        assert open_vistoms.lower() in ['y', 'yes', 'n', 'no']
        if open_vistoms.lower() in ['y', 'yes']:
            open_vistoms = True
        elif open_vistoms.lower() in ['n', 'no']:
            open_vistoms = False
        else:
            raise IOError('Please provide valid argument for -open, either y or n.')
    else:
        open_vistoms = True  # default is to open
    # Check if write_log is given in args
    if '-write_log' in args:
        write_log = args[args.index('-write_log') + 1]
        assert write_log.lower() in ['y', 'yes', 'n', 'no']
        if write_log.lower() in ['y', 'yes']:
            write_log = True
        elif write_log.lower() in ['n', 'no']:
            write_log = False
        else:
            raise IOError('Please provide valid argument for -open, either y or n.')
    else:
        write_log = True
    # Now run the Python VISTOMS method that you have in app.py
    run_vistoms(folder=folder, write_log=write_log, open_vistoms=open_vistoms)