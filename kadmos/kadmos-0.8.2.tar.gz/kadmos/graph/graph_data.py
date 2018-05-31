# Imports
import itertools
import copy
import logging
import distutils.util
import numbers
import os
import re
import random

import operator as oper
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from types import NoneType

from lxml import etree

from kadmos.utilities.strings import get_correctly_extended_latex_label
from ..utilities import prompting
from ..utilities import printing
from ..utilities.general import make_camel_case, unmake_camel_case, make_plural, get_list_entries, translate_dict_keys,\
    get_mdao_setup, get_group_vars
from ..utilities.testing import check
from ..utilities.plotting import AnnoteFinder
from ..utilities.xmls import Element

from graph_kadmos import KadmosGraph, _parse_check

from mixin_mdao import MdaoMixin
from mixin_kechain import KeChainMixin


# Settings for the logger
logger = logging.getLogger(__name__)


class DataGraph(KadmosGraph):

    OPTIONS_FUNCTION_ORDER_METHOD = ['manual', 'minimum feedback']

    def __init__(self, *args, **kwargs):
        super(DataGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_definition.set('uID', str(graph_problem_formulation.get('mdao_architecture')) +
                                      str(graph_problem_formulation.get('convergence_type')))

        # Create problemDefinition/problemFormulation
        cmdows_problem_formulation = cmdows_problem_definition.add('problemFormulation')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_formulation.add('mdaoArchitecture', graph_problem_formulation.get('mdao_architecture'))
        cmdows_problem_formulation.add('convergerType', graph_problem_formulation.get('convergence_type'))
        cmdows_executable_blocks_order = cmdows_problem_formulation.add('executableBlocksOrder')
        for index, item in enumerate(graph_problem_formulation.get('function_order')):
            # Create problemDefinition/problemFormulation/executableBlocksOrder/executableBlock
            cmdows_executable_blocks_order.add('executableBlock', item, attrib={'position': str(index + 1)})
        cmdows_problem_formulation.add('allowUnconvergedCouplings',
                                       str(graph_problem_formulation.get('allow_unconverged_couplings')).lower())

        # Create problemDefinition/problemFormulation/doeSettings
        graph_settings = graph_problem_formulation.get('doe_settings')
        if graph_settings is not None:
            cmdows_settings = cmdows_problem_formulation.add('doeSettings')
            cmdows_settings.add('doeMethod', graph_settings.get('doe_method'))
            cmdows_settings.add('doeSeeds', graph_settings.get('doe_seeds'))
            cmdows_settings.add('doeRuns', graph_settings.get('doe_runs'))

        # Create problemDefinition/problemRoles
        cmdows_problem_roles = cmdows_problem_definition.add('problemRoles')
        # Create problemDefinition/problemRoles/parameters
        cmdows_parameters = cmdows_problem_roles.add('parameters')
        # Create problemDefinition/problemRoles/parameters/...
        for cmdows_parameterIndex, cmdows_parameterDef in enumerate(self.CMDOWS_ROLES_DEF):
            cmdows_parameter = cmdows_parameters.add(cmdows_parameterDef[0] + 's')
            graph_attr_cond = ['problem_role', '==', self.PROBLEM_ROLES_VARS[cmdows_parameterIndex]]
            graph_parameter = self.find_all_nodes(category='variable', attr_cond=graph_attr_cond)
            for graph_problem_role in graph_parameter:
                cmdows_problem_role = cmdows_parameter.add(cmdows_parameterDef[0])
                cmdows_problem_role.set('uID',
                                        self.PROBLEM_ROLES_VAR_SUFFIXES[cmdows_parameterIndex] +
                                        str(graph_problem_role))
                cmdows_problem_role.add('parameterUID', graph_problem_role)
                for cmdows_problem_role_attr in cmdows_parameterDef[1]:
                    if cmdows_problem_role_attr == 'samples':
                        # Create problemDefinition/problemRoles/parameters/designVariables/designVariable/samples
                        cmdows_samples = cmdows_problem_role.add('samples')
                        if self.nodes[graph_problem_role].get(cmdows_problem_role_attr) is not None:
                            for idx, itm in enumerate(self.nodes[graph_problem_role].get(cmdows_problem_role_attr)):
                                cmdows_samples.add('sample', format(itm, '.12f'), attrib={'position': str(idx + 1)})
                    else:
                        cmdows_problem_role.add(self.CMDOWS_ATTRIBUTE_DICT[cmdows_problem_role_attr],
                                                self.nodes[graph_problem_role].get(cmdows_problem_role_attr),
                                                camel_case_conversion=True)

        # Create problemDefinition/problemRoles/executableBlocks
        cmdows_executable_blocks = cmdows_problem_roles.add('executableBlocks')
        graph_executable_blocks = self.graph['problem_formulation']['function_ordering']
        # Create problemDefinition/problemRoles/executableBlocks/...
        for executable_block in self.FUNCTION_ROLES:
            if graph_executable_blocks.get(executable_block) is not None:
                if len(graph_executable_blocks.get(executable_block)) != 0:
                    cmdows_key = cmdows_executable_blocks.add(make_camel_case(executable_block) + 'Blocks')
                    for graph_block in graph_executable_blocks.get(executable_block):
                        cmdows_key.add(make_camel_case(executable_block) + 'Block', graph_block)

        return cmdows_problem_definition

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_problem_def(self, cmdows):

        graph_problem_form = {}

        cmdows_problem_formulation = cmdows.find('problemDefinition/problemFormulation')
        if cmdows_problem_formulation is not None:
            graph_problem_form['mdao_architecture'] = cmdows_problem_formulation.findtext('mdaoArchitecture')
            graph_problem_form['convergence_type'] = cmdows_problem_formulation.findtext('convergerType')
            cmdows_executable_blocks = \
                cmdows_problem_formulation.find('executableBlocksOrder').findall('executableBlock')
            cmdows_executable_blocks_order = [None] * len(list(cmdows_executable_blocks))
            for cmdows_executable_block in cmdows_executable_blocks:
                cmdows_executable_blocks_order[int(cmdows_executable_block.get('position')
                                                   ) - 1] = cmdows_executable_block.text
            graph_problem_form['function_order'] = cmdows_executable_blocks_order
            graph_problem_form['allow_unconverged_couplings'] = bool(distutils.util.strtobool(
                cmdows_problem_formulation.findtext('allowUnconvergedCouplings')))
            graph_problem_form['doe_settings'] = {}
            cmdows_doe_settings = cmdows_problem_formulation.find('doeSettings')
            if cmdows_doe_settings is not None:
                for cmdows_doe_setting in list(cmdows_doe_settings):
                    graph_problem_form['doe_settings'][unmake_camel_case(cmdows_doe_setting.tag
                                                                         )] = cmdows_doe_setting.text

        cmdows_problem_roles = cmdows.find('problemDefinition/problemRoles')
        if cmdows_problem_roles is not None:
            graph_problem_form['function_ordering'] = {}
            cmdows_executable_blocks = cmdows_problem_roles.find('executableBlocks')
            for role in self.FUNCTION_ROLES:
                cmdows_blocks = cmdows_executable_blocks.find(make_camel_case(role) + 'Blocks')
                if cmdows_blocks is None:
                    arr = list()
                else:
                    arr = list()
                    for cmdows_block in list(cmdows_blocks):
                        if self.nodes.get(cmdows_block.text) is None:
                            # Add node if it does not exist yet
                            self.add_node(cmdows_block.text, category='function')
                        self.nodes[cmdows_block.text]['problem_role'] = role
                        arr.append(cmdows_block.text)
                graph_problem_form['function_ordering'][role] = arr

            variable_types = [make_plural(role[0]) for role in self.CMDOWS_ROLES_DEF]
            for variable_type in variable_types:
                cmdows_variables = cmdows_problem_roles.find('parameters/' + variable_type)
                if cmdows_variables is not None:
                    for cmdows_variable in list(cmdows_variables):
                        cmdows_parameter_uid = cmdows_variable.findtext('parameterUID')
                        cmdows_suffix = '__' + re.findall(r'(?<=__).*?(?=__)', cmdows_variable.get('uID'))[0] + '__'
                        # Add problem role
                        try:
                            self.nodes[cmdows_parameter_uid]['problem_role'] = self.CMDOWS_ROLES_DICT_INV[cmdows_suffix]
                            # TODO: Find a more elegant way to handle samples and parameterUID
                            for attribute in cmdows_variable.getchildren():
                                if attribute.tag == 'samples':
                                    cmdows_samples = attribute.findall('sample')
                                    cmdows_sample_data = [None] * len(list(cmdows_samples))
                                    for cmdows_sample in cmdows_samples:
                                        cmdows_sample_data[int(cmdows_sample.get('position')) - 1] = \
                                            float(cmdows_sample.text)
                                    self.nodes[cmdows_parameter_uid]['samples'] = cmdows_sample_data
                                    cmdows_variable.remove(attribute)
                            self.nodes[cmdows_parameter_uid].update(cmdows.finddict(cmdows_variable,
                                                                                    camel_case_conversion=True))
                            del self.nodes[cmdows_parameter_uid]['parameter_u_i_d']
                        except KeyError:
                            logger.error('Could not find the node "{}" for some reason when loading the CMDOWS'
                                         .format(cmdows_parameter_uid))
                            pass

        self.graph['problem_formulation'] = graph_problem_form

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                         GRAPH-SPECIFIC METHODS                                                   #
    # ---------------------------------------------------------------------------------------------------------------- #
    def mark_as_design_variable(self, node, lower_bound=None, upper_bound=None, samples=None, nominal_value=0.0,
                                ignore_outdegree=False):
        """Method to mark a single node as a design variable and add the required metadata for its definition.

        :param node: node
        :type node: str
        :param lower_bound: lower bound of design variable
        :type lower_bound: float
        :param upper_bound: upper bound of design variable
        :type upper_bound: float
        :param samples: samples of design variable
        :type samples: list
        :param nominal_value: nominal value of design variable
        :type nominal_value: float
        :param ignore_outdegree: option to ignore the outdegree required
        :type ignore_outdegree: bool
        :returns: graph with enriched design variable node
        """
        # Input assertions
        assert self.has_node(node), 'Node {} is not present in the graph.'.format(node)
        assert self.in_degree(node) <= 1, \
            'Node {} has to have an indegree of zero or one to be allowed as design variable.'.format(node)
        assert self.out_degree(node) > 0 or ignore_outdegree, \
            'Node {} has to have an outdegree of at least one to be a design variable.'.format(node)
        assert isinstance(lower_bound, (numbers.Number, list, NoneType)), \
            'Lower bound should be a number or list of numbers.'
        assert isinstance(upper_bound, (numbers.Number, list, NoneType)), \
            'Upper bound should be a number or list of numbers.'
        assert isinstance(samples, (list, NoneType)), 'Samples should be a list.'

        # Mark nodes
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[0]
        if lower_bound is not None:
            self.nodes[node]['valid_ranges'] = {'limit_range': {'minimum': lower_bound}}
        if upper_bound is not None:
            if 'valid_ranges' in self.nodes[node]:
                if 'limit_range' in self.nodes[node]['valid_ranges']:
                    self.nodes[node]['valid_ranges']['limit_range']['maximum'] = upper_bound
                else:
                    self.nodes[node]['valid_ranges']['limit_range'] = {'maximum': upper_bound}
            else:
                self.nodes[node]['valid_ranges'] = {'limit_range': {'maximum': upper_bound}}
        if samples is not None:
            self.nodes[node]['samples'] = samples
        self.nodes[node]['nominal_value'] = nominal_value

        return

    def mark_as_design_variables(self, nodes, lower_bounds=None, upper_bounds=None, samples=None, nominal_values=None):
        """Method to mark a list of nodes as design variable and add metadata.

        :param nodes: list of nodes present in the graph
        :type nodes: list or str
        :param lower_bounds: list of lower bound values
        :type lower_bounds: list, numbers.Number
        :param upper_bounds: list of upper bounds
        :type upper_bounds: list, numbers.Number
        :param samples: nested list of kadmos values
        :type samples: list
        :param nominal_values: list of nominal values
        :type nominal_values: list, numbers.Number
        :return: graph with enriched design variable nodes
        """

        # Input assertions
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_design_variable for' \
                                        ' single node.'
        if isinstance(lower_bounds, numbers.Number) or lower_bounds is None:
            lower_bounds = [lower_bounds]*len(nodes)
        else:
            assert isinstance(lower_bounds, list), 'Lower bounds should be a list.'
            assert len(lower_bounds) == len(nodes), 'Number of lower bounds is not equal to the number of nodes.'
        if isinstance(upper_bounds, numbers.Number) or upper_bounds is None:
            upper_bounds = [upper_bounds]*len(nodes)
        else:
            assert isinstance(upper_bounds, list), 'Upper bounds should be a list.'
            assert len(upper_bounds) == len(nodes), 'Number of upper bounds is not equal to the number of nodes.'
        if isinstance(nominal_values, numbers.Number) or nominal_values is None:
            nominal_values = [nominal_values]*len(nodes)
        else:
            assert isinstance(nominal_values, list), 'Nominal values should be a list.'
            assert len(nominal_values) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'
        if isinstance(samples, numbers.Number) or samples is None:
            samples = [samples]*len(nodes)
        else:
            assert isinstance(samples, list), 'Nominal values should be a list.'
            assert len(samples) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'

        # Mark nodes
        for node, lb, ub, sm, nv in zip(nodes, lower_bounds, upper_bounds, samples, nominal_values):
            self.mark_as_design_variable(node, lower_bound=lb, upper_bound=ub, samples=sm, nominal_value=nv)

        return

    def mark_as_objective(self, node, remove_unused_outputs=False):
        """Method to mark a single node as objective.

        :param node: variable node
        :type node: basestring
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :return: graph enriched with objective node
        """

        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark node
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[1]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraint(self, node, operator, reference_value, remove_unused_outputs=False):
        """Method to mark a node as a constraint.

        :param node: node to be marked (on the left side of the operator
        :type node: str
        :param operator: constraint operator or list of constraint operators
        :type operator: str or string list
        :param reference_value: value on the right side of the operator or list of values corresponding to the list of
                                operators
        :type reference_value: numbers.Number or list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :returns: graph with enriched constraint node
        """

        # dict of inequality operators
        operators = {'>': oper.gt,
                     '>=': oper.ge,
                     '<': oper.lt,
                     '<=': oper.le,
                     '==': oper.eq}

        # Input assertions
        assert self.has_node(node), 'Node %s not present in the graph.' % node
        if isinstance(operator, basestring):
            assert operator in operators, 'Operator has to be one of the following: %s' % operators.keys()
        elif isinstance(operator, list):
            assert len(operator) == 1 or len(operator) == 2, 'Only one or two operators can be provided.'
            assert len(operator) == len(reference_value), '{} operators provided with {} reference values. Please ' \
                                                          'provide equal sized lists.'.format(len(operator),
                                                                                              len(reference_value))
            for op in operator:
                assert operators[op](1, 0) or operators[op](0, 1), 'Operator has to be one of the following: >, >=, <' \
                                                                   ' or <='
        else:
            raise AssertionError('operator input is of wrong type {}.'.format(type(operator)))
        assert isinstance(reference_value, (numbers.Number, list)), 'Reference value is not a number or list.'

        # check if multiple bounds are used correctly.
        if isinstance(operator, list):
            if (operators[operator[0]](0, 1) and operators[operator[1]](1, 0)) or ((operators[operator[0]](1, 0) and
                                                                                    operators[operator[1]](0, 1))):
                a = reference_value[0]
                b = reference_value[1]
                if operators[operator[1]](a, b) and operators[operator[0]](b, a):
                    pass
                else:
                    raise IOError("ERROR: x {} {} and x {} {} are not consistent as "
                                  "bounds".format(operator[0], reference_value[0], operator[1], reference_value[1]))
            else:
                raise IOError("ERROR: the combination of {} and {} as bounds is not logical. "
                              "Please correct the operators provided".format(operator[0], operator[1]))

        # Mark nodes
        self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[2]
        if isinstance(operator, basestring):
            self.nodes[node]['constraint_operator'] = operator
            self.nodes[node]['reference_value'] = reference_value
        else:
            self.nodes[node]['constraint_operator'] = ';'.join(operator)
            self.nodes[node]['reference_value'] = ';'.join([str(item) for item in reference_value])
        if operator == '==':
            self.nodes[node]['constraint_type'] = 'equality'
        else:
            self.nodes[node]['constraint_type'] = 'inequality'

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraints(self, nodes, operators, reference_values, remove_unused_outputs=False):
        """Method to mark multiple nodes as constraints.

        :param nodes: nodes to be marked.
        :type nodes: list
        :param operators: operators to be implemented (as list per node or as single operator for all)
        :type operators: str, list
        :param reference_values: reference values to be used (as list of values per node or as single value for all)
        :type reference_values: float, list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        :return: graph with enriched constraint nodes

        Operators: '==', '>', '<', '>=' and '<='
        """

        # Input assertions
        # poss_ops = ['==', '>', '<', '>=', '<=']
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_constraint for ' \
                                        'single node.'
        if isinstance(operators, str):
            operators = [operators]*len(nodes)
        else:
            assert isinstance(operators, list), 'Operators should be a list.'
            assert len(operators) == len(nodes), 'Number of operators is not equal to the number of nodes.'
        if isinstance(reference_values, numbers.Number):
            reference_values = [reference_values]*len(nodes)
        else:
            assert isinstance(reference_values, list), 'Reference values should be a list.'
            assert len(reference_values) == len(nodes), 'Number of reference values is not equal to the number of ' \
                                                        'nodes.'
        for node, op, ref in zip(nodes, operators, reference_values):
            self.mark_as_constraint(node, op, ref)

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_qois(self, nodes, remove_unused_outputs=False):
        """Function to mark a list of nodes as quantity of interest.

        :param nodes: list of nodes present in the graph
        :type nodes: list
        :param remove_unused_outputs: option to remove unused outputs
        :type remove_unused_outputs: bool
        """

        # Input assertions
        assert isinstance(nodes, list)
        for node in nodes:
            assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark nodes
        for node in nodes:
            self.nodes[node]['problem_role'] = self.PROBLEM_ROLES_VARS[3]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def unmark_variable(self, node):
        """Function to unmark any marked variable.

        :param node: variable node to be unmarked
        :type node: basestring
        :return: graph with unmarked node
        """

        # Input assertions
        assert isinstance(node, basestring)
        assert self.has_node(node), 'Node {} is not present in the graph.'.format(node)
        assert self.nodes[node]['category'] == 'variable', 'Node {} should be of category variable.'.format(node)

        # Unmark design variable
        if 'problem_role' in self.nodes[node]:
            pr = self.nodes[node]['problem_role']
            if pr == self.PROBLEM_ROLES_VARS[0]:  # design variable
                del self.nodes[node]['problem_role']
                if 'valid_ranges' in self.nodes[node]:
                    del self.nodes[node]['valid_ranges']
                if 'samples' in self.nodes[node]:
                    del self.nodes[node]['samples']
                if 'nominal_value' in self.nodes[node]:
                    del self.nodes[node]['nominal_value']
            elif pr == self.PROBLEM_ROLES_VARS[1]:  # objective
                del self.nodes[node]['problem_role']
            elif pr == self.PROBLEM_ROLES_VARS[2]:  # constraint
                del self.nodes[node]['problem_role']
                del self.nodes[node]['constraint_operator']
                del self.nodes[node]['reference_value']
            elif pr == self.PROBLEM_ROLES_VARS[3]:  # quantity of interest
                del self.nodes[node]['problem_role']
            else:
                raise AssertionError('Invalid problem role {} found on variable node {}'.format(pr, node))

    def remove_unused_outputs(self):
        """ Function to remove output nodes from an FPG which do not have a problem role.

        :return: the nodes that were removed
        :rtype: list
        """
        # TODO: Reposition this and other functions to the FPG class.
        output_nodes = self.find_all_nodes(subcategory='all outputs')
        removed_nodes = []
        for output_node in output_nodes:
            if 'problem_role' not in self.nodes[output_node]:
                self.remove_node(output_node)
                removed_nodes.append(output_node)
        return removed_nodes

    def get_schema_root_name(self, node=None):
        if node is None:
            random_var_node = self.find_all_nodes(category='variable')[0]
            return random_var_node.split('/')[1]
        else:
            return node.split('/')[1]

    def get_coupling_matrix(self, function_order_method='manual', node_selection=None):
        """Function to determine the role of the different functions in the FPG.

        :param function_order_method: algorithm to be used for the order in which the functions are executed.
        :type function_order_method: basestring
        :param node_selection: selection of nodes for which the coupling matrix will be calculated only
        :type node_selection: list
        :return: graph with enriched function node attributes and function problem role dictionary
        :rtype: FundamentalProblemGraph
        """

        # Make a copy of the graph, check it and remove all inputs and outputs
        if node_selection:
            graph = self.get_subgraph_by_function_nodes(node_selection)
        else:
            graph = self.deepcopy()
        nodes_to_remove = list()
        # TODO: Consider using the check function
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all inputs'))
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all outputs'))
        graph.remove_nodes_from(nodes_to_remove)

        # Determine and check function ordering method
        assert function_order_method in self.OPTIONS_FUNCTION_ORDER_METHOD
        if function_order_method == 'manual':
            if node_selection:
                function_order = node_selection
            else:
                assert 'function_order' in graph.graph['problem_formulation'], 'function_order must be given as ' \
                                                                               'attribute.'
                function_order = graph.graph['problem_formulation']['function_order']
        elif function_order_method == 'random':
            function_order = graph.find_all_nodes(category='function')

        # First store all the out- and in-edge variables per function
        function_var_data = dict()
        # noinspection PyUnboundLocalVariable
        for function in function_order:
            function_var_data[function] = dict(in_vars=set(), out_vars=set())
            function_var_data[function]['in_vars'] = [edge[0] for edge in graph.in_edges(function)]
            function_var_data[function]['out_vars'] = [edge[1] for edge in graph.out_edges(function)]
        # Create an empty matrix
        coupling_matrix = np.zeros((len(function_order), len(function_order)), dtype=np.int)
        # Create the coupling matrix (including circular dependencies)
        for idx1, function1 in enumerate(function_order):
            for idx2, function2 in enumerate(function_order):
                n_coupling_vars = len(set(function_var_data[function1]['out_vars']).
                                      intersection(set(function_var_data[function2]['in_vars'])))
                coupling_matrix[idx1, idx2] = n_coupling_vars

        return coupling_matrix

    def get_coupling_dictionary(self):
        """ Function to get a coupling dictionary.

        :return: coupling dictionary
        :rtype: dict

        For each function node, the dictionary indicates from which function
        nodes it gets its input and the number of variables it gets.

        * F2 ==> x1, x2 ==> F1
        * F3 ==> x3 ==> F1

        Will give: {F1: {F2: 2, F3: 1}}
        """

        coupling_dict = dict()

        # Get all function nodes and corresponding coupling matrix
        function_nodes = self.find_all_nodes(category='function')
        coupling_matrix = self.get_coupling_matrix(node_selection=function_nodes)

        # Fill in dictionary
        for idx1, function1 in enumerate(function_nodes):
            coupling_dict[function1] = dict()
            for idx2, function2 in enumerate(function_nodes):
                if coupling_matrix[idx2][idx1] != 0:
                    coupling_dict[function1][function2] = coupling_matrix[idx2][idx1]

        return coupling_dict

    def get_possible_function_order(self, method, multi_start=None, check_graph=False):
        """ Method to find a possible function order, in the order: pre-coupled, coupled, post-coupled functions

        :param method: algorithm which will be used to minimize the feedback loops
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :param check_graph: check whether graph has problematic variables
        :type check_graph: bool
        :return: Possible function order
        :rtype: list
        """

        # Input assertions
        if check_graph:
            assert not self.find_all_nodes(subcategory='all problematic variables'), \
                'Graph still has problematic variables.'

        # Check for partitions
        if 'problem_formulation' in self.graph and 'partitions' in self.graph['problem_formulation']:
            partitions = self.graph['problem_formulation']['partitions']
        else:
            partitions = None

        # Get function graph
        function_graph = self.get_function_graph()
        function_graph.remove_edges_from(function_graph.selfloop_edges())

        # Add a super node in which the coupled functions will be merged
        function_graph.add_node('super_node', category='function')
        coupled_functions = []

        # If partitions check if all coupled nodes are assigned to a partition
        if partitions:
            functions_in_partitions = []
            for partition in partitions:
                nodes = list(partitions[partition])
                functions_in_partitions.extend(nodes)
            for function_id in functions_in_partitions:
                function_graph = nx.contracted_nodes(function_graph, 'super_node', function_id)
            function_graph.remove_edges_from(function_graph.selfloop_edges())
            if not nx.is_directed_acyclic_graph(function_graph):
                cycle = nx.find_cycle(function_graph)
                functions_in_cycle = set()
                functions_in_cycle.update(function_id for edges in cycle for function_id in edges)
                functions_in_cycle.remove('super_node')
                assert nx.is_directed_acyclic_graph(function_graph), 'Coupled functions {} should be added to a ' \
                                                                     'partition'.format(list(functions_in_cycle))
        else:
            # As long as not all coupled functions are merged into the super node:
            while not nx.is_directed_acyclic_graph(function_graph):
                # Find a cycle
                cycle = nx.find_cycle(function_graph)

                # Find the functions in the cycle
                functions_in_cycle = set()
                functions_in_cycle.update(function_id for edges in cycle for function_id in edges)
                functions_in_cycle = list(functions_in_cycle)

                # Merge the coupled functions in the super node
                for function_id in functions_in_cycle:
                    if function_id != 'super_node':
                        coupled_functions.append(function_id)
                        function_graph = nx.contracted_nodes(function_graph, 'super_node', function_id)
                        function_graph.remove_edges_from(function_graph.selfloop_edges())

        # Find a topological function order
        function_order = list(nx.topological_sort(function_graph))

        # Get pre-coupling functions and sort
        pre_coupling_functions = function_order[:function_order.index('super_node')]
        pre_coupling_functions_order = self.sort_nodes_for_process(pre_coupling_functions)

        # Sort coupled functions to minimize feedback
        if partitions:
            coupled_functions_order = []
            for partition in partitions:
                nodes = self.minimize_feedback(list(partitions[partition]), method, multi_start=multi_start)
                nodes = self.sort_nodes_for_process(nodes)
                partitions[partition] = nodes
                coupled_functions_order.extend(nodes)
            self.graph['problem_formulation']['partitions'] = partitions
        else:
            coupled_functions_order = self.minimize_feedback(coupled_functions, method, multi_start=multi_start)
            coupled_functions_order = self.sort_nodes_for_process(coupled_functions_order)

        # Get post-coupling functions and sort
        post_coupling_functions = function_order[function_order.index('super_node') + 1:]
        post_coupling_functions_order = self.sort_nodes_for_process(post_coupling_functions)

        # Get function_order
        function_order = pre_coupling_functions_order + coupled_functions_order + post_coupling_functions_order

        return function_order

    def get_highest_instance(self, node):
        """
        Method to get the highest instance of a node.

        :param node: node
        :type node: str
        :return: highest instance of the node
        :rtype: int
        """
        assert 'instance' in self.nodes[node], 'node {} does not have the expected attribute "instance".'.format(node)
        highest_instance = int(self.nodes[node]['instance'])
        instance_exists = True
        while instance_exists:
            # Check for one higher instance
            check_node = node + '__i' + str(highest_instance + 1)
            if self.has_node(check_node):
                highest_instance += 1
                assert self.nodes[check_node]['instance'] == highest_instance, \
                    'instance attribute of node {} does not match node string.'.format(check_node)
            else:
                return highest_instance

    def sort_nodes_for_process(self, nodes):
        """ Method to sort function nodes such that the process order is optimized, while not increasing the number of
        feedback loops

        :param nodes: function nodes to sort
        :type nodes: list
        :return: nodes in sorted order
        :rtype: list
        """

        # Input assertions
        for func in nodes:
            assert func in self, "Function node {} must be present in graph.".format(func)
            assert self.nodes[func]['category'] == 'function', "Node {} is not a function node".format(func)

        # When nodes have no feedback, get topological order (e.g. when sorting pre or post coupled functions)
        subgraph = self.get_subgraph_by_function_nodes(nodes)
        subgraph = subgraph.get_function_graph()
        if nx.is_directed_acyclic_graph(subgraph):
            nodes = nx.topological_sort(subgraph)

        nodes_to_sort = list(nodes)
        function_order = []

        # Get couplings between nodes
        coupling_dict = self.get_coupling_dictionary()

        while nodes_to_sort:
            sorted_nodes = []
            # Check for each node whether it can be sorted
            for idx, node in enumerate(nodes_to_sort):
                # If the non-sorted nodes before the node don't give input to the node, the node can be sorted
                if not set(nodes_to_sort[:idx]).intersection(coupling_dict[node]):
                    sorted_nodes.append(node)
                    function_order.extend([node])
            # Delete the sorted nodes from the nodes_to_sort list
            for node in sorted_nodes:
                nodes_to_sort.pop(nodes_to_sort.index(node))

        return function_order

    def minimize_feedback(self, nodes, method, multi_start=None, get_evaluations=False):
        """Function to find the function order with minimum feedback

        :param nodes: nodes for which the feedback needs to be minimized
        :type nodes: list
        :param method: algorithm used to find optimal function order
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :param get_evaluations: option to give the number of evaluations as output
        :type get_evaluations: bool
        :return: function order
        :rtype: list
        :return: number of evaluations
        :rtype: list
        """

        # TODO: check if input nodes > 1

        # Get coupling dictionary
        coupling_dict = self.get_coupling_dictionary()

        # Get random starting points for a multi-start
        if isinstance(multi_start, (int, long)):
            start_points = [[] for _ in range(multi_start)]
            for i in range(multi_start):
                random.shuffle(nodes)
                start_points[i][:] = nodes
            multi_start = start_points

        if multi_start:
            best_order = list(nodes)
            min_feedback = float("inf")
            min_size = float("inf")

            # Start algorithm for each starting point
            n_eval = 0
            for start_point in range(len(multi_start)):
                if method == 'brute-force' or method == 'branch-and-bound':
                    raise IOError('No multi start possible for an exact algorithm')
                elif method == 'single-swap':
                    function_order, n_eval_iter = self._single_swap(multi_start[start_point], coupling_dict)
                elif method == 'two-swap':
                    function_order, n_eval_iter = self._two_swap(multi_start[start_point], coupling_dict)
                elif method == 'hybrid-swap':
                    function_order, n_eval_iter1 = self._two_swap(multi_start[start_point], coupling_dict)
                    function_order, n_eval_iter2 = self._single_swap(function_order, coupling_dict)
                    n_eval_iter = n_eval_iter1 + n_eval_iter2
                else:
                    raise IOError('Selected method (' + method + ') is not a valid method for sequencing, supported ' +
                                  'methods are: brute-force, single-swap, two-swap, hybrid-swap, branch-and-bound')

                n_eval += n_eval_iter

                # Get feedback info
                feedback, size = self.get_feedback_info(function_order, coupling_dict)

                # Remember best order found
                if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                    best_order = list(function_order)
                    min_feedback = feedback
                    min_size = size

            function_order = list(best_order)

        else:
            if method == 'brute-force':
                function_order, n_eval = self._brute_force(nodes, coupling_dict)
            elif method == 'branch-and-bound':
                function_order, n_eval = self._branch_and_bound(nodes, coupling_dict)
            elif method == 'single-swap':
                function_order, n_eval = self._single_swap(nodes, coupling_dict)
            elif method == 'two-swap':
                function_order, n_eval = self._two_swap(nodes, coupling_dict)
            elif method == 'hybrid-swap':
                function_order, n_eval1 = self._two_swap(nodes, coupling_dict)
                function_order, n_eval2 = self._single_swap(function_order, coupling_dict)
                n_eval = n_eval1 + n_eval2
            elif method == 'genetic-algorithm':
                function_order = self._genetic_algorithm(nodes, coupling_dict)  # TODO: add n_eval to genetic algorithm
                n_eval = 1
            else:
                raise IOError('Selected method (' + method + ') is not a valid method for sequencing, supported ' +
                              'methods are: brute-force, single-swap, two-swap, hybrid-swap, branch-and-bound')

        if get_evaluations:
            return function_order, n_eval
        else:
            return function_order

    def _brute_force(self, nodes, coupling_dict):
        """Function to find the minimum number of feedback loops using the brute-force method: try all possible
        combinations and select the best one

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return: function order
        :rtype: list
        """

        # Calculate the number of runs that are needed and give a warning when it exceeds a threshold
        n_runs = np.math.factorial(len(nodes))
        if n_runs > 3e5:
            logger.warning(str(n_runs) + ' tool combinations need to be evaluated for the brute-force method. Be ' +
                           'aware that this can take up a considerable amount of time and resources')

        function_order = list(nodes)
        min_feedback = float("inf")

        # Keep track of number of evaluated function orders
        n_eval = 0

        # Get all possible combinations
        for current_order in itertools.permutations(nodes):
            n_eval += 1
            feedback = self.get_feedback_info(current_order, coupling_dict)

            # Evaluate whether current solution is better than the one found so far
            if feedback < min_feedback:
                min_feedback = feedback
                function_order = list(current_order)

        return function_order, n_eval

    def _single_swap(self, nodes, coupling_dict):
        """Function to find the minimum number of feedback loops using the single-swap method: improve the solution
         by searching for a better position for each node

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return: function order
        :rtype: list
        """

        converged = False

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_size = self.get_feedback_info(nodes, coupling_dict)

        # Keep track of number of evaluated function orders
        n_eval = 0

        while not converged:
            new_iteration = False

            # Move each node until a better solution is found
            for idx in range(len(best_order)):
                node = best_order[idx]

                # Get feedback information for each node placement
                for position in range(len(best_order)):

                    # Skip current solution
                    if idx == len(best_order) - position - 1:
                        continue
                    # Copy current solution
                    new_order = list(best_order)
                    # Delete current node
                    new_order.pop(idx)
                    # Insert node at new position (starting from the back)
                    new_order.insert(len(best_order) - position - 1, node)
                    n_eval += 1
                    feedback, size = self.get_feedback_info(new_order, coupling_dict)
                    # Check whether new order is an improvement
                    if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                        best_order = list(new_order)
                        min_feedback = feedback
                        min_size = size
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        function_order = list(best_order)

        return function_order, n_eval

    def _two_swap(self, nodes, coupling_dict):
        """Function to find the minimum number of feedback loops using the two-swap method: improve the solution
        by swapping two nodes

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return: function order
        :rtype: list
        """

        converged = False

        # Keep track of number of evaluated function orders
        n_eval = 0

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_size = self.get_feedback_info(best_order, coupling_dict)

        while not converged:
            new_iteration = False

            # Swap two nodes until a better solution is found
            for i in range(len(nodes)):
                for j in range(len(nodes) - (i + 1)):

                    # Copy current solution
                    neighbor_solution = list(best_order)
                    # Swap two nodes to get a neighbor solution
                    neighbor_solution[i], neighbor_solution[-j - 1] = best_order[-j - 1], best_order[i]
                    # Get feedback information of the neighbor solution
                    n_eval += 1
                    feedback, size = self.get_feedback_info(neighbor_solution, coupling_dict)
                    # Check whether the neighbor solution is a better than the current solution
                    if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                        best_order = list(neighbor_solution)
                        min_feedback = feedback
                        min_size = size
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        function_order = best_order

        return function_order, n_eval

    def _branch_and_bound(self, nodes, coupling_dict):
        """Function to find the minimum number of feedback loops using the branch-and-bound method: search the solution
        space in a systematic way to find the exact solution

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return: function order
        :rtype: list
        """

        active_branches = []

        # Keep track of number of evaluated function orders
        n_eval = 0

        # Calculate lower bound for each initial branch
        for node in nodes:
            node = [node]
            n_eval += 1
            lower_bound_feedback = self._get_lower_bound_branch_and_bound(node, nodes, coupling_dict)
            active_branches.append([node, lower_bound_feedback])

        while True:
            # Get the branches with the lowest feedback
            min_feedback = min(branch[1] for branch in active_branches)
            best_branches = [branch for branch in active_branches if branch[1] == min_feedback]

            # Select the longest branch as best branch
            selected_branch = max(best_branches, key=lambda x: len(x[0]))

            # Check whether the branch is a complete solution. If so, the best solution is found and iteration stopped
            if len(selected_branch[0]) == len(nodes):
                break

            # If branch is not a complete solution:
            # Explore branch and add children of selected branch to the list with active nodes
            for node in nodes:
                if node not in selected_branch[0]:
                    node = [node]
                    current_order = selected_branch[0] + node
                    n_eval += 1
                    lower_bound_feedback = self._get_lower_bound_branch_and_bound(current_order, nodes, coupling_dict)
                    active_branches.append([current_order, lower_bound_feedback])

            # Delete explored branch
            del active_branches[active_branches.index(selected_branch)]

        function_order = selected_branch[0]

        return function_order, n_eval

    def _get_lower_bound_branch_and_bound(self, branch, nodes, coupling_dict):
        """Function to calculate the lower bound of a branch in the branch and bound algorithm.
        The lower bound is defined as the amount of feedback loops that are guaranteed to occur if the
        selected nodes are placed at the beginning of the order

        :param branch: the nodes in the branch
        :type branch: list
        :param nodes: the nodes that are considered in the sequencing problem
        :type nodes: list
        :return: lower bound
        :rtype: int
        """

        # Get a random function order with the nodes of the branch at the start
        function_order = list(branch)
        for node in nodes:
            if node not in function_order:
                function_order.append(node)

        # Calculate lower bound for the number of feedback loops
        feedback = 0
        for idx1, function1 in enumerate(branch):
            for idx2, function2 in enumerate(function_order[idx1 + 1:]):
                if function2 in coupling_dict[function1]:
                    feedback += coupling_dict[function1][function2]

        return feedback

    def _genetic_algorithm(self, nodes, coupling_dict):

        from deap import base
        from deap import creator
        from deap import tools
        from deap import algorithms

        # Settings GA
        CXPB = 0.63
        MUTPB = 0.4
        NGEN = 250
        INDPB = 0.11
        pop_size = 300

        # Make mapping of nodes to sequence of integers
        mapping = copy.deepcopy(nodes)

        # Create fitness and individual class
        creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
        creator.create('Individual', list, fitness=creator.FitnessMin)

        # Get toolbox
        toolbox = base.Toolbox()

        # Fill the toolbox with methods
        toolbox.register('indices', random.sample, range(len(nodes)), len(nodes))
        toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indices)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)
        toolbox.register('mate', tools.cxOrdered)
        toolbox.register('mutate', tools.mutShuffleIndexes, indpb=INDPB)
        # toolbox.register('select', tools.selBest)
        toolbox.register('select', tools.selTournament, tournsize=3)
        toolbox.register('evaluate', self._get_fitness_individual, mapping=mapping, coupling_dict=coupling_dict)

        population = toolbox.population(pop_size)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        import time
        t = time.time()
        algorithms.eaSimple(population, toolbox, CXPB, MUTPB, NGEN, halloffame=hof,
                            verbose=True, stats=stats)
        print time.time()-t
        function_order = []
        for idx in hof[0]:
            function_order.append(mapping[idx])
        print 'ga function_order', function_order
        print self.get_feedback_info(function_order, coupling_dict)

        return function_order

    def _get_fitness_individual(self, individual, mapping, coupling_dict):
        """ Function to evaluate the fitness of an individual. Needed for the genetic algorithm
        """

        function_order = []
        for idx in individual:
            function_order.append(mapping[idx])
        feedback, size = self.get_feedback_info(function_order, coupling_dict)

        return feedback

    def get_feedback_info(self, function_order, coupling_dict):
        """Function to determine the number of feedback loops for a given function order

        :param function_order: function order of the nodes
        :type function_order: list
        :param coupling_dict: function couplings
        :type coupling_dict: dict
        :return: number of feedback loops
        :rtype: int
        """

        # Determine number of feedback loops
        n_feedback_loops = 0
        n_disciplines_in_feedback = 0
        for idx1, function1 in enumerate(function_order):
            for idx2, function2 in enumerate(function_order[idx1 + 1:]):
                if function2 in coupling_dict[function1]:
                    n_feedback_loops += coupling_dict[function1][function2]
                    n_disciplines_in_feedback += (idx2 + 2) * coupling_dict[function1][function2]

        return n_feedback_loops, n_disciplines_in_feedback


    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          XML-HANDLING METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #
    def add_variable_default_values(self, xml_file):
        """Method to add the default value of the variables based on a reference XML file containing those values.

        :param xml_file: path (absolute or local) to the XML file containing the default values
        :type xml_file: file
        :return: enriched graph with default values of the variables stored as attributes
        :rtype: self
        """
        # Check the input XML file and parse it
        assert os.path.isfile(xml_file), "Could not find the XML file {}".format(xml_file)
        _parse_check([[xml_file]])
        xml_file = etree.parse(xml_file)

        # Get all variables in the graph
        var_nodes = self.find_all_nodes(category='variable')

        # For each variable, check whether it exists in the reference XML file and add the value.
        for var_node in var_nodes:
            # Get the element in the xml_file
            els = xml_file.xpath(var_node)
            if els:
                el = els[0]
                default_value = el.text
                if default_value:
                    self.nodes[var_node]['default_value'] = default_value
        return


class RepositoryConnectivityGraph(DataGraph):

    PATHS_LIMIT = 1e4    # limit check for select_function_combination_from method
    WARNING_LIMIT = 3e6  # limit for _get_path_combinations method

    def __init__(self, *args, **kwargs):
        super(RepositoryConnectivityGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')

        return cmdows_problem_definition

    # noinspection PyPep8Naming
    def create_mathematical_problem(self, n_disciplines, coupling_strength=None, n_global_var=None, n_local_var=None,
                                    n_coupling_var=None, n_local_constraints=None, n_global_constraints=None, B=None,
                                    C=None, D=None, E=None, F=None, G=None, H=None, I=None, J=None, r=None, s=None,
                                    write_problem_to_textfile=False):
        """Function to get a mathematical problem according to the variable complexity problem as described in:
        Zhang D., Song B., Wang P. and He Y. 'Performance Evaluation of MDO Architectures within a Variable
        Complexity Problem', Mathematical Problems in Engineering, 2017.

        :param n_disciplines: Number of disciplines
        :type n_disciplines: int
        :param coupling_strength: percentage of couplings, 0 no couplings, 1 all possible couplings
        :type coupling_strength: int
        :param n_global_var: Number of global design variables
        :type n_global_var: int
        :param n_local_var: Number of local design variables for each discipline
        :type n_local_var: int
        :param n_coupling_var: Number of output variables for each discipline
        :type n_coupling_var: int
        :param n_local_constraints: Number of local constraints
        :type n_local_constraints: int
        :param n_global_constraints: Number of global constraints
        :type n_global_constraints: int
        :param B: relation between the coupling variables
        :param C: relation between the global design variables and coupling variables
        :param D: relation between the local design variables and coupling variables
        :param E: relation between the global design variables and local constraints
        :param F: relation between the local design variables and local constraints
        :param G: relation between the coupling variables and local constraints
        :param H: relation between the global design variables and global constraints
        :param I: relation between the local design variables and global constraints
        :param J: relation between the coupling variables and global constraints
        :param r: positive scalars to be used for the local constraints
        :type r: float
        :param s: positive scalars to be used for the global constraints
        :type s: float
        :param write_problem_to_textfile: option to write generated problem to a textfile
        :type write_problem_to_textfile: bool
        """

        # TODO Imco add type of B-J in docstring
        # Input assertions
        assert not B if coupling_strength else B is not None, 'Either the coupling strength or the B-matrix must be ' \
                                                              'given'

        mathematical_problem = dict()
        mathematical_problem['n_disciplines'] = n_disciplines

        # Create values for the random elements
        # Number of global design variables
        if n_global_var is None:
            n_global_var = random.randint(1, 3)
        mathematical_problem['n_global_var'] = n_global_var

        # Number of local design variables per discipline
        if n_local_var is None:
            n_local_var = [random.randint(1, 3) for _ in range(n_disciplines)]
        mathematical_problem['n_local_var'] = n_local_var

        # Number of coupling variables per discipline
        if n_coupling_var is None:
            n_coupling_var = [random.randint(1, 5) for _ in range(n_disciplines)]
        mathematical_problem['n_coupling_var'] = n_coupling_var

        # Number of local constraints
        if n_local_constraints is None:
            n_local_constraints = [random.randint(1, 5) for _ in range(n_disciplines)]
        mathematical_problem['n_local_constraints'] = n_local_constraints

        # Number of global constraints
        if n_global_constraints is None:
            n_global_constraints = random.randint(1, 3)
        mathematical_problem['n_global_constraints'] = n_global_constraints

        # Create B-matrix: relation between the coupling variables
        if B is None:
            while True:
                # Initiate matrix
                B = np.zeros((sum(n_coupling_var), sum(n_coupling_var)))

                # Calculate the number of couplings based on the coupling strength
                n_couplings = int(np.ceil(((sum(n_coupling_var)*n_disciplines) - sum(n_coupling_var)) *
                                          coupling_strength))

                # Get a list with all possible couplings between variables and disciplines
                possible_couplings = []
                for discipline in range(n_disciplines):
                    for coupling_var in range(sum(n_coupling_var)):
                        # An output variable of a discipline cannot be an input to the same discipline
                        if sum(n_coupling_var[:discipline]) <= coupling_var < sum(n_coupling_var[:discipline + 1]):
                            continue
                        possible_couplings.append([coupling_var, discipline])

                # Choose random couplings from all possible couplings
                couplings = random.sample(range(len(possible_couplings)), n_couplings)

                # Fill the B-matrix with the chosen couplings
                for coupling in couplings:
                    discipline = possible_couplings[coupling][1]
                    for variable in range(n_coupling_var[discipline]):
                        B[sum(n_coupling_var[:discipline]) + variable][possible_couplings[coupling][0]] = random.choice(
                            range(-5, 0)+range(1, 6))  # Zero is not allowed

                # To ensure convergence the B-matrix must be diagonally dominant
                B_diag = np.sum(np.abs(B), axis=1)
                B_diag = [entry + random.randint(1, 10) for entry in B_diag]
                i, j = np.indices(B.shape)
                B[i == j] = B_diag

                # Test if the matrix is singular by calculating its rank
                rank = np.linalg.matrix_rank(B)
                singular = True if rank < min(B.shape) else False
                if not singular:
                    break
                print 'B matrix is singular, new matrix is generated...'

        else:
            # Test if B matrix is singular by calculating its rank
            rank = np.linalg.matrix_rank(B)
            singular = True if rank < min(B.shape) else False
            assert not singular, 'B matrix is singular'

        mathematical_problem['B-matrix'] = B

        # Create C-matrix: relation between global design variables and coupling variables
        if C is None:
            C = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(sum(n_coupling_var))])
        mathematical_problem['C-matrix'] = C

        # Create D-matrix: relation between local design variables and coupling variables
        if D is None:
            D = np.zeros((sum(n_coupling_var), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for coupling_var in range(n_coupling_var[discipline]):
                        D[sum(n_coupling_var[:discipline]) + coupling_var][sum(n_local_var[:discipline]) + local_var] =\
                            random.choice(range(-5, 0)+range(1, 6))  # Zero is not allowed
        mathematical_problem['D-matrix'] = D

        # Create E-matrix: relation between global design variables and local constraints
        if E is None:
            E = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(sum(n_local_constraints))])
        mathematical_problem['E-matrix'] = E

        # Create F-matrix: relation between local design variables and local constraints
        if F is None:
            F = np.zeros((sum(n_local_constraints), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        F[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_local_var[:discipline]) + local_var] = random.randint(-5, 5)
        mathematical_problem['F-matrix'] = F

        # Create G-matrix: relation between coupling variables and local constraints
        if G is None:
            G = np.zeros((sum(n_local_constraints), sum(n_coupling_var)))
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        G[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_coupling_var[:discipline]) + coupling_var] = \
                            random.choice(range(-5, 0)+range(1, 6))  # Zero is not allowed
        mathematical_problem['G-matrix'] = G

        # Create r-matrix: positive scalars used to calculate local constraint values
        if r is None:
            r = [float(random.randint(1, 5)) for _ in range(sum(n_local_constraints))]
        mathematical_problem['r-matrix'] = r

        # Create H-matrix: relation between global design variables and global constraints
        if H is None:
            H = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(n_global_constraints)])
        mathematical_problem['H-matrix'] = H

        # Create I-matrix: relation between local design variables and global constraints
        if I is None:
            I = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_local_var))] for _ in
                          range(n_global_constraints)])
        mathematical_problem['I-matrix'] = I

        # Create J-matrix: relation between coupling variables and global constraints
        if J is None:
            J = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_coupling_var))] for _ in
                          range(n_global_constraints)])
        mathematical_problem['J-matrix'] = J

        # Create s-matrix: positive scalars used to calculate global constraint values
        if s is None:
            s = [float(random.randint(1, 5)) for _ in range(n_global_constraints)]
        mathematical_problem['s-matrix'] = s

        # Check whether problem is well-formulated
        # Check whether all coupling variables are defined
        for coupling_var in range(sum(n_coupling_var)):
            assert B[coupling_var][coupling_var] != 0, 'Diagonal of B cannot be zero'

        # Check whether output variable is not also an input variable to the same discipline
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                           sum(n_coupling_var[:discipline]) + coupling_var]
                for index, v in enumerate(values):
                    if index != coupling_var:
                        assert v == 0, 'Output variable y{0}_{1} cannot be an input to discipline ' \
                                       'D{0}'.format(discipline + 1, coupling_var + 1)

        # Check whether local variables are not used by other disciplines
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    if local_var_disc != discipline:
                        values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                                   sum(n_local_var[:local_var_disc]) + local_var]
                        assert all(
                            v == 0 for v in values), 'Local variable x{0}_{1} cannot be an input to discipline ' \
                                                     'D{2}, only to discipline D{0}'.format(local_var_disc + 1,
                                                                                            local_var + 1,
                                                                                            discipline + 1)
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if local_var_disc != local_con_disc:
                            assert F[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_local_var[:local_var_disc]) + local_var] == 0, \
                                'Local variable x{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(local_var_disc + 1, local_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # Check whether coupling variables are not used for different local constraints
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if coupling_var_disc != local_con_disc:
                            assert G[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_coupling_var[:coupling_var_disc]) + coupling_var] == 0, \
                                'Coupling variable y{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(coupling_var_disc + 1, coupling_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # All function nodes are defined
        for discipline in range(n_disciplines):  # Disciplines
            self.add_node('D{0}'.format(discipline + 1), category='function')
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_node('G{0}_{1}'.format(discipline+1, local_constraint+1), category='function')
        self.add_node('F', category='function')  # Objective
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_node('G0{0}'.format(constraint + 1), category='function')

        # All variable nodes are defined
        for global_var in range(n_global_var):  # Global design variables
            self.add_node('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                          category='variable',
                          label='x0{0}'.format(global_var + 1))
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_node('/data_schema/global_constraints/g0{0}'.format(constraint + 1),
                          category='variable',
                          label='g0{0}'.format(constraint + 1))
        self.add_node('/data_schema/objective/f',  # Objective
                      category='variable',
                      label='f')
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):  # Local design variables
                self.add_node('/data_schema/local_design_variables/x{0}_{1}'.format(discipline + 1, local_var + 1),
                              category='variable',
                              label='x{0}_{1}'.format(discipline + 1, local_var + 1))
            for coupling_var in range(n_coupling_var[discipline]):  # Coupling variables
                self.add_node('/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1),
                              category='variable',
                              label='y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_node('/data_schema/local_constraints/g{0}_{1}'.format(discipline+1, local_constraint+1),
                              category='variable',
                              label='g{0}_{1}'.format(discipline+1, local_constraint+1))

        # Edges between global variables and function nodes are defined
        for global_var in range(n_global_var):
            for discipline in range(n_disciplines):
                values = C[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]), global_var]
                if not all(v == 0 for v in values):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'D{0}'.format(discipline + 1))
                for local_constraint in range(n_local_constraints[discipline]):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
            self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1), 'F')
            for constraint in range(n_global_constraints):
                self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                              'G0{0}'.format(constraint + 1))

        # Edges between local variables and function nodes are defined
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_local_var[:local_var_disc]) + local_var]
                    if not all(v == 0 for v in values):
                        self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                      local_var + 1), 'D{0}'.format(local_var_disc + 1))
                for local_constraint in range(n_local_constraints[local_var_disc]):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                                                                        local_var + 1),
                                  'G{0}_{1}'.format(local_var_disc + 1, local_constraint + 1))
                self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1, local_var + 1),
                              'F')
                for constraint in range(n_global_constraints):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                  local_var + 1), 'G0{0}'.format(constraint + 1))

        # Edges between coupling variables and function nodes are defined
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for discipline in range(n_disciplines):
                    values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                    if not discipline == coupling_var_disc and not all(v == 0 for v in values):
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'D{0}'.format(discipline + 1))
                    for local_constraint in range(n_local_constraints[discipline]):
                        value = G[sum(n_local_constraints[:discipline]) + local_constraint,
                                  sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                        if value != 0:
                            self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1,
                                                                                            coupling_var + 1),
                                          'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
                self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var +
                                                                                1), 'F')
                for constraint in range(n_global_constraints):
                    if J[constraint][sum(n_coupling_var[:coupling_var_disc]) + coupling_var] != 0:
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'G0{0}'.format(constraint + 1))

        # Edges between function nodes and coupling variables are defined
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):  # Disciplines
                self.add_edge('D{0}'.format(discipline + 1),
                              '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_edge('G{0}_{1}'.format(discipline + 1, local_constraint + 1),
                              '/data_schema/local_constraints/g{0}_{1}'.format(discipline + 1, local_constraint + 1))
        self.add_edge('F', '/data_schema/objective/f')  # Objective
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_edge('G0{0}'.format(constraint + 1), '/data_schema/global_constraints/g0{0}'.format(constraint +
                                                                                                         1))

        # Add equations
        self.add_equation_labels(self.get_function_nodes(), labeling_method='node_id')

        # Add discipline analysis equations
        for discipline in range(n_disciplines):
            for output_var in range(n_coupling_var[discipline]):
                equation = ""
                for global_var in range(n_global_var):
                    if C[sum(n_coupling_var[:discipline]) + output_var][global_var] != 0:
                        equation += '-{0}*x0{1}'.format(C[sum(n_coupling_var[:discipline]) + output_var][global_var],
                                                        global_var + 1)
                for local_var_disc in range(n_disciplines):
                    for local_var in range(n_local_var[local_var_disc]):
                        if D[sum(n_coupling_var[:discipline]) + output_var][
                                    sum(n_local_var[:local_var_disc]) + local_var] != 0:
                            equation += '-{0}*x{1}_{2}'.format(D[sum(n_coupling_var[:discipline]) + output_var][
                                                                sum(n_local_var[:local_var_disc]) + local_var],
                                                               local_var_disc + 1, local_var + 1)
                for coupling_var_disc in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[coupling_var_disc]):
                        if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:coupling_var_disc]) +
                           coupling_var] != 0 and (discipline, output_var) != (coupling_var_disc, coupling_var):
                            equation += '-{0}*y{1}_{2}'.format(B[sum(n_coupling_var[:discipline]) + output_var][sum(
                                n_coupling_var[:coupling_var_disc]) + coupling_var], coupling_var_disc + 1,
                                                              coupling_var + 1)
                if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:discipline]) + output_var] != 1:
                    equation = '({0})/{1}'.format(equation, B[sum(n_coupling_var[:discipline]) + output_var][
                        sum(n_coupling_var[:discipline]) + output_var])
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'Python')
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'LaTeX')

        # Add objective function equation
        objective = ""
        for global_var in range(n_global_var):
            objective += '+x0{0}'.format(global_var + 1)
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):
                objective += '+x{0}_{1}'.format(discipline + 1, local_var + 1)
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                objective += '+y{0}_{1}'.format(discipline + 1, coupling_var + 1)
        self.add_equation('F', '({0})**3'.format(objective), 'Python')
        self.add_equation('F', '({0})^3'.format(objective), 'LaTeX')

        # Add global constraint function equations
        for constraint in range(n_global_constraints):
            constraint_eq = ""
            for global_var in range(n_global_var):
                constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                if H[constraint][global_var] != 0:
                    constraint_eq += '+{0}*x0{1}'.format(H[constraint][global_var], global_var + 1)
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(discipline + 1, local_var + 1)
                    if I[constraint][sum(n_local_var[:discipline]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(I[constraint][sum(n_local_var[:discipline]) +
                                                                              local_var], discipline + 1, local_var + 1)
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    if J[constraint][sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                        constraint_eq += '+{0}*y{1}_{2}'.format(
                            J[constraint][sum(n_coupling_var[:discipline]) + coupling_var], discipline + 1,
                            coupling_var + 1)
            constraint_eq += '-{0}'.format(s[constraint])
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'Python')
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'LaTeX')

        # Add local constraint function equations
        for local_con_disc in range(n_disciplines):
            for local_constraint in range(n_local_constraints[local_con_disc]):
                constraint_eq = ""
                for global_var in range(n_global_var):
                    constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                    if E[sum(n_local_constraints[:local_con_disc]) + local_constraint, global_var] != 0:
                        constraint_eq += '+{0}*x0{1}'.format(E[sum(n_local_constraints[:local_con_disc]) +
                                                               local_constraint][global_var], global_var + 1)
                for local_var in range(n_local_var[local_con_disc]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(local_con_disc + 1, local_var + 1)
                    if F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(
                            F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var], local_con_disc + 1, local_var + 1)
                for discipline in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[discipline]):
                        if G[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                    sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                            constraint_eq += '+{0}*y{1}_{2}'.format(G[sum(n_local_constraints[:local_con_disc]) +
                                                                      local_constraint][sum(n_coupling_var[:discipline])
                                                                                        + coupling_var], discipline + 1,
                                                                    coupling_var + 1)
                constraint_eq += '-{}'.format(r[sum(n_local_constraints[:local_con_disc]) + local_constraint])
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'Python')
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'LaTeX')

        # Get function order
        function_order = []
        for discipline in range(n_disciplines):
            function_order += ['D{0}'.format(discipline + 1)]
        for discipline in range(n_disciplines):
            for local_constraint in range(n_local_constraints[discipline]):
                function_order += ['G{0}_{1}'.format(discipline + 1, local_constraint + 1)]
        for constraint in range(n_global_constraints):
            function_order += ['G0{0}'.format(constraint + 1)]
        function_order += ['F']
        mathematical_problem['function_order'] = function_order

        # Write problem to text file
        if write_problem_to_textfile:
            f = open("Problem_formulation.txt", "w")
            f.write('Number of disciplines: ' + str(n_disciplines) + '\n')
            f.write('Number of global variables: ' + str(n_global_var) + '\n')
            f.write('Number of local variables: ' + str(n_local_var) + '\n')
            f.write('Number of coupling variables: ' + str(n_coupling_var) + '\n')
            f.write('Number of global constraints: ' + str(n_global_constraints) + '\n')
            f.write('B-matrix: ' + str(B) + '\n')
            f.write('C-matrix: ' + str(C) + '\n')
            f.write('D-matrix: ' + str(D) + '\n')
            f.write('H-matrix: ' + str(H) + '\n')
            f.write('I-matrix: ' + str(I) + '\n')
            f.write('J-matrix: ' + str(J) + '\n')
            f.write('s-matrix: ' + str(s) + '\n')
            f.close()

        return mathematical_problem

    # -----------------------------------------------------------------------------------------------------------------#
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # -----------------------------------------------------------------------------------------------------------------#

    def get_function_paths_by_objective(self, *args, **kwargs):
        """This function takes an arbitrary amount of objective nodes as graph sinks and returns all path combinations
        of tools.

        :param args: arbitrary amount of objective nodes
        :type args: list, str
        :param kwargs: filter options to limit possible path combinations
        :type kwargs: bool, str
        :return: all possible FPG path combinations for the provided objective nodes

        If no arguments are given, user is prompted to select objectives from the graph.

        .. hint:: The tool combinations are found using the function itertools.product() and can lead to significant
            computation times for large graphs. If this is the case, the user is prompted whether to continue or not.

        A variety of filters can be applied to the search of possible tools combinations, some of which reduce the
        computation time.

        .. note:: kwargs:

            * obj_vars_covered - ensures that all objective variables are used in tool configurations
            * ignore_funcs - ignores functions for the config
            * source - source node; if provided, must be in config
        """

        # TODO: Add filters
        # Filters:
        # include_functions - returned path combinations must include the indicated functions
        # exclude_functions - returned path combinations must exclude the indicated functions
        # min_funcs - only returns paths that have a minimum amount if functions
        # max_funcs - only returns paths that have a maximum amount of functions
        # obj_vars_covered - only returns paths where ALL objective variables are covered

        # make copy of self
        graph = copy.deepcopy(self)

        # get and check keyword arguments
        obj_vars_covered = kwargs.get('objective_variables_covered', False)  # TODO: Implement this option
        assert isinstance(obj_vars_covered, bool)

        ignore_funcs = None
        if "ignore_funcs" in kwargs:
            ignore_funcs = kwargs["ignore_funcs"]
            for func in ignore_funcs:
                assert func in self, "Function node {} must be present in graph.".format(func)

        # source = None
        # if "source" in kwargs:
        #    source = kwargs["source"]
        #    assert graph.node_is_function(source), "Source node must be a function."

        min_funcs = None
        if "min_funcs" in kwargs:
            min_funcs = kwargs["min_funcs"]
            assert isinstance(min_funcs, int)

        max_funcs = float("inf")
        if "max_funcs" in kwargs:
            max_funcs = kwargs["max_funcs"]
            assert isinstance(max_funcs, int)

        # get all function nodes in graph
        # func_nodes = graph.get_function_nodes()

        # [step 1] check if function nodes provided
        if args:
            objs = list(args)
            for arg in objs:
                assert graph.node_is_function(arg), "Provided Objective must be function."

        else:  # if not provided, ask user to select
            objs = graph.select_objectives_from_graph()

        # intermediate check that OBJ function node given
        assert objs, "No valid Objective Functions provided."
        logger.info('Function configurations are considered for objective(s): [{}]'.format(
            ', '.join(str(x) for x in objs)))

        # [Step 2]: Get OBJ function variables in graph
        obj_variables = []
        for objFunc in objs:
            for u, v in graph.in_edges(objFunc):
                obj_variables.append(u)

        # [Step 3]: Get function graph (remove all variable nodes and replace them with corresponding edges)
        if obj_vars_covered:
            # if obj_vars_covered, objective vars will be present in paths; easy to check their presence
            function_graph = graph.get_function_graph(keep_objective_variables=True)
        else:
            function_graph = graph.get_function_graph()

        # [Step 4]: get all (simple) paths to sinks
        all_simple_paths = set()  # making sure that no duplicate paths in list
        for sink in objs:
            anc_nodes = nx.ancestors(function_graph, sink)
            for anc in anc_nodes:
                if function_graph.node_is_function(anc):  # do not take objVars into account

                    # add every path to sink as frozenset
                    for path in nx.all_simple_paths(function_graph, anc, sink):  # TODO: Test for multiple sinks!
                        all_simple_paths.add(frozenset(path))

        # [Step 5]: Apply (some) filters
        # TODO: Apply some filters here

        # [Step 6]: group paths according into subsets
        path_subsets = self._group_elements_by_subset(*all_simple_paths)

        # [Step 7]: Get all combinations between all feedback tool combinations
        subsets_list = [subset for _, subset in path_subsets.iteritems()]

        # remove all paths that have ignore-functions
        if ignore_funcs:
            for subset in subsets_list:
                remove = []
                for path in subset:
                    if not ignore_funcs.isdisjoint(path):
                        remove.append(path)
                for p in remove:
                    subset.remove(p)

        all_fpg_paths = function_graph.get_path_combinations(*subsets_list, min_funcs=min_funcs, max_funcs=max_funcs)

        return all_fpg_paths

    def get_path_combinations(self, *args, **kwargs):
        """This function takes lists of subsets and generates all possible combinations between them.

        :param args: lists of subsets that will be used to find configurations
        :type args: list
        :param kwargs: see optional arguments
        :type kwargs: int
        :return: set of all unique path combinations

        This is done by using the itertools.product() function. If the amount of expected evaluations exceeds a pre-set
        minimum, the user will be asked if to continue or not; because the process can take a long time and use up many
        resources.

        .. note:: Optional arguments:

            * min_func: minimum amount of functions in each configuration
            * max_func: maximum amount of functions in each configuration
        """

        # get list of subsets
        subsets = list(args)

        # kwargs check
        # min_funcs = None
        # if "min_funcs" in kwargs:
        #     min_funcs = kwargs["min_funcs"]
        #     assert isinstance(min_funcs, int)

        max_funcs = kwargs.get('max_funcs', float("inf"))

        # append empty string to each list (to get ALL combinations; check itertools.product()) and count evaluations
        count = 1
        for subset in subsets:
            subset.append('')
            count *= len(subset)
        count -= 1

        # If many combinations are evaluated, warn user and ask if to continue
        if count > self.WARNING_LIMIT:
            logger.warning('Only ' + str(self.WARNING_LIMIT) + ' tool combinations can be evaluated with the current ' +
                           ' settings. However, ' + str(count) + ' evaluations are now selected. You can decrease ' +
                           'this number by applying filters. You could also increase the WARNING_LIMIT but be aware ' +
                           'that the process can take a considerable amount of time and resources then.')
            return list()

        # get all tool combinations using subsets
        all_path_combinations = set()

        for comb in itertools.product(*subsets):
            # combine separate lists into one for each combo
            # clean_comb = frozenset(itertools.chain.from_iterable(comb))
            clean_comb = frozenset().union(*comb)
            if len(clean_comb) > max_funcs or len(clean_comb) > max_funcs:
                continue
            # add to list if combo is not empty and does not yet exist in list
            if clean_comb and clean_comb not in all_path_combinations:
                all_path_combinations.add(clean_comb)

        return all_path_combinations

    def _get_feedback_paths(self, path, functions_only=True):
        # TODO: Add docstring

        # functions_only only passes on argument, not used in this function
        assert isinstance(functions_only, bool)

        # get feedback nodes if exist in path
        # empty strings in tpls are necessary for proper functioning
        feedback = self._get_feedback_nodes(path, functions_only=functions_only)

        # get path combinations in case feedback loops exist in path
        feedback_combis = []
        for prod in itertools.product([tuple(path)], *feedback):
            # remove all empty products
            removed_empty = (x for x in prod if x)  # remove empty strings
            # remove brackets created by product; create frozenset to make object immutable
            removed_brackets = frozenset(itertools.chain.from_iterable(removed_empty))

            # if combination is not empty and does not already exist in list, add to list
            if removed_brackets not in feedback_combis and removed_brackets:
                feedback_combis.append(removed_brackets)

        return feedback_combis

    def _get_feedback_nodes(self, main_path, functions_only=True):
        # TODO: Add docstring

        assert isinstance(functions_only, bool)
        feed_back = []  # contains feed_back nodes; each feed_back loop is in a separate list

        for main_path_idx, main_path_node in enumerate(main_path):
            search_loop = []
            start_index = -1

            if functions_only:
                if not self.node_is_function(main_path_node):
                    continue

            # iterate through edges recursively and add feed_back loops if they exist
            self._iter_out_edges(main_path_idx, main_path, main_path_node, start_index, search_loop, feed_back,
                                 functions_only)

        return feed_back

    def _iter_out_edges(self, main_path_idx, main_path, node, search_index, search_loop, feed_back,
                        functions_only=True):
        # TODO: Add docstring

        search_index += 1

        for edge in self.out_edges(node):
            if functions_only:
                if not self.node_is_function(edge[1]):
                    continue
            if edge[1] in search_loop:
                continue
            search_loop.insert(search_index, edge[1])
            if edge[1] in main_path and main_path.index(edge[1]) <= main_path_idx:
                feed_back.append(("", search_loop[:search_index]))
            elif edge[1] not in main_path:
                self._iter_out_edges(main_path_idx, main_path, edge[1], search_index, search_loop, feed_back,
                                     functions_only)

        return

    # noinspection PyMethodMayBeStatic
    def _group_elements_by_subset(self, *args):
        """This function takes arguments of type set/frozenset and groups them by subset.

        All elements that are subsets of another element are grouped together and returned in a dict with the longest
        superset as keywords.

        Example:
        >> list = [set([1]),set([1,2]),set([3]),set([0,1,2])]
        >> sub_sets = graph._group_elements_by_subset(*list)
        >> sub_sets
        >> {set([0,1,2]): [set([1]), set([1,2]),set([0,1,2])], set([3]):[set([3])]}

        :param args: arbitrary argument
        :type args: set, frozenset
        :return: dict with grouped arguments by longest subset in group
        :rtype: dict
        """

        for arg in args:
            assert isinstance(arg, (set, frozenset))
        set_list = list(args)

        sub_sets = {}
        skip = []
        for i, path in enumerate(set_list):
            if path in skip:
                continue

            set_found = False
            for comp in set_list[i + 1:]:
                if comp in skip:
                    continue

                if path == comp:
                    skip.append(comp)
                    continue

                if path.issubset(comp):
                    set_found = True

                    if comp not in sub_sets:
                        sub_sets[comp] = [comp]

                    if path in sub_sets:
                        sub_sets[comp] += sub_sets[path]
                        sub_sets.pop(path, None)
                    else:
                        sub_sets[comp].append(path)

                    skip.append(path)
                    break

                elif path.issuperset(comp):
                    set_found = True
                    skip.append(comp)

                    if path not in sub_sets:
                        sub_sets[path] = [path]
                    sub_sets[path].append(comp)

                    if comp in sub_sets:
                        sub_sets[path] += sub_sets[comp]
                        sub_sets.pop(comp, None)
                    continue

            if not set_found and path not in sub_sets:
                sub_sets[path] = []
                sub_sets[path].append(path)

        return sub_sets

    def select_function_combination_from(self, *args, **kwargs):
        """This function takes all provided workflow configurations and lists them according to their characteristics.

        :param args: workflow configurations
        :type args: list
        :param kwargs: see optional arguments
        :type kwargs: bool, str, int
        :return: sorted list of workflow configurations
        :rtype: list

        .. note:: Optional arguments:

            * 'print_combos' - option to print the combinations in a table
            * 'n_limit' - amount of combinations that will be printed in the table
            * 'sort_by' - characteristic to sort workflow configurations by
            * 'sort_by ascending' - option to sort workflow configurations by ascension
            * 'plot_combos' - option to plot the combinations in a graph

        The user can choose the workflow configuration from the list.

        A warning is given to the user if the amount of total configurations exceeds n = 1e4.
        Print limit is set to [0-20] by default.

        .. note:: sort_by must be one of ["couplings", "system_inputs", "edges", "nodes"].
        """

        # make sure arguments provided
        assert args, "At least one argument must be provided."

        # check number of arguments; prompt user to continue or not
        if len(args) > self.PATHS_LIMIT:
            msg = "More than {} workflow configurations provided; this could take a lot of time to analyze. Continue?"
            usr_sel = prompting.user_prompt_yes_no(message=msg)
            if not usr_sel:
                print "Combination selection cancelled."
                return

        # check if all arguments are non-string iterables (list, tuple, set, frozenset,...)
        assert all([hasattr(arg, '__iter__') for arg in args]), "All arguments must be non-string iterables."

        # check KWARGS HERE
        print_combos = True
        if "print_combos" in kwargs:
            print_combos = kwargs["print_combos"]
            assert isinstance(print_combos, bool)

        # if no limit given, limit for displaying combos is set to 10
        n_limit = 21
        if "n_limit" in kwargs:
            n_limit = kwargs["n_limit"]
            assert isinstance(n_limit, int)
            assert n_limit > 0, "Argument must be positive."

        # if no sort_by argument given, it sorts combos by "holes"
        sort_by = "functions"
        if "sort_by" in kwargs:
            sort_by = kwargs["sort_by"]
            assert isinstance(sort_by, basestring)
            assert sort_by in self.GRAPH_PROPERTIES, "Argument must be in self.GRAPH_PROPERTIES."

        sort_by_ascending = False
        if "sort_by_ascending" in kwargs:
            sort_by_ascending = kwargs["sort_by_ascending"]
            assert isinstance(sort_by_ascending, bool)

        plot_combos = True
        if "plot_combos" in kwargs:
            plot_combos = kwargs["plot_combos"]
            # TODO: Add assert for type of plot, plot variables etc

        # ------------------------------------------------------------- #

        # iterate through arguments and analyze their graphs
        graph_analysis = {}
        for arg in args:
            # TODO: Implement an option to get graph data from a db instead of analyzing each subgraph (if available)
            # TODO: This saves time in large graphs!

            # initiate dict to save subgraph data to
            graph_analysis[arg] = {}

            # get subgraph in order to get fast analysis
            sub_graph = self.get_subgraph_by_function_nodes(*arg)

            # subgraph analysis
            graph_analysis[arg] = sub_graph.get_graph_properties()

        # sort configuration list
        combo_list = list(graph_analysis.items())
        sorted_combos = sorted(combo_list, key=lambda x: x[1][sort_by], reverse=not sort_by_ascending)

        if plot_combos:

            # plot
            plt_x, plt_y, annotes = [], [], []
            for k, v in graph_analysis.iteritems():
                plt_y.append(v["system_inputs"])
                plt_x.append(v["functions"])
                annotes.append(str(list(k)))

            # TODO: Automate the plotting of graphs (data, labels, etc)!
            fig, ax = plt.subplots()
            ax.scatter(plt_x, plt_y)
            af = AnnoteFinder(plt_x, plt_y, annotes, ax=ax)
            fig.canvas.mpl_connect('button_press_event', af)
            plt.xlabel('Tools')
            plt.ylabel('System Inputs')
            plt.show()

        # print configs
        if print_combos:
            print_list = []
            for combo, properties in sorted_combos:
                prop_list = [properties[prop] for prop in self.GRAPH_PROPERTIES]
                prop_list.append(list(combo))
                print_list.append(prop_list)

            hdr = self.GRAPH_PROPERTIES + ["Configuration"]
            msg = "The following tool configurations were found in the graph:"
            printing.print_in_table(print_list[:n_limit], message=msg, headers=hdr, print_indeces=True)

        # select combo for FPG
        # TODO: finish!
        # sel_mssg = "Please select a tool combination from the list above:"
        sel_list = [sorted_combo[0] for sorted_combo in sorted_combos[:n_limit]]
        # user_sel= PRO.user_prompt_select_options(*sel_list, message=sel_mssg, allow_multi=False, allow_empty=False)
        user_sel = [sel_list[0]]

        return next(iter(user_sel))

    def get_fpg_by_function_nodes(self, *args):
        """This function creates a new (FPG)-graph based on the selected function nodes.

        :param args: arbitrary amount of graph nodes
        :type args: list, str
        :return: new fpg graph
        :rtype: FundamentalProblemGraph
        """

        # TODO: Assert that nodes are function nodes

        # get subgraph from function nodes
        sub_graph = self.get_subgraph_by_function_nodes(*args)

        # create FPG from sub-graph
        fpg = nx.compose(FundamentalProblemGraph(), sub_graph)
        # TODO: Make sure that the name of the graph is changed!

        return fpg

    def get_fpg_based_on_sinks(self, list_of_sinks, name='FPG'):
        """Function to get the a Fundamental Problem Graph based on a list of sinks/required output variables.

        :param list_of_sinks: list with strings that specify the desired output
        :type list_of_sinks: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        fpg = FundamentalProblemGraph(sinks=list_of_sinks, name=name)
        for sink in list_of_sinks:
            ancestors = nx.ancestors(self, sink)
            ancestors.add(sink)
            fpg_sink = self.subgraph(ancestors)
            fpg = nx.compose(fpg, fpg_sink)

        return fpg

    def get_fpg_based_on_list_functions(self, list_of_functions, name='FPG'):
        """Function to get a Fundamental Problem Graph based on a list of functions.

        :param list_of_functions: list with strings that specify the desired functions
        :type list_of_functions: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, kb_path=self.graph['kb_path'],
                                      name=name)

        # build fpg by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg

    def get_fpg_based_on_function_nodes(self, *args, **kwargs):
        """Function to get the Fundamental Problem Graph based on a list of (or a single) function.

        :param args: node names of functions of interest
        :type args: str
        :param kwargs: name: name of the graph to be generated
        :type kwargs: name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # Input assertions
        name = kwargs.get('name', 'FPG')
        assert isinstance('name', str)
        list_of_functions = list(args)
        for function in list_of_functions:
            assert function in self.nodes, 'Defined function node ' + str(function) + ' does not exist in the graph.'

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, name=name)

        # build FPG by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg


class FundamentalProblemGraph(DataGraph, KeChainMixin):

    def __init__(self, *args, **kwargs):
        super(FundamentalProblemGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')
        out_nodes = self.find_all_nodes(subcategory='all outputs')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for out_node in out_nodes:
            category_check, i_not = check('problem_role' not in self.nodes[out_node],
                                          'The attribute problem_role is missing on the output node %s.'
                                          % str(out_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1
        for func_node in func_nodes:
            category_check, i_not = check('problem_role' not in self.nodes[func_node],
                                          'The attribute problem_role is missing on the function node %s.'
                                          % str(func_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    def _check_category_b(self):
        """Extended method to perform a category B check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_b()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')

        # Checks
        category_check, i = check('problem_formulation' not in self.graph,
                                  'The problem formulation attribute is missing on the graph.',
                                  status=category_check,
                                  category='B',
                                  i=i)
        if category_check:
            category_check, i = check('mdao_architecture' not in self.graph['problem_formulation'],
                                      'The mdao_architecture attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['mdao_architecture'] not in
                                          self.OPTIONS_ARCHITECTURES,
                                          'Invalid mdao_architecture attribute in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('convergence_type' not in self.graph['problem_formulation'],
                                      'The convergence_type attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['convergence_type'] not in
                                          self.OPTIONS_CONVERGERS,
                                          'Invalid convergence_type %s in the problem formulation.'
                                          % self.graph['problem_formulation']['convergence_type'],
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_order' not in self.graph['problem_formulation'],
                                      'The function_order attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                func_order = self.graph['problem_formulation']['function_order']
                category_check, i = check(len(func_order) != len(func_nodes),
                                          'There is a mismatch between the FPG functions and the given function_order, '
                                          + 'namely: %s.' % set(func_nodes).symmetric_difference(set(func_order)),
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_ordering' not in self.graph['problem_formulation'],
                                      'The function_ordering attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if 'allow_unconverged_couplings' in self.graph['problem_formulation']:
                allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']
                category_check, i = check(not isinstance(allow_unconverged_couplings, bool),
                                          'The setting allow_unconverged_couplings should be of type boolean.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            if self.graph['problem_formulation']['mdao_architecture'] in get_list_entries(self.OPTIONS_ARCHITECTURES, 5,
                                                                                          6):  # DOE
                category_check, i = check('doe_settings' not in self.graph['problem_formulation'],
                                          'The doe_settings attribute is missing in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
                if category_check:
                    category_check, i = check('doe_method' not in self.graph['problem_formulation']['doe_settings'],
                                              'The doe_method attribute is missing in the doe_settings.',
                                              status=category_check,
                                              category='B',
                                              i=i)
                    if category_check:
                        doe_method = self.graph['problem_formulation']['doe_settings']['doe_method']
                        category_check, i = check(self.graph['problem_formulation']['doe_settings']['doe_method'] not
                                                  in self.OPTIONS_DOE_METHODS,
                                                  'Invalid doe_method (%s) specified in the doe_settings.' % doe_method,
                                                  status=category_check,
                                                  category='B',
                                                  i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 0, 1, 2):  # FF, LHC, Monte Carlo
                            category_check, i = check('doe_runs' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The doe_runs attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['doe_runs'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['doe_runs'] < 0
                                category_check, i = check(test,
                                                          'Invalid doe_runs (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['doe_runs'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 1, 2):  # LHC, Monte Carlo
                            category_check, i = check('doe_seed' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The doe_seed attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['doe_seed'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['doe_seed'] < 0
                                category_check, i = check(test,
                                                          'Invalid doe_seed (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['doe_seed'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)

        # Return
        return category_check, i

    def _check_category_c(self):
        """Extended method to perform a category C check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_c()

        # Get information
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        conv_type = self.graph['problem_formulation']['convergence_type']
        allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']

        # Check if architecture and convergence_type match
        # -> match for converged-MDA, MDF, converged-DOE
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[1], self.OPTIONS_ARCHITECTURES[3], self.OPTIONS_ARCHITECTURES[6]]:
            category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match IDF
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[2]]:
            category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match for unconverged-MDA, IDF, unconverged-OPT, unconverged-DOE
        # TODO: Sort out unconverged coupling mess
        # if mdao_arch in [self.OPTIONS_ARCHITECTURES[0], self.OPTIONS_ARCHITECTURES[4], self.OPTIONS_ARCHITECTURES[5]]:
        #     if allow_unconverged_couplings:
        #         category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are allowed, the convergence method None has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)
        #     else:
        #         category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are not allowed, a convergence method has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)

        # For architectures using convergence, check whether this is necessary
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            if mdao_arch == self.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-MDA".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[3]:  # MDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=False),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-DOE".',
                                          status=category_check,
                                          category='C',
                                          i=i)

        # For architectures not using convergence, check whether this is allowed
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            # unconverged-MDA, unconverged-OPT, unconverged-DOE
            if mdao_arch in get_list_entries(self.OPTIONS_ARCHITECTURES, 0, 4, 5):
                if not allow_unconverged_couplings:
                    category_check, i = check(self.check_for_coupling(coup_funcs, only_feedback=True),
                                              'Inconsistent problem formulation, no feedback coupling was expected. '
                                              'Architecture should be set to something using convergence (e.g. MDF). '
                                              'Or setting allow_unconverged_couplings should be set to True.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                if category_check and conv_type is not self.OPTIONS_CONVERGERS[2]:
                    category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                              conv_type == self.OPTIONS_CONVERGERS[1] else False),
                                              'Inconsistent problem formulation, expected coupling missing. '
                                              'Architecture should be unconverged variant with convergence type None.',
                                              status=category_check,
                                              category='C',
                                              i=i)

        # Check the feedforwardness of the pre-coupling functions
        if category_check:
            precoup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[0]]
            category_check, i = check(self.check_for_coupling(precoup_funcs, only_feedback=True),
                                      'Pre-coupling functions contain feedback variables. '
                                      'Pre-coupling functions should be adjusted.',
                                      status=category_check,
                                      category='C',
                                      i=i)

        # Check whether the necessary variables have been marked with the problem_role attribute
        if category_check:
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unconverged-OPT
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                # Check the design variables connections
                for des_var_node in des_var_nodes:
                    des_var_sources = self.get_sources(des_var_node)
                    # noinspection PyUnboundLocalVariable
                    category_check, i_not = check(not set(des_var_sources).issubset(precoup_funcs),
                                                  'Design variable %s has a source after the pre-coupling functions. '
                                                  'Adjust design variables or function order to solve this.'
                                                  % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(des_var_node) == 0,
                                                  'Design variable %s does not have any targets. Reconsider design '
                                                  'variable selection.' % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                i += 2
                constraint_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]])
                objective_node = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
                category_check, i = check(len(objective_node) != 1,
                                          '%d objective variables are specified. Only one objective node is allowed. '
                                          'Use the problem_role attribute for this.' % len(objective_node),
                                          status=category_check,
                                          category='C',
                                          i=i)
                constraint_functions = list()
                for idx, node in enumerate(objective_node + constraint_nodes):
                    category_check, i_not = check(self.in_degree(node) != 1,
                                                  'Invalid in-degree of ' + str(self.in_degree(node)) +
                                                  ', while it should be 1 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(node) != 0,
                                                  'Invalid out-degree of '+ str(self.out_degree(node))
                                                  + ', while it should be 0 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                    if idx == 0:
                        objective_function = list(self.in_edges(node))[0][0]
                    elif not (list(self.in_edges(node))[0][0] in set(constraint_functions)):
                        constraint_functions.append(list(self.in_edges(node))[0][0])
                i += 2
                if category_check:
                    # Check that the objective function is unique (not also a constraint function)
                    # noinspection PyUnboundLocalVariable
                    category_check, i = check(objective_function in constraint_functions,
                                              'Objective function should be a separate function.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                    optimizer_functions = [objective_function] + constraint_functions
                    # Check that all optimizer function are post-coupling functions for IDF and MDF
                    if mdao_arch in self.OPTIONS_ARCHITECTURES[2:4]:
                        func_cats = self.graph['problem_formulation']['function_ordering']
                        diff = set(optimizer_functions).difference(func_cats[self.FUNCTION_ROLES[2]])
                        coup_check = self.check_for_coupling(optimizer_functions, only_feedback=False)
                        category_check, i = check(diff,
                                                  'Not all optimizer functions are not post-coupling functions, '
                                                  'namely: %s' % diff,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                        category_check, i = check(coup_check,
                                                  'The optimizer functions %s are not independent of each other.'
                                                  % optimizer_functions,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[:2] + self.OPTIONS_ARCHITECTURES[5:7]:
                # unc-MDA, con-MDA, unc-DOE, con-DOE
                # Check whether quantities of interest have been defined.
                qoi_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[3]])
                category_check, i = check(len(qoi_nodes) == 0,
                                          'No quantities of interest are specified. Use the problem_role attribute for '
                                          'this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                if category_check:
                    # If custom table, check the samples
                    if self.graph['problem_formulation']['doe_settings']['doe_method'] == self.OPTIONS_DOE_METHODS[3]:
                        all_samples = []
                        for des_var_node in des_var_nodes:
                            category_check, i_not = check('samples' not in self.nodes[des_var_node],
                                                          'The samples attributes is missing for design variable node'
                                                          ' %s.' % des_var_node,
                                                          status=category_check,
                                                          category='C',
                                                          i=i)
                            if category_check:
                                all_samples.append(self.nodes[des_var_node]['samples'])
                        i += 1
                        sample_lengths = [len(item) for item in all_samples]
                        # Check whether all samples have the same length
                        category_check, i = check(not sample_lengths.count(sample_lengths[0]) == len(sample_lengths),
                                                  'Not all given samples have the same length, this is mandatory.',
                                                  status=category_check,
                                                  category='C',
                                                  i=i)

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def add_function_problem_roles(self, function_order_method='manual'):
        """Method to add the function problem roles (pre-coupled, coupled, post-coupled functions).

        :param function_order_method: algorithm to be used for the order in which the functions are executed.
        :type function_order_method: basestring
        :return: graph with problem roles added to functions
        :rtype: FundamentalProblemGraph

        Algorithm options:

        * 'manual' - function order attributed to the problem formulation of the graph is used
        """

        logger.info('Adding function problem roles...')

        # Input assertions
        assert not self.find_all_nodes(subcategory='all problematic variables'), \
            'Problem roles could not be determined. Graph still has problematic variables.'

        # Determine and check function ordering method
        assert function_order_method in self.OPTIONS_FUNCTION_ORDER_METHOD
        if function_order_method == 'manual':
            assert 'function_order' in self.graph['problem_formulation'], 'function_order must be given as attribute.'
            function_order = self.graph['problem_formulation']['function_order']
        elif function_order_method == 'random':
            raise IOError('Random function ordering method not allowed for adding function problem roles.')

        # Determine the coupling matrix
        coupling_matrix = self.get_coupling_matrix()

        # Determine the different function roles
        # determine non-zero values in the coupling matrix
        non_zeros = np.transpose(np.nonzero(coupling_matrix))
        # remove upper triangle and diagonal elements
        lower_zeros = []
        left_ind = None
        low_ind = None
        for pos in non_zeros:
            if pos[1] < pos[0]:
                lower_zeros.append(pos)
                # Assess left-most feedback coupling node position -> first coupled function
                if left_ind is None:
                    left_ind = pos[1]
                elif pos[1] < left_ind:
                    left_ind = pos[1]
                # Assess lowest feedback coupling node position -> last coupled function
                if low_ind is None:
                    low_ind = pos[0]
                elif pos[0] > low_ind:
                    low_ind = pos[0]

        # Enrich graph function nodes and create dictionary with ordering results
        function_ordering = dict()
        function_ordering[self.FUNCTION_ROLES[0]] = list()
        function_ordering[self.FUNCTION_ROLES[1]] = list()
        function_ordering[self.FUNCTION_ROLES[2]] = list()
        if left_ind is not None:
            for i in range(0, left_ind):
                self.nodes[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[0]
                function_ordering[self.FUNCTION_ROLES[0]].append(function_order[i])
            for i in range(left_ind, low_ind+1):
                self.nodes[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[1]
                function_ordering[self.FUNCTION_ROLES[1]].append(function_order[i])
            if low_ind < len(function_order)-1:
                for i in range(low_ind+1, len(function_order)):
                    self.nodes[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[2]
                    function_ordering[self.FUNCTION_ROLES[2]].append(function_order[i])
        else:
            # noinspection PyUnboundLocalVariable
            for function in function_order:
                self.nodes[function]['problem_role'] = self.FUNCTION_ROLES[0]
                function_ordering[self.FUNCTION_ROLES[0]].append(function)

        # Add function ordering to the graph as well
        self.graph['problem_formulation']['function_ordering'] = function_ordering

        logger.info('Successfully added function problem roles...')

        return

    def add_problem_formulation(self, mdao_definition, function_order, doe_settings=None):
        """Method to add the problem formulation.

        :param mdao_definition: MDF-GS, MDF-J, IDF, CO, BLIS-2000
        :type mdao_definition: str
        :param function_order: order or functions to be included in graph
        :type function_order: list
        :param doe_settings: doe settings of the graph
        :type doe_settings: dict
        :return: graph enriched with problem formulation
        :rtype: Fundamental ProblemGraph
        """

        # Impose the MDAO architecture
        mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

        # Define settings of the problem formulation
        if 'problem_formulation' not in self.graph:
            self.graph['problem_formulation'] = dict()
        self.graph['problem_formulation']['function_order'] = function_order
        self.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
        self.graph['problem_formulation']['convergence_type'] = convergence_type
        self.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

        if doe_settings:
            self.graph['problem_formulation']['doe_settings'] = dict()
            self.graph['problem_formulation']['doe_settings']['doe_method'] = doe_settings['doe_method']
            if 'doe_seed' in doe_settings:
                self.graph['problem_formulation']['doe_settings']['doe_seed'] = doe_settings['doe_seed']
            if 'doe_runs' in doe_settings:
                self.graph['problem_formulation']['doe_settings']['doe_runs'] = doe_settings['doe_runs']

    def partition_graph(self, n_parts, include_run_time=False, tpwgts=None, recursive=True, contig=False):
        """Partition a graph using the Metis algorithm (http://glaros.dtc.umn.edu/gkhome/metis/metis/overview).

        :param n_parts: number of partitions requested (algorithm might provide less)
        :type n_parts: int
        :param include_run_time:
        :type include_run_time: bool
        :param tpwgts: list of target partition weights
        :type tpwgts: list
        :param recursive: option to use the recursive bisection or k-way partitioning algorithm
        :type recursive: bool
        :param contig: Metis option
        :type contig: bool

        .. note:: partitioning can only be performed on undirected graphs. Therefore every graph input is translated
            into an undirected graph.
        """

        import metis

        # Input assertions
        assert 'function_ordering' in self.graph['problem_formulation'], 'Function ordering is missing'
        coupled_nodes = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
        if include_run_time:
            for node in coupled_nodes:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        # Get subgraph
        subgraph = self.get_subgraph_by_function_nodes(coupled_nodes)
        graph = subgraph.deepcopy()
        coupling_dict = graph.get_coupling_dictionary()

        best_solution = {'partitions': dict(), 'variables': float("inf"), 'run_time': float("inf")}
        number_of_iterations_not_improved = 0

        while True:

            # Get undirected graph
            g_und = graph.to_undirected()

            # Add run time to the nodes of the undirected graph
            for node in g_und.nodes():
                if g_und.nodes[node]['category'] == 'variable':
                    g_und.nodes[node]['run_time'] = 0
                elif g_und.nodes[node]['category'] == 'function':
                    g_und.nodes[node]['run_time'] = g_und.nodes[node]['performance_info']['run_time'] if \
                        include_run_time else 1
            g_und.graph['node_weight_attr'] = 'run_time'

            # Partition graph
            (edgecuts, parts) = metis.part_graph(g_und, n_parts, tpwgts=tpwgts, recursive=recursive, contig=contig)

            # Get partition dict
            partitions = dict()
            for part in range(n_parts):
                nodes = []
                # Get function nodes in partition
                for idx, node in enumerate(g_und.nodes):
                    if parts[idx] == part and graph.nodes[node]['category'] == 'function':
                        nodes.extend(node.split('--') if '--' in node else [node])
                # Minimize feedback within the partition
                nodes = self.minimize_feedback(nodes, 'single-swap')
                nodes = self.sort_nodes_for_process(nodes)
                # Add nodes to the partition dict
                partitions[part+1] = nodes

            # Reset graph
            graph = subgraph.deepcopy()

            # Evaluate the properties of the partitioning
            partition_variables, system_variables, runtime = graph.get_partition_info(partitions,
                                                                                      include_run_time=include_run_time)

            # Merge nodes that can be merged based on process and calculate runtime of each partition
            for partition in partitions:
                nodes = list(partitions[partition])
                while nodes:
                    merge_nodes, run_times = [], []
                    for idx, node in enumerate(nodes):
                        if not set(nodes[:idx]).intersection(coupling_dict[node]):
                            merge_nodes.append(node)
                            run_times.append(self.nodes[node]['performance_info']['run_time'] if include_run_time else
                                             1)
                        else:
                            break
                    if len(merge_nodes) > 1:
                        new_node = '--'.join(merge_nodes)
                        try:
                            graph = graph.merge_parallel_functions(merge_nodes, new_label=new_node)
                            graph.nodes[new_node]['performance_info'] = {'run_time': max(run_times)}
                        except AssertionError:
                            pass
                    for node in merge_nodes:
                        nodes.pop(nodes.index(node))

            n_variables = len(system_variables) + sum([len(variables) for variables in partition_variables])

            # Decide whether new solution is better than the best solution found so far
            accept_solution = False
            variable_change = abs((best_solution['variables'] - n_variables)/float(best_solution['variables']))
            run_time_change = abs((best_solution['run_time'] - max(runtime))/float(best_solution['run_time']))
            if n_variables <= best_solution['variables']:
                if max(runtime) < best_solution['run_time']:
                    accept_solution = True
                else:
                    if variable_change*1.5 > run_time_change:
                        accept_solution = True
            elif max(runtime) <= best_solution['run_time']:
                if run_time_change > variable_change*1.5:
                    accept_solution = True

            if accept_solution:
                best_solution = {'partitions': partitions, 'variables': n_variables, 'run_time': max(runtime)}
                number_of_iterations_not_improved = 0
            else:
                number_of_iterations_not_improved += 1

            # Remember current partition
            if accept_solution:
                best_solution['partitions'] = partitions
                best_solution['variables'] = n_variables
                best_solution['runtime'] = max(runtime)

            # If the third iteration does not give an improvement the iterations are stopped
            if number_of_iterations_not_improved > 2:
                break

        return best_solution['partitions']

    def get_partition_info(self, partitions, include_run_time=False):
        """ Function to get the number of feedback variables in the partitions and the number system variables (feedback
        and feedforward variables between partitions)

        :param partitions: dictionary which indicates which nodes are in which partition
        :type partitions: dict
        :param include_run_time:
        :type include_run_time: bool
        :return: partition_variables:
        :rtype: partition_variables: list of sets
        :return: system_variables:
        :rtype: system_variables: set
        """

        # Get complete function order of nodes in the partitions
        function_order = []
        for partition in partitions:
            function_order.extend(partitions[partition])

        # Input assertions
        if include_run_time:
            for node in function_order:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        # Get coupling dictionary
        coupling_dict = self.get_coupling_dictionary()

        # For each node in the partitions check whether its input comes from the same partition, another partition or
        # neither
        partition_variables = [set() for _ in partitions]
        system_variables = set()
        for partition in partitions:
            for idx, target in enumerate(partitions[partition]):
                for source in coupling_dict[target]:
                    if source in partitions[partition][idx+1:]:
                        paths = nx.all_shortest_paths(self, source, target)
                        for path in paths:
                            partition_variables[partition-1].update([path[1].split('/')[-1]])
                    elif source in function_order and source not in partitions[partition]:
                        paths = nx.all_shortest_paths(self, source, target)
                        for path in paths:
                            system_variables.update([path[1].split('/')[-1]])

        # Calculate run time of each partition
        run_time_partitions = []
        for partition in partitions:
            nodes = list(partitions[partition])
            run_time_partition = 0
            while nodes:
                parallel_nodes = []
                run_times = []
                for idx, node in enumerate(nodes):
                    if not set(nodes[:idx]).intersection(coupling_dict[node]):
                        parallel_nodes.append(node)
                        if include_run_time:
                            run_times.append(self.nodes[node]['performance_info']['run_time'])
                        else:
                            run_times.append(1)
                    else:
                        break
                run_time_partition += max(run_times)
                for node in parallel_nodes:
                    nodes.pop(nodes.index(node))
            run_time_partitions.append(run_time_partition)

        return partition_variables, system_variables, run_time_partitions

    def select_number_of_partitions(self, partition_range, include_run_time=False, plot_pareto_front=False):
        """ Function to evaluate the properties of different number of partitions and to select the best one.

        :param partition_range: range of number of partitions that need to be evaluated
        :type partition_range: list
        :param include_run_time:
        :type include_run_time:
        :param plot_pareto_front: Option to plot the characteristics of different number of partitions
        :type plot_pareto_front: bool
        :return:
        """

        # Input assertions
        assert 'function_ordering' in self.graph['problem_formulation'], 'Function ordering is missing'
        coupled_nodes = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
        if include_run_time:
            for node in coupled_nodes:
                assert 'run_time' in self.nodes[node]['performance_info'], 'Run time missing for function ' \
                                                                           '{}'.format(node)

        partition_info = []
        partition_results = dict()

        for idx, n_partitions in enumerate(partition_range):
            # Partition graph
            partitioned_graph = self.deepcopy()
            partitions = partitioned_graph.partition_graph(n_partitions, include_run_time=include_run_time)

            # Evaluate graph
            partition_variables, system_variables, runtime = partitioned_graph.get_partition_info(
                partitions, include_run_time=include_run_time)
            total_var = len(system_variables) + sum([len(variables) for variables in partition_variables])

            # Save partition information
            partition_info.append([idx, n_partitions, [len(variables) for variables in partition_variables],
                                   len(system_variables), total_var, max(runtime)])
            partition_results[n_partitions] = partitions

        # Print partition information in table
        header = ['Option', '# partitions', '# feedback in partitions', '# system variables', 'Total # variables',
                  'Runtime']
        printing.print_in_table(partition_info, headers=header)

        # Show the options in a graph
        if plot_pareto_front:
            from matplotlib.ticker import MaxNLocator
            fig, ax = plt.subplots()
            plt_x, plt_y, txt = [], [], []
            for result in partition_info:
                plt_x.append(result[5])
                plt_y.append(result[4])
                txt.append(str(result[1]))
            ax.scatter(plt_x, plt_y)
            for idx in range(len(plt_x)):
                ax.annotate(txt[idx], (plt_x[idx], plt_y[idx]))
            plt.xlabel('Longest runtime')
            plt.ylabel('# variables to converge')
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.show()

        # Select the number of partitions
        selmsg = 'Please slect number of partitions:'
        sel = prompting.user_prompt_select_options(*partition_range, message=selmsg, allow_empty=False,
                                                   allow_multi=False)
        idx = partition_range.index(int(sel[0]))

        # Get result
        partitions = partition_results[partition_range[idx]]

        return partitions

    def select_distributed_architecture(self):
        """ Function for easy selection of a distributed architecture for a partitioned graph.

        :return: Extended problem formulation
        """

        # Check if graph is partitioned
        assert 'partitions' in self.graph['problem_formulation'], 'Graph is not partitioned. ' \
                                                                  'Distributed architecture is not possible'
        assert len(self.graph['problem_formulation']['partitions']) > 1, 'Graph must have at least two partitions ' \
                                                                         'to select a distributed architecture'

        # Get graph info
        partitions = self.graph['problem_formulation']['partitions']
        coupling_dict = self.get_coupling_dictionary()

        # Select system architecture
        system_architectures = ['unconverged-MDA', 'converged-MDA', 'MDF', 'IDF', 'unconverged-OPT']
        options = []
        for idx, arch in enumerate(system_architectures):
            options.append([idx, arch])
        printing.print_in_table(options, headers=['Option', 'System architecture'])
        msg = 'Please select system architecture:'
        system_architecture = str(prompting.user_prompt_select_options(*system_architectures, allow_empty=False,
                                                                       allow_multi=False, message=msg)[0])

        # Select which partitions need a local converger
        msg = 'Please select which partitions need a local converger:'
        idx_list = range(len(partitions)+1)
        while True:
            local_convergers = prompting.user_prompt_select_options(*idx_list, allow_empty=True, allow_multi=True,
                                                                    message=msg)
            # Partitions start counting at one, so zero is not allowed
            if 0 in local_convergers:
                print 'Partition numbering starts from 1.'
                continue
            # Check if feedback exists in the chosen partitions
            valid_input = True
            for converger in local_convergers:
                feedback = False
                for idx, node in enumerate(partitions[converger]):
                    if set(partitions[converger][idx+1:]).intersection(coupling_dict[node]):
                        feedback = True
                if not feedback:
                    print 'Partition {} does not contain feedback and therefore it cannot have a local ' \
                          'converger'.format(converger)
                    valid_input = False
                    continue
            if not valid_input:
                continue
            break

        # Select which partitions needs to be solved using the Jacobi method instead of Gauss-Seidel
        msg = 'Please select which partitions must be solved using a Jacobi convergence instead of Gauss-Seidel'
        idx_list = range(len(partitions) + 1)
        while True:
            jacobi_convergence = prompting.user_prompt_select_options(*idx_list, allow_empty=True, allow_multi=True,
                                                                      message=msg)
            # Partitions start counting at one, so zero is not allowed
            if 0 in jacobi_convergence:
                print 'Partition numbering starts from 1.'
                continue
            break

        # Select which partitions must be executed in sequence # TODO: add more checks
        msg = 'Please select which partitions must be run in sequence (e.g. [[1, 2], [3, 4]])'
        while True:
            valid_input = True
            sequence_partitions = prompting.user_prompt_string(allow_empty=True, message=msg)
            sequence_partitions = eval(sequence_partitions) if sequence_partitions else []
            sequence_partitions = [sequence_partitions] if not any(isinstance(el, list) for el in sequence_partitions) \
                else sequence_partitions
            if not isinstance(sequence_partitions, list) or not any(isinstance(el, list) for el in sequence_partitions):
                print 'Input should be a list or list of lists'
                valid_input = False
            for sequence in sequence_partitions:
                if 0 in sequence:
                    print 'Partition numbering starts from 1.'
                    valid_input = False
                for element in sequence:
                    if not isinstance(element, int):
                        print 'Invalid input given'
                        valid_input = False
            if not valid_input:
                continue
            break

        print 'local converger:', local_convergers
        print 'system architecture:', system_architecture
        print 'jacobi convergence:', jacobi_convergence
        print 'sequence partitions:', sequence_partitions

        self.graph['problem_formulation']['system_architecture'] = system_architecture
        self.graph['problem_formulation']['local_convergers'] = local_convergers
        self.graph['problem_formulation']['partition_convergence'] = jacobi_convergence
        self.graph['problem_formulation']['sequence_partitions'] = sequence_partitions

        return

    def get_mg_function_ordering(self):
        """Method to determine the function ordering for MDAO graphs (FPG and MDG) based on an FPG.

        :return: function ordering dictionary
        :rtype: dict

        .. note:: Function ordering has to be adjusted when design variables are used. In that case, the pre-coupling
            functions have to be divided in  two parts: the first part does not use the design variables yet, while the
            second does.
        """

        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        pre_functions = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[0]]
        mg_function_ordering = dict(self.graph['problem_formulation']['function_ordering'])
        if mdao_arch == self.OPTIONS_ARCHITECTURES[7]:  # Distributed-conv
            mdao_arch = self.graph['problem_formulation']['system_architecture']

        # OPTIONS_ARCHITECTURE: IDF, MDF, unc-OPT, unc-DOE, con-DOE, CO, BLISS-2000
        if mdao_arch in self.OPTIONS_ARCHITECTURES[2:7]+self.OPTIONS_ARCHITECTURES[8:10]:
            del mg_function_ordering[self.FUNCTION_ROLES[0]]
            if pre_functions:
                target_set = set()
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                for des_var in des_var_nodes:
                    # Find targets
                    des_var_targets = self.get_targets(des_var)
                    target_set.update(des_var_targets)
                post_desvars_idx = len(pre_functions)
                for idx, func in enumerate(pre_functions):
                    # Check if the function is in the target set
                    if func in target_set:
                        post_desvars_idx = idx
                        break
                pre_desvars_funcs = pre_functions[:post_desvars_idx]
                post_desvars_funcs = pre_functions[post_desvars_idx:]
            else:
                pre_desvars_funcs = []
                post_desvars_funcs = []
            mg_function_ordering[self.FUNCTION_ROLES[3]] = pre_desvars_funcs
            mg_function_ordering[self.FUNCTION_ROLES[4]] = post_desvars_funcs
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                mg_function_ordering[self.FUNCTION_ROLES[2]].append(self.CONSCONS_STRING)

        return mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CONVERSION METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #

    def create_mpg(self, mg_function_ordering, name='MPG'):
        """Function to automatically create a MPG based on a FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MPG graph
        :type name: basestring
        :return: unconnected FPG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """

        from graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(kb_path=self.graph.get('kb_path'), name=name,
                               fpg=self, mg_function_ordering=mg_function_ordering)
        mpg.graph['problem_formulation'] = self.graph['problem_formulation']

        return mpg

    def create_mdg(self, mg_function_ordering, name='MDG'):
        """Function to automatically create an MDG based on an FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MDG graph
        :type name: basestring
        :return: baseline MDG (only added additional action blocks, no changed connections)
        :rtype: MdaoDataGraph
        """

        mdg = MdaoDataGraph(self, name=name, mg_function_ordering=mg_function_ordering)

        return mdg

    def determine_scope_design_variables(self, des_vars=None, coupled_functions_groups=None,
                                         pre_coupling_functions=None):
        """Method to determine the scope (global, local) of the design variables and to determine to which coupled
        function groups the design variable belongs.

        :param des_vars: list of design variables (if not given, it is taken from the graph)
        :type des_vars: list
        :param coupled_functions_groups: list with list of coupled function groups
        :type coupled_functions_groups: list
        :param pre_coupling_functions: list with list of pre-coupled function groups
        :type pre_coupling_functions: list
        :return: list of global design variables, list of local design variables, dictionary with dependencies
        :rtype: tuple
        """

        # Start empty lists and dictionary
        global_des_vars = []
        local_des_vars = []
        des_vars_group_idxs = dict()

        # Get and check design variables
        des_vars = self.check_and_get_design_variables(des_vars=des_vars)

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)

        # Get and check pre-coupling functions
        pre_coupling_functions = \
            self.check_and_get_pre_coupling_functions(pre_coupling_functions=pre_coupling_functions)

        # Determine the scope of the design variables
        for des_var in des_vars:
            linked_groups = []
            for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                subgraph = self.get_subgraph_by_function_nodes(pre_coupling_functions + coupled_functions_group)
                for func in coupled_functions_group:
                    if subgraph.has_node(des_var):
                        if nx.has_path(subgraph, des_var, func):
                            linked_groups.append(idx)
                            break
                    else:
                        break
            if len(linked_groups) == 0:
                raise AssertionError(
                    "Design variable {} could not be associated with a coupled function.".format(des_var))
            elif len(linked_groups) == 1:
                local_des_vars.append(des_var)
            else:
                global_des_vars.append(des_var)
            des_vars_group_idxs[des_var] = linked_groups
        return global_des_vars, local_des_vars, des_vars_group_idxs

    def determine_scope_constraint_functions(self, cnstrnt_vars=None, coupled_functions_groups=None,
                                             post_coupling_functions=None):
        """Method to determine the scope (global, local) of the constraint functions based on the constraint variables
        and to determine on which coupled function groups the constraint function depends.

        :param cnstrnt_vars: (optional) constraint variables to be determined
        :type cnstrnt_vars: list
        :param coupled_functions_groups: (optional) list of lists with coupled functions groups
        :type coupled_functions_groups: list
        :param post_coupling_functions: (optional) list with post-coupling functions
        :type post_coupling_functions: list
        :return: global constraint variables and functions, local constraint variables and functions, groups indices
                 per constraint function
        :rtype: tuple
        """

        # Start empty lists and dictionary
        global_cnstrnt_vars = []
        global_cnstrnt_funcs = []
        local_cnstrnt_vars = []
        local_cnstrnt_funcs = []
        cnstrnt_vars_group_idxs = dict()
        cnstrnt_funcs_group_idxs = dict()

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)

        # Get and check post-coupling functions
        post_coupling_functions = \
            self.check_and_get_post_coupling_functions(post_coupling_functions=post_coupling_functions)

        # Associate constraint variables with the constraint functions
        cnstrnt_funcs = dict()
        for cnstrnt_var in cnstrnt_vars:
            cnstrnt_func = self.get_sources(cnstrnt_var)[0]
            if cnstrnt_func not in cnstrnt_funcs:
                cnstrnt_funcs[cnstrnt_func] = [cnstrnt_var]
            else:
                cnstrnt_funcs[cnstrnt_func].append(cnstrnt_var)

        # Determine the scope of the constraint functions
        for cnstrnt_func in cnstrnt_funcs:
            linked_groups = []
            for idx, coupled_functions_group in enumerate(coupled_functions_groups):
                subgraph = self.get_subgraph_by_function_nodes(coupled_functions_group + post_coupling_functions)
                for func in coupled_functions_group:
                    if nx.has_path(subgraph, func, cnstrnt_func):
                        linked_groups.append(idx)
                        break
            if len(linked_groups) == 0:
                raise AssertionError("Constraint function {} could not be associated with a coupled function "
                                     "group.".format(cnstrnt_func))
            elif len(linked_groups) == 1:
                local_cnstrnt_funcs.append(cnstrnt_func)
                local_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
            else:
                global_cnstrnt_funcs.append(cnstrnt_func)
                global_cnstrnt_vars.extend(cnstrnt_funcs[cnstrnt_func])
            for cnstrnt_var in cnstrnt_funcs[cnstrnt_func]:
                cnstrnt_vars_group_idxs[cnstrnt_var] = linked_groups
            cnstrnt_funcs_group_idxs[cnstrnt_func] = linked_groups

        return global_cnstrnt_vars, global_cnstrnt_funcs, local_cnstrnt_vars, local_cnstrnt_funcs, \
               cnstrnt_vars_group_idxs, cnstrnt_funcs_group_idxs

    def get_group_couplings(self, coupled_functions_groups=None):
        """Method to obtain group couplings and their indices.

        :param coupled_functions_groups: (optional) list of coupled function groups
        :type coupled_functions_groups: list
        :returns: group couplings present
        :rtype: list
        :returns: index of coupled groups
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)
        all_coupled_functions = [item for sublist in coupled_functions_groups for item in sublist]

        # Create subgraph of just the coupled functions
        subgraph = self.get_subgraph_by_function_nodes(all_coupled_functions)

        # Merge the functions of each coupled group into one
        for coupled_functions_group in coupled_functions_groups:
            if len(coupled_functions_group) > 1:
                subgraph = subgraph.merge_functions()
        group_couplings = subgraph.find_all_nodes(category='variable', subcategory='all couplings')

        # Determine for each group coupling to which group its determination belongs
        group_couplings_groups_idx = dict()
        for group_coupling in group_couplings:
            source_func = self.get_sources(group_coupling)[0]
            for idx, coupled_function_group in enumerate(coupled_functions_groups):
                if source_func in coupled_function_group:
                    group_couplings_groups_idx[group_coupling] = idx
                    break

        return group_couplings, group_couplings_groups_idx

    def get_sys_post_couplings(self, sys_level_post_coupled, coupled_functions_groups=None):
        """Method to obtain the system-level post-couplings functions.

        :param sys_level_post_coupled: nodes with attributed problem role 'post-coupling'
        :type sys_level_post_coupled: list
        :param coupled_functions_groups: (optional) list of coupled function groups
        :type coupled_functions_groups: list
        :returns: system-level post-coupling functions
        :rtype: list
        :returns: indices ot system-level post-coupling functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Check system-level post-coupling functions
        for fun in sys_level_post_coupled:
            assert self.has_node(fun), 'Node {} is not present in the graph.'.format(fun)
            assert 'problem_role' in self.nodes[fun], 'Node {} does not have a problem_role assigned.'.format(fun)
            assert self.nodes[fun]['problem_role'] == self.FUNCTION_ROLES[2], \
                'Node {} is does not have problem_role {}.'.format(fun, self.FUNCTION_ROLES[2])

        # Get and check coupled function groups
        coupled_functions_groups = \
            self.check_and_get_coupled_functions_groups(coupled_functions_groups=coupled_functions_groups)
        all_coupled_functions = [item for sublist in coupled_functions_groups for item in sublist]

        # Create subgraph of just the coupled and system-level post-coupling functions
        subgraph = self.get_subgraph_by_function_nodes(all_coupled_functions+sys_level_post_coupled)

        # Merge the functions of the coupled groups into one, as well as the system-level post-coupled functions
        if len(coupled_functions_groups) > 1:
            coupled_functions_groups_flat = [item for sublist in coupled_functions_groups for item in sublist]
            subgraph = subgraph.merge_functions(coupled_functions_groups_flat)
        if len(sys_level_post_coupled) > 1:
            subgraph = subgraph.merge_functions(sys_level_post_coupled)
        sys_post_couplings = subgraph.find_all_nodes(category='variable', subcategory='all couplings')

        # Determine for each group coupling to which group its determination belongs
        sys_post_couplings_groups_idx = dict()
        for sys_post_coupling in sys_post_couplings:
            source_func = self.get_sources(sys_post_coupling)[0]
            for idx, coupled_function_group in enumerate(coupled_functions_groups):
                if source_func in coupled_function_group:
                    sys_post_couplings_groups_idx[sys_post_coupling] = idx
                    break

        return sys_post_couplings, sys_post_couplings_groups_idx

    def get_system_level_functions(self, global_objective_function, global_cnstrnt_functions,
                                   mg_function_ordering=None):
        """Method to obtain system level functions

        :param global_objective_function: global objective function
        :type global_objective_function: str
        :param global_cnstrnt_functions: global constraint function(s)
        :type global_cnstrnt_functions: list
        :param mg_function_ordering: MdaoGraph function ordering
        :type mg_function_ordering: dict
        :return: system level functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Initiate dictionary
        global_functions = [global_objective_function] + global_cnstrnt_functions
        system_level_function_dict = dict()
        system_level_function_dict[self.FUNCTION_ROLES[1]] = []
        system_level_function_dict[self.FUNCTION_ROLES[3]] = []
        system_level_function_dict[self.FUNCTION_ROLES[4]] = []
        system_level_function_dict[self.FUNCTION_ROLES[2]] = global_functions

        # Get and check function groups
        if mg_function_ordering is None:
            mg_function_ordering = self.get_mg_function_ordering()
        pre_desvars = mg_function_ordering[self.FUNCTION_ROLES[3]]
        post_desvars = mg_function_ordering[self.FUNCTION_ROLES[4]]
        post_couplings = mg_function_ordering[self.FUNCTION_ROLES[2]]

        # Add pre-design variables functions to the dictionary
        system_level_function_dict[self.FUNCTION_ROLES[3]] = pre_desvars

        # Add post-design variables and post-coupling functions to the dictionary if they have a dependency to one of
        # the global functions
        # Create a subgraph
        subgraph = self.get_subgraph_by_function_nodes(post_desvars + post_couplings)
        # Check each function
        for post_desvar in post_desvars:
            for global_function in global_functions:
                if nx.has_path(subgraph, post_desvar, global_function):
                    system_level_function_dict[self.FUNCTION_ROLES[4]].append()
        additional_post_couplings = []
        for post_coupling in post_couplings:
            if post_coupling not in global_functions:
                for global_function in global_functions:
                    if nx.has_path(subgraph, post_coupling, global_function):
                        additional_post_couplings.append(post_coupling)
        # This operation is done to keep the right order of the functions
        system_level_function_dict[self.FUNCTION_ROLES[2]] = [fun for fun in post_couplings if fun in
                                                              global_functions+additional_post_couplings]
        return system_level_function_dict

    def get_sub_level_functions(self, local_objective_function, local_cnstrnt_funcs, coupled_functions_group,
                                mg_function_ordering=None):
        """Method to obtain subsystem level functions.

        :param local_objective_function: local objective function
        :type local_objective_function: str
        :param local_cnstrnt_funcs: local constraint function(s)
        :type local_cnstrnt_funcs: list
        :param coupled_functions_group: coupled functions
        :type coupled_functions_group: list
        :param mg_function_ordering: (optional) MdaoGraph function ordering
        :type mg_function_ordering: dict
        :return: subsystem level functions
        :rtype: dict
        """
        # TODO: Imco check docstring

        # Initiate dictionary
        local_objective_function_list = [] if local_objective_function is None else [local_objective_function]
        local_functions = local_objective_function_list + local_cnstrnt_funcs
        sub_level_function_dict = dict()
        sub_level_function_dict[self.FUNCTION_ROLES[3]] = []
        sub_level_function_dict[self.FUNCTION_ROLES[4]] = []
        sub_level_function_dict[self.FUNCTION_ROLES[1]] = coupled_functions_group
        sub_level_function_dict[self.FUNCTION_ROLES[2]] = local_functions

        # Get and check function groups
        if mg_function_ordering is None:
            mg_function_ordering = self.get_mg_function_ordering()
        post_desvars = mg_function_ordering[self.FUNCTION_ROLES[4]]
        post_couplings = mg_function_ordering[self.FUNCTION_ROLES[2]]

        # Add post-design variables and post-coupling functions to the dictionary if they have a dependency to one of
        # the global functions
        # Create a subgraph
        subgraph = self.get_subgraph_by_function_nodes(post_desvars + coupled_functions_group + post_couplings)
        # Check each function
        for post_desvar in post_desvars:
            for local_function in local_functions:
                if nx.has_path(subgraph, post_desvar, local_function):
                    sub_level_function_dict[self.FUNCTION_ROLES[4]].append(post_desvar)
        additional_post_couplings = []
        for post_coupling in post_couplings:
            if post_coupling not in local_functions:
                for local_function in local_functions:
                    if nx.has_path(subgraph, post_coupling, local_function):
                        additional_post_couplings.append(post_coupling)
        # This operation is done to keep the right order of the functions
        sub_level_function_dict[self.FUNCTION_ROLES[2]] = [fun for fun in post_couplings if fun in
                                                           local_functions + additional_post_couplings]
        return sub_level_function_dict

    def check_and_get_pre_coupling_functions(self, pre_coupling_functions=None):
        """Method to obtain the pre-coupled functions and check them if provided

        :param pre_coupling_functions: (optional) pre-coupled function nodes
        :type pre_coupling_functions: list
        :return: pre-coupled function nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'pre-coupled'
        """

        if not pre_coupling_functions:
            pre_coupling_functions = self.graph['problem_formulation']['function_ordering']['pre-coupling']
        assert isinstance(pre_coupling_functions, list), \
            'The pre_coupling_functions input should be a list.'
        for pre_coupling_function in pre_coupling_functions:
            assert self.has_node(pre_coupling_function), \
                'Function {} is not a node in the graph.'.format(pre_coupling_function)
            assert 'problem_role' in self.nodes[pre_coupling_function], \
                'Function {} does not have a problem role.'.format(pre_coupling_function)
            assert self.nodes[pre_coupling_function]['problem_role'] == self.FUNCTION_ROLES[0], \
                'Pre-coupled function {} lacks the problem ' \
                'role "{}".'.format(pre_coupling_function, self.FUNCTION_ROLES[0])
        return pre_coupling_functions

    def check_and_get_coupled_functions_groups(self, coupled_functions_groups=None):
        """Method to obtain the coupled functions and check them if provided

        :param coupling_functions_groups: (optional) coupled function groups
        :type coupling_functions_groups: list
        :return: coupled function groups
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'coupled'
        """

        if not coupled_functions_groups:
            coupled_functions_groups = self.graph['problem_formulation']['coupled_functions_groups']
        functions_found = []
        assert coupled_functions_groups > 1, 'There have to be at least two coupled functions groups.'
        for coupled_functions_group in coupled_functions_groups:
            assert isinstance(coupled_functions_group, list), \
                'The elements of the coupled_functions_groups should be lists.'
            for func in coupled_functions_group:
                assert self.has_node(func), 'Function {} is not a node in the graph.'.format(func)
                assert 'problem_role' in self.nodes[func], \
                    'Function {} does not have a problem role.'.format(func)
                assert self.nodes[func]['problem_role'] == self.FUNCTION_ROLES[1], \
                    'Coupled function {} lacks the problem role "{}".'.format(func, self.FUNCTION_ROLES[1])
                assert func not in functions_found, \
                    'Coupled function {} is present multiple times in the coupled_functions_group.'.format(func)
                functions_found.append(func)
        return coupled_functions_groups

    def check_and_get_post_coupling_functions(self, post_coupling_functions=None):
        """Method to obtain the post-coupled functions and check them if provided

        :param post_coupling_functions: (optional) post-coupled function nodes
        :type post_coupling_functions: list
        :return: post-coupled function nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'post-coupled'
        """

        if not post_coupling_functions:
            post_coupling_functions = self.graph['problem_formulation']['function_ordering']['post-coupling']
        assert isinstance(post_coupling_functions, list), \
            'The post_coupling_functions input should be a list.'
        for post_coupling_function in post_coupling_functions:
            assert self.has_node(post_coupling_function), \
                'Function {} is not a node in the graph.'.format(post_coupling_function)
            assert 'problem_role' in self.nodes[post_coupling_function], \
                'Function {} does not have a problem role.'.format(post_coupling_function)
            assert self.nodes[post_coupling_function]['problem_role'] == self.FUNCTION_ROLES[2], \
                'Post-coupled function {} lacks the problem ' \
                'role "{}".'.format(post_coupling_function, self.FUNCTION_ROLES[2])
        return post_coupling_functions

    def check_and_get_design_variables(self, des_vars=None):
        """Method to obtain the design variable nodes and check them if provided

        :param des_vars: (optional) design variable nodes
        :type des_vars: list
        :return: design variable nodes
        :rtype: list

        Checks whether the function is a node of the graph with the problem role 'design variable'
        """
        if des_vars:
            for des_var in des_vars:
                assert self.has_node(des_var), 'Design variable {} is not a node in the graph.'.format(des_var)
                assert 'problem_role' in self.nodes[des_var], \
                    'Design variable {} does not have a problem role.'.format(des_var)
                assert self.nodes[des_var]['problem_role'] == self.PROBLEM_ROLES_VARS[0], \
                    'Design variable {} lacks the problem role "{}".'.format(des_var, self.PROBLEM_ROLES_VARS[0])
        else:
            des_vars = self.find_all_nodes(category='variable',
                                           attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
            assert len(des_vars) > 0, 'No design variables found in the graph.'
        return des_vars

    def _analyze_distributed_system(self, des_var_nodes, objective_node, constraint_nodes, mg_function_ordering):
        """Method to analyze an FPG as a distributed system to asses local and global functions and variables.

        :param des_var_nodes: design variable nodes in the graph
        :type des_var_nodes: list
        :param objective_node: objective node in the graph
        :type objective_node: basestring
        :param constraint_nodes: constraint nodes in the graph
        :type constraint_nodes: list
        :param mg_function_ordering: function ordering of the MDAO graph
        :type mg_function_ordering: dict
        :return: dictionary with the system analysis results
        :rtype: dict
        """

        # Get settings from graph
        coupled_functions_groups = self.graph['problem_formulation']['coupled_functions_groups']

        # Determine coupling variables between coupled_function_groups
        group_couplings, group_couplings_groups_idx = self.get_group_couplings()
        basic_group_couplings = list(group_couplings)

        # Determine objective function based on objective value
        global_objective_function = self.get_sources(objective_node)[0]
        # TODO: Assert that objective function only has one output

        # Determine local and global design variables
        global_des_vars, local_des_vars, des_vars_group_idxs = \
            self.determine_scope_design_variables(des_vars=des_var_nodes)
        # TODO: assess that each discipline group is dependent on at least one design variable (?)

        # Get global and local constraints and their functions
        global_cnstrnt_vars, global_cnstrnt_funcs, local_cnstrnt_vars, local_cnstrnt_funcs, cnstrnt_vars_group_idxs, \
        cnstrnt_funcs_group_idxs = self.determine_scope_constraint_functions(cnstrnt_vars=constraint_nodes)

        # Create dictionary of pre-desvar, post-desvar, and post-coupling functions for the system optimizer
        sys_functions_dict = self.get_system_level_functions(global_objective_function, global_cnstrnt_funcs,
                                                             mg_function_ordering=mg_function_ordering)

        # Determine couplings between coupled groups and system-level post-coupling functions
        add_group_couplings, add_group_couplings_groups_idx = \
            self.get_sys_post_couplings(sys_functions_dict[self.FUNCTION_ROLES[2]])

        # Add additional couplings to the group_couplings
        for add_group_coupling in add_group_couplings:
            if add_group_coupling not in group_couplings:
                group_couplings.append(add_group_coupling)
                group_couplings_groups_idx[add_group_coupling] = add_group_couplings_groups_idx[add_group_coupling]

        # Create dictionaries of post-desvar, coupled, and post-coupling functions per each subgroup
        subsys_functions_dicts = []
        for idx, coupled_functions_group in enumerate(coupled_functions_groups):
            # Get the local constraint functions of the current group
            local_cnstrnt_funcs_group = []
            for cnstrnt_func, groups in cnstrnt_funcs_group_idxs.iteritems():
                if idx in groups:
                    local_cnstrnt_funcs_group.append(cnstrnt_func)
            subsys_functions_dict = self.get_sub_level_functions(None, local_cnstrnt_funcs_group,
                                                                 coupled_functions_group,
                                                                 mg_function_ordering=mg_function_ordering)
            # Create dict collecting the subsystem functions dictionary
            subsys_functions_dicts.append(subsys_functions_dict)

        return {'des_vars': {'global': global_des_vars, 'local': local_des_vars, 'groups': des_vars_group_idxs},
                'objective': {'global_fun': global_objective_function},
                'constraints': {'global_vars': global_cnstrnt_vars, 'local_vars': local_cnstrnt_vars,
                                'global_funs': global_cnstrnt_funcs, 'local_funs': local_cnstrnt_funcs,
                                'groups_vars': cnstrnt_vars_group_idxs, 'groups_funs': cnstrnt_funcs_group_idxs},
                'couplings': {'basic': basic_group_couplings, 'extended': group_couplings,
                              'groups': group_couplings_groups_idx},
                'functions_dicts': [sys_functions_dict, subsys_functions_dicts]}

    def get_objective_node(self):
        """Method to get the single (or non-existent) objective node from a graph.

        :return: objective node or None if no objective node is present
        :rtype: str, None
        """
        objective_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
        assert len(objective_nodes) <= 1, 'Multiple objective nodes found: {}'.format(objective_nodes)
        if objective_nodes:
            return objective_nodes[0]
        else:
            return None

    def get_mdg(self, name='MDG'):
        """Create the MDAO data graph for a given FPG.

        :param name: name of the new graph
        :type name: basestring
        :return: MDAO data graph
        :rtype: MdaoDataGraph
        """

        # Start-up checks
        logger.info('Composing MDG...')
        assert isinstance(name, basestring)
        self.add_function_problem_roles()
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        graph = self.deepcopy()

        # Load variables from FPG
        mdao_arch = graph.graph['problem_formulation']['mdao_architecture']
        conv_type = graph.graph['problem_formulation']['convergence_type']
        if 'allow_unconverged_couplings' in graph.graph['problem_formulation']:
            allow_unconverged_couplings = graph.graph['problem_formulation']['allow_unconverged_couplings']
        else:
            allow_unconverged_couplings = False

        # Determine special variables and functions
        des_var_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[0]])
        constraint_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[2]])
        objective_node = graph.get_objective_node()
        qoi_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[3]])

        # Get the function ordering for the FPG and assign coupling function lists accordingly.
        mg_function_ordering = graph.get_mg_function_ordering()
        coup_functions = mg_function_ordering[graph.FUNCTION_ROLES[1]]

        # Set up MDAO data graph
        mdg = graph.create_mdg(mg_function_ordering, name=name)

        # Manipulate data graph
        if mdao_arch == graph.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, True)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[2]:  # IDF
            opt = graph.OPTIMIZER_STRING
            # Connect optimizer as a converger using the consistency constraint function
            mdg.connect_converger(opt, graph.OPTIONS_ARCHITECTURES[2], coup_functions, True)
            # Connect optimizer w.r.t. design variables, objective, contraints
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[3]:  # MDF
            opt = graph.OPTIMIZER_STRING
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, True)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = graph.OPTIMIZER_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=True)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=True)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = graph.DOE_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = graph.DOE_STRING
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == self.OPTIONS_ARCHITECTURES[7]:  # distributed-convergence

            # Input checks
            assert 'partitions' in graph.graph['problem_formulation'], 'Graph is not partitioned.'
            assert 'system_architecture' in graph.graph['problem_formulation'], 'No architecture selected for ' \
                                                                                'distributed convergence.'

            # Load extra variables from fpg
            partitions = graph.graph['problem_formulation']['partitions']
            system_arch = graph.graph['problem_formulation']['system_architecture']
            local_convergers = graph.graph['problem_formulation']['local_convergers']
            parallel_conv = graph.graph['problem_formulation']['partition_convergence']

            if system_arch == 'converged-MDA' or system_arch == 'MDF':
                system_conv = graph.CONVERGER_STRING
                # Connect partitions
                for partition in partitions:
                    local_conv = graph.CONVERGER_STRING + str(partition)
                    # Get convergence type of partitions (default is Gauss-Seidel, unless indicated otherwise)
                    conv_type_partition = graph.OPTIONS_CONVERGERS[0] if partition in parallel_conv else \
                        graph.OPTIONS_CONVERGERS[1]
                    # Connect disciplines to local converger if present, otherwise system converger
                    converger = local_conv if partition in local_convergers else system_conv
                    mdg.connect_converger(converger, conv_type_partition, partitions[partition], True)
                # Connect remaining couplings to system converger
                mdg.connect_converger(system_conv, graph.OPTIONS_CONVERGERS[0], coup_functions, True,
                                      system_converger=True)
                # Connect optimizer if present
                if system_arch == 'MDF':
                    opt = graph.OPTIMIZER_STRING
                    # noinspection PyUnboundLocalVariable
                    mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
                # Connect qoi
                mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
                # Connect coordinator
                mdg.connect_coordinator()
            elif system_arch == 'IDF':
                opt = graph.OPTIMIZER_STRING
                # Connect partitions
                for partition in partitions:
                    local_conv = graph.CONVERGER_STRING + str(partition)
                    converger = local_conv if partition in local_convergers else opt
                    # Get convergence type for the partition
                    if partition in parallel_conv:
                        if converger == opt:
                            conv_type_partition = graph.OPTIONS_ARCHITECTURES[2]
                        else:
                            conv_type_partition = graph.OPTIONS_CONVERGERS[0]
                    else:
                        conv_type_partition = graph.OPTIONS_CONVERGERS[1]
                    mdg.connect_converger(converger, conv_type_partition, partitions[partition], True)
                # Connect remaining couplings to optimer as system converger
                mdg.connect_converger(opt, graph.OPTIONS_ARCHITECTURES[2], coup_functions, True, system_converger=True)
                # Connect optimizer
                # noinspection PyUnboundLocalVariable
                mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
                # Connect qoi
                mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
                # Connect coordinator
                mdg.connect_coordinator()
            elif system_arch == 'unconverged-MDA' or system_arch == 'unconverged-OPT':
                # Connect partitions
                for partition in partitions:
                    local_conv = graph.CONVERGER_STRING + str(partition)
                    # Get convergence type of partitions (default is Gauss-Seidel, unless indicated otherwise)
                    conv_type_partition = graph.OPTIONS_CONVERGERS[0] if partition in parallel_conv else \
                        graph.OPTIONS_CONVERGERS[1]
                    # Connect disciplines to local converger if present
                    if partition in local_convergers:
                        mdg.connect_converger(local_conv, conv_type_partition, partitions[partition], True)
                    else:
                        if conv_type_partition == graph.OPTIONS_CONVERGERS[1]:
                            mdg.manipulate_coupling_nodes(partitions[partition], remove_feedback=True,
                                                          remove_feedforward=False, converger=None,
                                                          include_couplings_as_final_output=False)
                        else:
                            mdg.manipulate_coupling_nodes(partitions[partition], remove_feedback=True,
                                                          remove_feedforward=True, converger=None,
                                                          include_couplings_as_final_output=False)
                # Connect remaining couplings
                mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                              converger=None, include_couplings_as_final_output=False,
                                              system_converger=True)
                # Connect optimizer if present
                if system_arch == 'unconverged-OPT':
                    opt = graph.OPTIMIZER_STRING
                    # noinspection PyUnboundLocalVariable
                    mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
                # Connect qoi
                mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
                # Connect coordinator
                mdg.connect_coordinator()

            # Resolve problematic variables
            prob_var = mdg.find_all_nodes(subcategory='all splittable variables')
            for var in prob_var:
                sources = mdg.get_sources(var)
                targets = mdg.get_targets(var)
                function_order = []
                for converger in local_convergers:
                    if self.CONVERGER_STRING + str(converger) in sources:
                        function_order.extend([self.CONVERGER_STRING + str(converger)])
                        function_order.extend([target for target in targets if target in partitions[converger]])
                if self.CONVERGER_STRING in sources:
                    function_order.extend([self.CONVERGER_STRING])
                    function_order.extend([target for target in targets if target not in function_order])
                if self.OPTIMIZER_STRING in sources:
                    function_order.extend([self.OPTIMIZER_STRING])
                    function_order.extend([target for target in targets if target not in function_order])
                mdg.split_variables(var, function_order=function_order)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[8]:  # CO
            coupled_functions_groups = graph.graph['problem_formulation']['coupled_functions_groups']
            n_groups = len(coupled_functions_groups)
            sys_opt, sub_opts = self.get_architecture_node_ids('CO', number_of_groups=n_groups)
            sys_opt_label, sub_opts_labels = self.get_architecture_node_labels('CO', number_of_groups=n_groups)

            sa = self._analyze_distributed_system(des_var_nodes, objective_node, constraint_nodes, mg_function_ordering)

            # TODO: Assert that function instances are not required (future functionality)
            # TODO: Determine the functions requiring instances, add them and adjust subsys_functions_dict accordingly
            # sys_functions_dict, subsys_functions_dicts = graph.create_function_instances(sys_functions_dict,
            #                                                                              subsys_functions_dicts)

            # Keep track of the design variables and constraints for the system level
            sys_lev_des_vars = set(sa['des_vars']['global'])
            sys_lev_cnstrnts = set(sa['constraints']['global_vars'])

            # For each discipline group, localize the group, add the consistency objective function and add the
            # sub-optimizer
            for idx, subsys_functions_dict in enumerate(sa['functions_dicts'][1]):
                # Get global and local design nodes and local constraint nodes involved in the group
                subsys_functions = [item for sublist in subsys_functions_dict.values() for item in sublist]
                global_des_vars_group, local_des_vars_group, local_cnstrnt_vars_group, local_group_couplings_group, \
                external_group_couplings_group = get_group_vars(sa, idx)

                # Make the groups local by introducing the right copies
                local_des_vars_copies_group, global_des_vars_copies_group, mapping_des_vars = \
                    mdg.localize_design_variables(subsys_functions, global_des_vars_group, local_des_vars_group)
                sys_lev_des_vars.update(global_des_vars_copies_group)

                external_group_couplings_copies_group, local_group_couplings_copies_group, \
                mapping_locals= mdg.localize_group_couplings(subsys_functions,
                                                             external_group_couplings_group,
                                                             local_group_couplings_group)
                sys_lev_des_vars.update(external_group_couplings_copies_group+local_group_couplings_copies_group)

                # Add the consistency objective function according to CO2
                cof_mappings = mapping_des_vars.copy()
                cof_mappings.update(mapping_locals)
                group_cof_node, group_cof_obj_node = mdg.connect_consistency_objective_function(idx, cof_mappings)
                sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[2]].append(group_cof_node)

                # TODO: Then (optionally) add a converger or check for the removal of feedback?
                # if feedback inside the coupled group
                # mdg.connect_converger()

                # Add and connect the sub-level optimizer
                mdg.connect_optimizer(sub_opts[idx],
                                      local_des_vars_group+local_des_vars_copies_group,
                                      group_cof_obj_node,
                                      local_cnstrnt_vars_group,
                                      label=sub_opts_labels[idx])
                # Mark the final consistency objective value as a constraint and add it to the system level constraints
                group_cof_obj_node_final = mdg.find_all_nodes(attr_cond=['related_to_schema_node', '==',
                                                                         group_cof_obj_node])
                assert len(group_cof_obj_node_final) == 1, 'One final value for the consistency objective value is' \
                                                           ' expected, found: {}.'.format(group_cof_obj_node_final)
                mdg.mark_as_constraint(group_cof_obj_node_final[0], '==', 0.0)
                sys_lev_cnstrnts.update([group_cof_obj_node_final[0]])

            # Connect the system-level optimizer
            mdg.connect_optimizer(sys_opt,
                                  list(sys_lev_des_vars),
                                  objective_node,
                                  list(sys_lev_cnstrnts),
                                  label=sys_opt_label)

            # TODO: Clean up some of the system outputs

            # Finally, connect the coordinator
            mdg.connect_coordinator()

            # Write function_ordering to the graph
            mdg.graph['distr_function_ordering'] = sa['functions_dicts']

        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[9]:  # BLISS-2000
            coupled_functions_groups = graph.graph['problem_formulation']['coupled_functions_groups']
            n_groups = len(coupled_functions_groups)
            sys_opt, sys_conv, sys_sms, sub_smbds, sub_does, sub_opts, sub_smbs = \
                self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sys_opt_label, sys_conv_label, sys_sms_labels, sub_smbds_labels, sub_does_labels, sub_opts_labels, \
            sub_smbs_labels = self.get_architecture_node_labels(mdao_arch, number_of_groups=n_groups)

            sa = self._analyze_distributed_system(des_var_nodes, objective_node, constraint_nodes, mg_function_ordering)

            # TODO: Assert that function instances are not required (future functionality)
            # TODO: Determine the functions requiring instances, add them, and adjust subsys_functions_dict accordingly
            # sys_functions_dict, subsys_functions_dicts = graph.create_function_instances(sys_functions_dict,
            #                                                                              subsys_functions_dicts)

            # Keep track of the design variables and constraints for the system level
            sys_lev_des_vars = set(sa['des_vars']['global'])
            sys_lev_cnstrnts = set(sa['constraints']['global_vars'])

            # For each discipline group, localize the group, add the consistency objective function and add the
            # sub-optimizer
            prev_local_group_couplings_copies = []
            sms_outs = []
            sms_ins = []
            weight_nodes2 = []
            sm_inps_lists = []
            sa['functions_dicts'][0][self.FUNCTION_ROLES[1]].extend(sys_sms)
            for idx, subsys_functions_dict in enumerate(sa['functions_dicts'][1]):
                # Get global and local design nodes and local constraint nodes involved in the group
                subsys_functions = [item for sublist in subsys_functions_dict.values() for item in sublist]
                global_des_vars_group, local_des_vars_group, local_cnstrnt_vars_group, local_group_couplings_group, \
                external_group_couplings_group = get_group_vars(sa, idx)

                # Make the groups local by introducing the right copies
                local_des_vars_copies_group, global_des_vars_copies_group, mapping_des_vars = \
                    mdg.localize_design_variables(subsys_functions, global_des_vars_group, local_des_vars_group)

                external_group_couplings_copies_group, local_group_couplings_copies_group, \
                mapping_locals = mdg.localize_group_couplings(subsys_functions, external_group_couplings_group +
                                                              prev_local_group_couplings_copies,
                                                              local_group_couplings_group, instances_for_externals=True)

                # Add the weighted couplings objective function according to BLISS-2000
                group_wcf_node, group_wcf_obj_node, weight_nodes = \
                    mdg.connect_weighted_couplings_objective_function(idx, local_group_couplings_group)
                sa['functions_dicts'][1][idx][mdg.FUNCTION_ROLES[2]].append(group_wcf_node)

                # Add and connect the sub-level optimizer
                fin_des_vars, _, _, _ = mdg.connect_optimizer(sub_opts[idx], local_des_vars_group, group_wcf_obj_node,
                                                              local_cnstrnt_vars_group, label=sub_opts_labels[idx])

                # Add local coupling nodes as final output in the graph
                lgcg_finals = []
                for node in local_group_couplings_group:
                    lgcg_final = mdg.copy_node_as(node,
                                                  mdg.ARCHITECTURE_ROLES_VARS[5],  # final output variables
                                                  add_instance_if_exists=True)
                    lgcg_finals.append(lgcg_final)
                    source = mdg.get_sources(node)[0]
                    mdg.add_edge(source, lgcg_final)

                # Add and connect the sub-level DOE
                doe_inps, doe_outs = mdg.connect_doe_block(sub_does[idx],
                                                           external_group_couplings_copies_group +
                                                           local_des_vars_copies_group+weight_nodes,
                                                           lgcg_finals+fin_des_vars)

                # Add and connect the surrogate model boundary determinator
                mdg.connect_boundary_determinator(sub_smbds[idx], [], doe_inps, label=sub_smbds_labels[idx])

                # Add and connect the surrogate model builder
                sm_def_node = mdg.connect_surrogate_model_builder(sub_smbs[idx], doe_inps, doe_outs,
                                                                  label=sub_smbs_labels[idx])

                # Add and connect the surrogate model itself
                sm_inps = []
                for weight_node in weight_nodes:
                    weight_node2 = mdg.add_instance(weight_node)
                    sm_inps.append(weight_node2)
                    mdg.mark_as_design_variable(weight_node2, lower_bound=-2.0, nominal_value=0.0, upper_bound=2.0,
                                                ignore_outdegree=True)
                    weight_nodes2.append(weight_node2)
                for node in external_group_couplings_copies_group:
                    # Check for hole node for instance = 1, otherwise add instance
                    original_node = mdg.get_first_node_instance(node)
                    if mdg.in_degree(original_node) == 0:
                        node2 = original_node
                    else:
                        node2 = mdg.add_instance(node)
                    sm_inps.append(node2)
                    mdg.mark_as_design_variable(node2, ignore_outdegree=True)
                sm_inps.extend(global_des_vars_group)
                sm_out_originals = [mdg.nodes[node]['related_to_schema_node'] for node in lgcg_finals+fin_des_vars]
                sm_outs = mdg.connect_surrogate_model(sys_sms[idx], sm_def_node, sm_inps, sm_out_originals,
                                                      label=sys_sms_labels[idx])
                sm_inps_lists.append(sm_inps)
                sms_ins.extend(sm_inps)
                sms_outs.extend(sm_outs)

                # List to keep track of earlier created local group couplings copies
                prev_local_group_couplings_copies.extend(local_group_couplings_copies_group)

            # Connect the surrogate model outputs to the system-level post-coupling functions
            sms_outs_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_outs]
            for func in sa['functions_dicts'][0][self.FUNCTION_ROLES[2]]:
                sources = mdg.get_sources(func)
                for source in sources:
                    if 'related_to_schema_node' in mdg.nodes[source]:
                        rel_node = mdg.nodes[source]['related_to_schema_node']
                        if rel_node in sms_outs_related:
                            sm_node = sms_outs[sms_outs_related.index(rel_node)]
                            # Reconnect the source to the SM node
                            assert mdg.in_degree(source) == 0, 'This node is supposed to be an input.'
                            mdg.remove_edge(source, func)
                            mdg.add_edge(sm_node, func)

            # Create and connect the consistency constraint function
            sms_outs_couplings = [node for node in sms_outs if mdg.nodes[node]['related_to_schema_node'] in
                                  sa['couplings']['basic']]
            sms_outs_couplings_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_outs_couplings]
            sms_ins2 = [node for node in sms_ins if 'related_to_schema_node' in mdg.nodes[node]]
            sms_ins_couplings = [node for node in sms_ins2 if mdg.nodes[node]['related_to_schema_node'] in
                                 sa['couplings']['basic']]
            sms_ins_couplings_related = [mdg.nodes[node]['related_to_schema_node'] for node in sms_ins_couplings]
            ccf_mapping = dict()
            for sms_out, sms_out_related in zip(sms_outs_couplings, sms_outs_couplings_related):
                if sms_out_related in sms_ins_couplings_related:
                    map_node = sms_ins_couplings[sms_ins_couplings_related.index(sms_out_related)]
                    ccf_mapping[sms_out] = map_node
                else:
                    raise NotImplementedError('Could not find the right map node somehow...')
            ccf_node, cc_nodes = mdg.connect_consistency_constraint_function(ccf_mapping)
            sa['functions_dicts'][0][self.FUNCTION_ROLES[2]].append(ccf_node)

            # Connect the system-level optimizer
            fin_des_vars, _, _, ini_guess_nodes = mdg.connect_optimizer(sys_opt,
                                                                        list(sys_lev_des_vars)+weight_nodes2 +
                                                                        ccf_mapping.values(),
                                                                        objective_node, list(sys_lev_cnstrnts)+cc_nodes,
                                                                        label=sys_opt_label)

            # Connect converger check
            fin_sys_lev_des_vars = [node for node in fin_des_vars if
                                    mdg.nodes[node]['related_to_schema_node'] in sys_lev_des_vars]
            ini_guess_nodes_filt = [node for node in ini_guess_nodes if
                                    mdg.nodes[node]['related_to_schema_node'] in sys_lev_des_vars]
            mdg.connect_convergence_check(sys_conv, fin_sys_lev_des_vars+ini_guess_nodes_filt, label=sys_conv_label)

            # Connect the initial guesses and final values to the surrogate model boundary determinator
            ini_guess_nodes_related = [mdg.nodes[node]['related_to_schema_node'] for node in ini_guess_nodes]
            fin_val_nodes_related = [mdg.nodes[node]['related_to_schema_node'] for node in fin_des_vars]
            for idx, smbo in enumerate(sub_smbds):
                smbo_sources = sm_inps_lists[idx]
                for smbo_source in smbo_sources:
                    # First the initial guesses
                    if 'related_to_schema_node' in mdg.nodes[smbo_source]:
                        if mdg.nodes[smbo_source]['related_to_schema_node'] in ini_guess_nodes_related:
                            ini_inp = ini_guess_nodes[ini_guess_nodes_related.index(mdg.nodes[smbo_source]
                                                                                    ['related_to_schema_node'])]
                        else:
                            raise NotImplementedError('Could not find related node.')
                    else:
                        ini_inp = ini_guess_nodes[ini_guess_nodes_related.index(smbo_source)]
                    assert ini_inp, 'Could not find the right node.'
                    mdg.add_edge(ini_inp, smbo)

                    # Then the final values
                    if 'related_to_schema_node' in mdg.nodes[smbo_source]:
                        if mdg.nodes[smbo_source]['related_to_schema_node'] in fin_val_nodes_related:
                            fin_inp = fin_des_vars[fin_val_nodes_related.index(mdg.nodes[smbo_source]
                                                                               ['related_to_schema_node'])]
                        else:
                            raise NotImplementedError('Could not find related node.')
                    else:
                        fin_inp = fin_des_vars[fin_val_nodes_related.index(smbo_source)]
                    assert fin_inp, 'Could not find the right node.'
                    mdg.add_edge(fin_inp, smbo)

            # Finally, connect the coordinator
            mdg.connect_coordinator(additional_inputs=fin_sys_lev_des_vars)

            # Remove hole variable nodes
            holes = mdg.find_all_nodes(category='variable', subcategory='hole')
            for hole in holes:
                mdg.remove_node(hole)

            # Write function_ordering to the graph
            mdg.graph['distr_function_ordering'] = sa['functions_dicts']

        logger.info('Composed MDG.')

        return mdg

    def impose_mdao_architecture(self):
        """Method to directly get both the MDG and MPG of an FPG.

        :return: MdaoDataGraph and MdaoProcessGraph
        :rtype: tuple
        """
        mdg = self.get_mdg()
        mpg = mdg.get_mpg()
        return mdg, mpg


class MdaoDataGraph(DataGraph, MdaoMixin):

    def __init__(self, *args, **kwargs):
        super(MdaoDataGraph, self).__init__(*args, **kwargs)
        if 'mg_function_ordering' in kwargs:
            mg_function_ordering = kwargs['mg_function_ordering']
            self._add_action_blocks_and_roles(mg_function_ordering)
            self.graph['function_ordering'] = mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(MdaoDataGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in var_nodes:
            category_check, i_not = check(self.in_degree(node) == 0,
                                          'The node %s has in-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
            category_check, i_not = check(self.out_degree(node) == 0,
                                          'The node %s has out-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i+1)
        i += 1
        category_check, i = check(not self.has_node(self.COORDINATOR_STRING),
                                  'The %s node is missing in the graph.' % self.COORDINATOR_STRING,
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in func_nodes:
            category_check, i_not = check('architecture_role' not in self.nodes[node],
                                          'The architecture_role attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_workflow_problem_def(self):

        # Create workflow/problemDefinitionUID
        cmdows_workflow_problem_def = Element('problemDefinitionUID')
        cmdows_workflow_problem_def.text = (str(self.graph['problem_formulation'].get('mdao_architecture')) +
                                            str(self.graph['problem_formulation'].get('convergence_type')))

        return cmdows_workflow_problem_def

    def _create_cmdows_architecture_elements(self):

        # Create architectureElement
        cmdows_architecture_elements = Element('architectureElements')

        # Create architectureElements/parameters
        cmdows_parameters = cmdows_architecture_elements.add('parameters')
        # Create architectureElements/parameters/instances
        # noinspection PyUnusedLocal
        cmdows_instances = cmdows_parameters.add('instances')
        # TODO: Implement this
        # Create architectureElements/parameters/...
        for architecture_roles_var in self.ARCHITECTURE_ROLES_VARS:
            cmdows_parameter = cmdows_parameters.add(make_camel_case(architecture_roles_var, make_plural_option=True))
            graph_parameter_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_var])
            for graph_parameter_node in graph_parameter_nodes:
                cmdows_parameter_node = cmdows_parameter.add(make_camel_case(architecture_roles_var))
                cmdows_parameter_node.set('uID', graph_parameter_node)
                instance = int(self.nodes[graph_parameter_node].get('instance'))
                if instance > 1:
                    cmdows_parameter_node.add('relatedInstanceUID',
                                              self.get_first_node_instance(self.nodes[graph_parameter_node]))
                else:
                    cmdows_parameter_node.add('relatedParameterUID',
                                              self.nodes[graph_parameter_node].get('related_to_schema_node'))
                cmdows_parameter_node.add('label',
                                          self.nodes[graph_parameter_node].get('label'))
                cmdows_parameter_node.add('instanceID', instance)
        # Create architectureElements/executableBlocks
        cmdows_executable_blocks = cmdows_architecture_elements.add('executableBlocks')
        # Create architectureElements/executableBlocks/...
        for architecture_roles_fun in self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER:
            graph_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_fun])
            cmdows_executable_block = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                                   make_plural_option=True))
            # Create architectureElements/executableBlocks/.../...
            for graph_node in graph_nodes:

                cmdows_executable_block_elem = cmdows_executable_block.add(make_camel_case(architecture_roles_fun))
                cmdows_executable_block_elem.set('uID', graph_node)
                cmdows_executable_block_elem.add('label', self.nodes[graph_node].get('label'))

                if architecture_roles_fun == 'optimizer':
                    cmdows_executable_block_elem.add('settings', self.nodes[graph_node].get('settings'),
                                                     camel_case_conversion=True)
                    graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0] + var} for var in
                                      self.nodes[graph_node].get('design_variables')]
                    cmdows_executable_block_elem.add('designVariables', graph_des_vars)
                    graph_obj_vars = [{'objectiveVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[1] + var} for var in
                                      self.nodes[graph_node].get('objective_variable')]
                    cmdows_executable_block_elem.add('objectiveVariables', graph_obj_vars)
                    graph_con_vars = [{'constraintVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[2] + var} for var in
                                      self.nodes[graph_node].get('constraint_variables')]
                    cmdows_executable_block_elem.add('constraintVariables', graph_con_vars)

                elif architecture_roles_fun == 'doe':
                    graph_settings = self.nodes[graph_node].get('settings')
                    if graph_settings is not None:
                        cmdows_settings = cmdows_executable_block_elem.add('settings')
                        cmdows_settings.add('doeMethod', graph_settings.get('doe_method'))
                        if graph_settings.get('doe_runs') is not None:
                            cmdows_settings.add('doeRuns', graph_settings.get('doe_runs'))
                        if graph_settings.get('doe_seed') is not None:
                            cmdows_settings.add('doeSeed', graph_settings.get('doe_seed'))
                        if graph_settings.get('doe_table') is not None:  # TODO: Temp fix, doe should have settings
                            cmdows_table = cmdows_settings.add('doeTable')
                            for graph_row_index, graph_row in enumerate(graph_settings.get('doe_table_order')):
                                cmdows_row = cmdows_table.add('tableRow',
                                                              attrib={'relatedParameterUID': str(graph_row)})
                                for graph_element_index, graph_element in enumerate(graph_settings.get('doe_table')):
                                    cmdows_row.add('tableElement', str(format(float(graph_element[graph_row_index]),
                                                                              '.12f')),
                                                   attrib={'experimentID': str(graph_element_index)})
                        graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0] + var} for var in
                                          self.nodes[graph_node].get('design_variables')]
                        cmdows_executable_block_elem.add('designVariables', graph_des_vars)
                else:
                    cmdows_executable_block_elem.add('settings', self.nodes[graph_node].get('settings'),
                                                     camel_case_conversion=True)

        # Create architectureElements/executableBlocks/...Analyses/...
        architecture_roles_funs = np.setdiff1d(self.ARCHITECTURE_ROLES_FUNS, self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER,
                                               assume_unique=True)
        for architecture_roles_fun in architecture_roles_funs:
            nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', str(architecture_roles_fun)])
            cmdows_analyses = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                           make_plural_option=True))
            for node in nodes:
                cmdows_analysis = cmdows_analyses.add(make_camel_case(architecture_roles_fun))
                cmdows_analysis.add('relatedExecutableBlockUID', node)

        return cmdows_architecture_elements

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_architecture_elements(self, cmdows):

        # Create architecture element nodes
        cmdows_architecture_parameters = cmdows.find('architectureElements/parameters')
        if cmdows_architecture_parameters is not None:
            for cmdows_architecture_parameter in list(cmdows_architecture_parameters):
                for cmdows_single_architecture_parameter in list(cmdows_architecture_parameter):
                    cmdows_uid = cmdows_single_architecture_parameter.get('uID')
                    attrb = cmdows.finddict(cmdows_single_architecture_parameter, ordered=False,
                                            camel_case_conversion=True)
                    attrb = translate_dict_keys(attrb, {'related_parameter_u_i_d': 'related_to_schema_node',
                                                        'instance_id': 'instance'})
                    self.add_node(cmdows_uid,
                                  attr_dict=attrb,
                                  category='variable',
                                  architecture_role=unmake_camel_case(cmdows_single_architecture_parameter.tag, ' '))
        cmdows_architecture_exe_blocks = cmdows.find('architectureElements/executableBlocks')
        for cmdows_architecture_exe_block in list(cmdows_architecture_exe_blocks):
            for cmdows_single_architecture_exe_block in list(cmdows_architecture_exe_block):
                cmdows_uid = cmdows_single_architecture_exe_block.get('uID')

                if cmdows_uid is not None:
                    role = unmake_camel_case(cmdows_single_architecture_exe_block.tag, ' ')
                    self.add_node(cmdows_uid,
                                  category='function',
                                  architecture_role=role,
                                  label=cmdows_single_architecture_exe_block.findasttext('label'),
                                  settings=cmdows_single_architecture_exe_block.findasttext('settings'))
                    if role == 'optimizer' or role == 'doe':
                        cmdows_des_vars = cmdows_single_architecture_exe_block.findall('designVariables/designVariable')
                        graph_des_vars = [var.findtext('designVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['design_variables'] = graph_des_vars
                    if role == 'converger' or role == 'optimizer':
                        if 'settings' not in self.nodes[cmdows_uid] or self.nodes[cmdows_uid]['settings'] is None:
                            self.nodes[cmdows_uid]['settings'] = {}
                        if role == 'converger':
                            setting_options = {'last_iterations_to_consider': 'lastIterationsToConsider',
                                               'maximum_iterations': 'maximumIterations',
                                               'convergence_tolerance_relative': 'convergenceToleranceRelative',
                                               'convergence_tolerance_absolute': 'convergenceToleranceAbsolute'}
                        else:
                            setting_options = {'maximum_iterations': 'maximumIterations',
                                               'algorithm': 'algorithm',
                                               'apply_scaling': 'applyScaling',
                                               'maximum_function_evaluations': 'maximumFunctionEvaluations',
                                               'constraint_tolerance': 'constraintTolerance',
                                               'convergence_tolerance': 'convergenceTolerance'}
                        for setting_option in setting_options:
                            if setting_option == 'apply_scaling':
                                bool_options = {'true': True, 'false': False}
                                self.nodes[cmdows_uid]['settings'][setting_option] = \
                                    bool_options[cmdows_single_architecture_exe_block.findtext('settings/' +
                                                                                               setting_options
                                                                                               [setting_option])]
                            else:
                                self.nodes[cmdows_uid]['settings'][setting_option] = \
                                    cmdows_single_architecture_exe_block.findtext('settings/' +
                                                                                  setting_options[setting_option])
                    if role == 'optimizer':
                        cmdows_des_vars = \
                            cmdows_single_architecture_exe_block.findall('objectiveVariables/objectiveVariable')
                        graph_des_vars = [var.findtext('objectiveVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['objective_variable'] = graph_des_vars
                        cmdows_des_vars = \
                            cmdows_single_architecture_exe_block.findall('constraintVariables/constraintVariable')
                        graph_des_vars = [var.findtext('constraintVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.nodes[cmdows_uid]['constraint_variables'] = graph_des_vars
                    elif role == 'doe':
                        cmdows_rows = list(cmdows_single_architecture_exe_block.findall('settings/doeTable/tableRow'))
                        graph_rows = [cmdows_row.get('relatedParameterUID') for cmdows_row in cmdows_rows]
                        graph_table = []
                        for cmdows_row in cmdows_rows:
                            def get_experiment_id(elem):
                                return float(elem.get('experimentID'))
                            elements = sorted(cmdows_row, key=get_experiment_id)
                            entry = []
                            for element in elements:
                                entry.append(format(element.findasttext(), '.12f'))
                            graph_table.append(entry)
                        graph_table = map(list, zip(*graph_table))
                        if 'settings' not in self.nodes[cmdows_uid] or self.nodes[cmdows_uid]['settings'] is None:
                            self.nodes[cmdows_uid]['settings'] = {}
                        self.nodes[cmdows_uid]['settings']['doe_table_order'] = graph_rows
                        self.nodes[cmdows_uid]['settings']['doe_table'] = graph_table
                        self.nodes[cmdows_uid]['settings']['doe_method'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/doeMethod')
                        self.nodes[cmdows_uid]['settings']['doe_runs'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/doeRuns')
                        self.nodes[cmdows_uid]['settings']['doe_seed'] = \
                            cmdows_single_architecture_exe_block.findtext('settings/doeSeed')

                else:
                    for role in self.ARCHITECTURE_ROLES_FUNS:
                        cmdows_role_name = make_camel_case(role)
                        if cmdows_single_architecture_exe_block.tag == cmdows_role_name:
                            cmdows_uid = cmdows_single_architecture_exe_block.find('relatedExecutableBlockUID').text
                            self.nodes[cmdows_uid]['architecture_role'] = role

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _add_action_blocks_and_roles(self, mg_function_ordering):
        """Method to add function blocks to the MDG based on the FPG function ordering

        :param mg_function_ordering: ordered list of functions to be added
        :type mg_function_ordering: list
        """

        # Set input settings
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        local_convergers = []
        if mdao_arch == 'distributed-convergence':
            mdao_arch = self.graph['problem_formulation']['system_architecture']
            local_convergers = self.graph['problem_formulation']['local_convergers']

        # Add coordinator node
        assert not self.has_node(self.COORDINATOR_STRING), 'Coordinator name already in use in FPG.'
        self.add_node(self.COORDINATOR_STRING,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[0],
                      shape='8',
                      label=self.COORDINATOR_LABEL,
                      level=None)

        # No optimizer present
        if self.FUNCTION_ROLES[0] in mg_function_ordering:
            functions = mg_function_ordering[self.FUNCTION_ROLES[0]]
            for func in functions:
                self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[4]

        # Optimizer / DOE present
        if self.FUNCTION_ROLES[3] in mg_function_ordering:
            # Add pre-optimizer functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[3]]
            for func in functions:
                self.nodes[func]['architecture_role'] = 'pre-iterator analysis'
            # Add optimizer / DOE
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unc-OPT
                assert not self.has_node(self.OPTIMIZER_STRING), 'Optimizer name already in use in FPG.'
                self.add_node(self.OPTIMIZER_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[1],
                              shape='8',
                              label=self.OPTIMIZER_LABEL,
                              settings={'algorithm': 'Dakota Quasi-Newton method',
                                        'maximum_iterations': 1000,
                                        'maximum_function_evaluations': 1000,
                                        'constraint_tolerance': 1e-4,
                                        'convergence_tolerance': 1e-4,
                                        'apply_scaling': True})
            elif mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                assert not self.has_node(self.DOE_STRING), 'DOE name already in use in FPG.'
                self.add_node(self.DOE_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[3],  # doe
                              shape='8',
                              label=self.DOE_LABEL,
                              settings=self.graph['problem_formulation']['doe_settings'])
            # Add architecture role to post-iterator functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[4]]
            for func in functions:
                self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]

        # Converger required
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[1]] + [self.OPTIONS_ARCHITECTURES[3]] + \
                [self.OPTIONS_ARCHITECTURES[6]]:  # con-MDA, MDF, con-DOE
            # Add converger
            assert not self.has_node(self.CONVERGER_STRING), 'Converger name already in use in FPG.'
            self.add_node(self.CONVERGER_STRING,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[2],
                          shape='8',
                          label=self.CONVERGER_LABEL,
                          settings={'convergence_tolerance_absolute': 1e-6, 'convergence_tolerance_relative': 1e-6,
                                    'last_iterations_to_consider': 1, 'maximum_iterations': 100})

        # Add local convergers if needed
        if local_convergers:
            for converger in local_convergers:
                assert not self.has_node(self.CONVERGER_STRING + str(converger)), 'Converger name already in use in FPG.'
                self.add_node(self.CONVERGER_STRING + str(converger),
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[2],
                              shape='8',
                              label=self.CONVERGER_LABEL + str(converger),
                              settings={'tolerance_absolute': 1e-6, 'tolerance_relative': 1e-6,
                                        'last_iterations_to_consider': 1, 'maximum_iterations': 100})

        # Add architecture role to coupled functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[1]]:
            self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[7]

        # Add post-coupling functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[2]]:
            if func != self.CONSCONS_STRING:
                self.nodes[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[8]
            else:
                assert not self.has_node(self.CONSCONS_STRING), 'Consistency constraint name already in use in FPG.'
                self.add_node(self.CONSCONS_STRING,
                              label=self.CONSCONS_LABEL,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[8],
                              function_type='consistency')

        return

    def copy_node_as(self, node, architecture_role, add_instance_if_exists=False, ignore_duplicates=True):
        """Method to copy a given node for an architecture role.

        :param node: node to be copied
        :type node: str
        :param architecture_role: architecture role of the copied node
        :type architecture_role: basestring
        :param add_instance_if_exists: option to create another instance if copy already exists
        :type add_instance_if_exists: bool
        :param ignore_duplicates: option to ignore if the creation of an existing node is attempted
        :type ignore_duplicates: bool
        :return: modified node
        """

        assert self.has_node(node), "Node %s is not present in the graph." % node
        assert architecture_role in self.ARCHITECTURE_ROLES_VARS, "Invalid architecture role %s specified." % \
                                                                  architecture_role
        xpath_nodes = node.split('/')
        root = xpath_nodes[1]
        if architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:-1]) + '/gc_' + xpath_nodes[-1]
            # TODO: This needs to be fixed, now used to make RCE WF work for IDF (g_y1) instead of (y1)
        else:
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:])
        if architecture_role == self.ARCHITECTURE_ROLES_VARS[0]:  # initial guess coupling variable
            label_prefix = ''
            label_suffix = '^{c0}'
        elif architecture_role in [self.ARCHITECTURE_ROLES_VARS[1],
                                   self.ARCHITECTURE_ROLES_VARS[5]]:  # final coupling/output variable
            label_prefix = ''
            label_suffix = '^{*}'
        elif architecture_role in [self.ARCHITECTURE_ROLES_VARS[2],
                                   self.ARCHITECTURE_ROLES_VARS[9]]:  # coupling / design copy variable
            label_prefix = ''
            label_suffix = '^{c}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[3]:  # initial guess design variable
            label_prefix = ''
            label_suffix = '^{0}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[4]:  # final design variable
            label_prefix = ''
            label_suffix = '^{*}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            label_prefix = 'gc_'
            label_suffix = ''
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[7]:  # doe input samples
            label_prefix = 'DOE_'
            label_suffix = '_{inp}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[8]:  # doe output samples
            label_prefix = 'DOE_'
            label_suffix = '_{out}'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[10]:  # SM approximate
            label_prefix = ''
            label_suffix = '^{a}'
        else:
            raise IOError('Label extension could not be found.')

        node_data_dict = dict(self.nodes[node])

        # Determine the related schema node
        if 'related_to_schema_node' in node_data_dict:
            related_schema_node = node_data_dict['related_to_schema_node']
        else:
            related_schema_node = node

        if not self.has_node(new_node):
            self.add_node(new_node,
                          category=node_data_dict['category'],
                          related_to_schema_node=related_schema_node,
                          architecture_role=architecture_role,
                          label=label_prefix+get_correctly_extended_latex_label(node_data_dict['label'], label_suffix),
                          instance=1)
        elif self.has_node(new_node):
            if not ignore_duplicates:
                raise AssertionError('Node {} that is created as copy already exists in the graph.'.format(new_node))
            elif add_instance_if_exists:
                highest_instance = self.get_highest_instance(new_node)
                self.copy_node_with_suffix(new_node, self.INSTANCE_SUFFIX + str(highest_instance+1),
                                           '^{i' + str(highest_instance+1) + '}',
                                           instance=highest_instance+1, related_to_schema_node=node)
                new_node = new_node + self.INSTANCE_SUFFIX + str(highest_instance+1)
        return new_node

    def connect_qoi_nodes_as_input(self, nodes, function, override_with_final_outputs):
        """Method to connect a list of qoi nodes as input to a given function node.

        :param nodes: list of nodes to be connected as input
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: basestring
        :param override_with_final_outputs: setting on whether to override the use of final outputs
        :type override_with_final_outputs: bool
        """

        for node in nodes:
            assert self.has_node(node)
            # Check if there is a final output node as well and use that one instead.
            if override_with_final_outputs:
                schema_related_nodes = self.find_all_nodes(category='variable',
                                                           attr_cond=['related_to_schema_node', '==', node])
                for schema_related_node in schema_related_nodes:
                    if 'architecture_role' in self.nodes[schema_related_node]:
                        if self.nodes[schema_related_node]['architecture_role'] in \
                                get_list_entries(self.ARCHITECTURE_ROLES_VARS, 1, 4, 5):
                            node = schema_related_node
            self.add_edge(node, function)

        return

    def connect_consistency_objective_function(self, group_idx, ccv_mappings):
        """Method to add a consistency objective function. A consistency objective function between related values
        y_1, y_1^c, y_2 and y_2^c would be: (y_1 - y_1^c)^2 + (y_2 - y_2^c)^2

        :param group_idx: index of the subgroup
        :type group_idx: int
        :param ccv_mappings: mapping between original inputs and copies to be made consistent.
        :type ccv_mappings: dict
        :return: the new function node and its output objective value
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = self.COF_STRING + str(group_idx) + self.COF_SUFFIX
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_node(new_function_node,
                      category='function',
                      label=self.COF_LABEL + str(group_idx),
                      instance=1,
                      problem_role=self.FUNCTION_ROLES[2],  # post-coupling
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[4],  # post-coupling analysis
                      function_type='consistency')
        # Connect the variable inputs for the function
        for idx, (var1, var2) in enumerate(ccv_mappings.iteritems()):
            eq_lab1 = 'x{}_0'.format(idx)
            eq_lab2 = 'x{}_1'.format(idx)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            if idx == 0:
                math_expression = '({}-{})**2'.format(eq_lab2, eq_lab1)
            else:
                math_expression += '+({}-{})**2'.format(eq_lab2, eq_lab1)
        # Create the output objective node of the function and connect it
        new_obj_node = '/{}/distributedArchitectures/group{}/objective'.format(self.get_schema_root_name(var1),
                                                                               group_idx)
        self.add_node(new_obj_node,
                      category='variable',
                      label='J'+str(group_idx),
                      instance=1,
                      problem_role=self.PROBLEM_ROLES_VARS[1])  # objective
        self.add_edge(new_function_node, new_obj_node)
        self.add_equation((new_function_node, new_obj_node), math_expression, 'Python')
        return new_function_node, new_obj_node

    def connect_weighted_couplings_objective_function(self, group_idx, couplings):
        """Method to add a weighted couplings objective function. A consistency objective function between related
         weights and couplings w_1, y_1, w_2, y_2 would be: w_1*y_1 + w_2*y_2

        :param group_idx: index of the subgroup
        :type group_idx: int
        :param couplings: couplings to be weighted
        :type couplings: list
        :return: new function node, objective output value and weight nodes
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = self.WCF_STRING + str(group_idx) + self.WCF_SUFFIX
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_node(new_function_node,
                      category='function',
                      label=self.WCF_LABEL + str(group_idx),
                      instance=1,
                      problem_role=self.FUNCTION_ROLES[2],  # post-coupling
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[8],  # post-coupling analysis
                      function_type='regular')
        weight_nodes = []
        # Connect the variable inputs for the function
        for idx, var1 in enumerate(couplings):
            # Add a weight coefficient for each coupling
            xpath_var1 = var1.split('/')
            root = xpath_var1[1]
            var2 = '/{}/distributedArchitectures/group{}/couplingWeights/w{}'.format(root, group_idx, idx)
            self.add_node(var2,
                          category='variable',
                          label=var2.split('/')[-1] + '_' + var1.split('/')[-1],
                          instance=1,
                          architecture_role=self.ARCHITECTURE_ROLES_VARS[11])
            weight_nodes.append(var2)
            eq_lab1 = 'y{}'.format(idx)
            eq_lab2 = 'w{}'.format(idx)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            if idx == 0:
                math_expression = '{}*{}'.format(eq_lab2, eq_lab1)
            else:
                math_expression += '+{}*{}'.format(eq_lab2, eq_lab1)
        # Create the output objective node of the function and connect it
        new_obj_node = '/{}/distributedArchitectures/group{}/objective'.format(root, group_idx)
        self.add_node(new_obj_node,
                      category='variable',
                      label='wcf'+str(group_idx),
                      instance=1,
                      problem_role=self.PROBLEM_ROLES_VARS[1])  # objective
        self.add_edge(new_function_node, new_obj_node)
        self.add_equation((new_function_node, new_obj_node), math_expression, 'Python')
        return new_function_node, new_obj_node, weight_nodes

    def connect_consistency_constraint_function(self, ccv_mappings):
        """Method to add a consistency constraint function to an MDG.

        :param ccv_mappings: mapping between nodes that should be made consistent
        :type ccv_mappings: dict
        :return: new function node and constraint output nodes
        :rtype: tuple
        """

        # Add the consistency constraint objective function (as generic function node, since it will be made as a
        # mathematical function)
        new_function_node = '{}{}'.format(self.CONSCONS_STRING, self.CONSCONS_SUFFIX)
        assert not self.has_node(new_function_node), \
            'The automatically generated function {} somehow already exists.'.format(new_function_node)
        self.add_node(new_function_node,
                      category='function',
                      label=self.CONSCONS_LABEL,
                      instance=1,
                      problem_role=self.FUNCTION_ROLES[2],  # post-coupling
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[8],  # post-coupling analysis
                      function_type='consistency')
        # Connect the variable inputs for the function
        new_con_nodes = []
        for idx, (var1, var2) in enumerate(ccv_mappings.iteritems()):
            eq_lab1 = 'y{}_0'.format(idx)
            eq_lab2 = 'y{}_1'.format(idx)
            self.add_edge(var1, new_function_node, equation_label=eq_lab1)
            self.add_edge(var2, new_function_node, equation_label=eq_lab2)
            math_expression = '{}-{}'.format(eq_lab2, eq_lab1)
            # Create the output objective node of the function and connect it
            xpath_var1 = var1.split('/')
            root = xpath_var1[1]
            new_con_node = '/{}/mdo_data/systemLevel/consistencyConstraints/gc{}'.format(root, idx)
            self.add_node(new_con_node,
                          category='variable',
                          label='gc{}'.format(idx),
                          instance=1,
                          problem_role=self.PROBLEM_ROLES_VARS[2])  # constraint
            self.mark_as_constraint(new_con_node, '==', 0.0)
            self.add_edge(new_function_node, new_con_node)
            self.add_equation((new_function_node, new_con_node), math_expression, 'Python')
            new_con_nodes.append(new_con_node)
        return new_function_node, new_con_nodes

    def localize_design_variables(self, group_functions, global_des_vars, local_des_vars):
        """Method for distributed architecture to create instances of local and global design variables with respect to
        the subgroup.

        :param group_functions: functions that are part of the current group
        :type group_functions: list
        :param global_des_vars: global design variables of the system
        :type global_des_vars: list
        :param local_des_vars: local design variables used in the group
        :type local_des_vars: list
        :return: created copies of the design variables and their mapping
        :rtype: tuple
        """

        # Start with empty lists
        local_des_var_copies = []
        global_des_var_copies = []
        mapping = dict()
        # The global design variables get copies at the local level and are connected accordingly
        for global_des_var in global_des_vars:
            # Find the functions for which the design variable is input
            targets = self.get_targets(global_des_var)
            local_targets = [target for target in targets if target in group_functions]

            # Create a local copy of the design variable
            local_des_var_copy = self.copy_node_as(global_des_var,
                                                   self.ARCHITECTURE_ROLES_VARS[9],  # copy design variable
                                                   add_instance_if_exists=True)
            local_des_var_copies.append(local_des_var_copy)
            mapping[global_des_var] = local_des_var_copy

            for target in local_targets:
                # Remove the connection between the global design variable and the target
                self.remove_edge(global_des_var, target)

                # Connect the local copy to the targets
                self.add_edge(local_des_var_copy, target)
        # The local design variables get copies at the global level and are connected accordingly
        for local_des_var in local_des_vars:
            # Find the functions outside the local level for which the design variable is input
            targets = self.get_targets(local_des_var)
            external_targets = [target for target in targets if target not in group_functions]

            # Create a global copy of the design variable
            if external_targets:
                global_des_var_copy = self.copy_node_as(local_des_var,
                                                        self.ARCHITECTURE_ROLES_VARS[9],  # copy design variable
                                                        add_instance_if_exists=False)
                global_des_var_copies.append(global_des_var_copy)
                mapping[local_des_var] = global_des_var_copy

            for target in external_targets:
                # Remove the connection between the local design variable and the external target
                self.remove_edge(local_des_var, target)

                # Connect the global copy to the targets
                self.add_edge(global_des_var_copy, target)

        return local_des_var_copies, global_des_var_copies, mapping

    def localize_group_couplings(self, group_functions, external_couplings, local_couplings,
                                 instances_for_externals=False):
        """Method for distributed architecture to create instances of local and global coupling variables with respect
        to the subgroup.

        :param group_functions: functions that are part of the current group
        :type group_functions: list
        :param external_couplings: external couplings w.r.t. the current group
        :type external_couplings: list
        :param local_couplings: local coupling w.r.t. the current group
        :type local_couplings: list
        :param instances_for_externals: setting whether additional instances should be created for external couplings
        :type instances_for_externals: bool
        :return: created copies of the couplings and their mapping
        :rtype: tuple
        """

        # Start with empty lists
        external_couplings_copies = []
        local_couplings_copies = []
        mapping_locals = dict()
        # The external couplings should be handled with a copy at the local level
        for external_coupling in external_couplings:
            # Find the functions for which the coupling variable is input
            targets = self.get_targets(external_coupling)
            local_targets = [target for target in targets if target in group_functions]

            if local_targets:
                # Create a local copy of the external coupling
                related_node = external_coupling
                if 'architecture_role' in self.nodes[external_coupling]:
                    if self.nodes[external_coupling]['architecture_role'] == self.ARCHITECTURE_ROLES_VARS[2]:
                        related_node = self.nodes[external_coupling]['related_to_schema_node']
                external_coupling_copy = self.copy_node_as(related_node,
                                                           self.ARCHITECTURE_ROLES_VARS[2],    # coupling copy variable
                                                           add_instance_if_exists=instances_for_externals)
                external_couplings_copies.append(external_coupling_copy)

            for target in local_targets:
                # Remove the connection between the global coupling variable and the target
                self.remove_edge(external_coupling, target)

                # Connect the local copy to the targets
                self.add_edge(external_coupling_copy, target)
        # Local couplings should only be handled by the functions inside the group, outside, they are handled by copies
        for local_coupling in local_couplings:
            # Find the external functions for which the coupling variable is input
            targets = self.get_targets(local_coupling)
            external_targets = [target for target in targets if target not in group_functions]

            # Create a global copy of the internal coupling (if it does not exist in the graph yet)
            if external_targets:
                local_coupling_copy = self.copy_node_as(local_coupling,
                                                        self.ARCHITECTURE_ROLES_VARS[2],  # coupling copy variable
                                                        add_instance_if_exists=False)
                local_couplings_copies.append(local_coupling_copy)
                mapping_locals[local_coupling] = local_coupling_copy
            else:
                # Assess that the local_coupling_copy already exists (but has been disconnected to targets already)
                # and add its mapping.
                xpath_nodes = local_coupling.split('/')
                root = self.get_schema_root_name(local_coupling)
                local_coupling_copy = '/{}/architectureNodes/{}s/{}Copy/{}'\
                    .format(root, make_camel_case(self.ARCHITECTURE_ROLES_VARS[2]), root, '/'.join(xpath_nodes[2:]))
                self.assert_node_exists(local_coupling_copy)
                mapping_locals[local_coupling] = local_coupling_copy

            for target in external_targets:
                # Remove the connection between the local coupling variable and the target
                self.remove_edge(local_coupling, target)

                # Connect the local copy to the targets
                self.add_edge(local_coupling_copy, target)

        return external_couplings_copies, local_couplings_copies, mapping_locals

    def connect_nodes_as_output(self, nodes, function):
        """Method to connect a list of nodes as output to a function node.

        :param nodes: list of nodes to be connected as output
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: basestring
        """

        for node in nodes:
            assert self.has_node(node)
            self.add_edge(function, node)

        return

    def connect_coordinator(self, additional_inputs=[], additional_outputs=[]):
        """Method to automatically connect all system inputs and outputs of a graph to the coordinator node."""

        # Get system inputs and outputs
        input_nodes = self.find_all_nodes(subcategory='all inputs')
        output_nodes = self.find_all_nodes(subcategory='all outputs')

        # Connect the nodes to the coordinator
        for input_node in input_nodes+additional_outputs:
            self.add_edge(self.COORDINATOR_STRING, input_node)
        for output_node in output_nodes+additional_inputs:
            self.add_edge(output_node, self.COORDINATOR_STRING)

        return

    def connect_convergence_check(self, converger, inputs, label='SYS-CONV'):
        """Method to add a convergence check in the MDG.

        :param converger: node ID of the converger block
        :type converger: basestring
        :param inputs: input nodes to be connected for convergence check
        :type inputs: list
        :param label: label for the converger block
        :type label: basestring
        :return: the convergence check node
        :rtype: basestring
        """

        # Input assertions
        # Add converger block if it's not there
        if not self.has_node(converger):
            self.add_node(converger,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[2],
                          label=label,
                          instance=1)
        assert isinstance(inputs, list)
        self.assert_node_exists(inputs)

        # Connect the converger block
        for input in inputs:
            self.add_edge(input, converger)

        # Add convergence check output
        conv_check_node = '/{}/mdoData/systemConvergenceCheck'.format(self.get_schema_root_name(input))
        self.assert_node_exists_not(conv_check_node)
        self.add_node(conv_check_node, category='variable', instance=1, label='conv_check')
        self.add_edge(converger, conv_check_node)

        return conv_check_node

    def connect_converger(self, converger, conv_type, coupling_functions, include_couplings_as_final_output,
                          system_converger=False, label='CONV'):
        """Method to automatically connect a converger around a collection of coupled functions.

        :param converger: name of the converger to be connected
        :type converger: basestring
        :param conv_type: setting for the type of convergence (Jacobi, Gauss-Seidel)
        :type conv_type: basestring
        :param coupling_functions: list of coupled functions
        :type coupling_functions: list
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        :param system_converger: converger is a system converger
        :type system_converger: bool
        :param label: converger label
        :type label: str
        """

        # Input assertions
        # Add converger block if it's not there
        if not self.has_node(converger):
            self.add_node(converger,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[2],
                          label=label,
                          instance=1,
                          settings={'convergence_tolerance_absolute': 1e-6, 'convergence_tolerance_relative': 1e-6,
                                    'last_iterations_to_consider': 1, 'maximum_iterations': 100})
        assert conv_type in self.OPTIONS_CONVERGERS + [self.OPTIONS_ARCHITECTURES[2]], \
            'Invalid converger type %s specified.' % conv_type
        assert isinstance(coupling_functions, list)
        for coupling_function in coupling_functions:
            assert self.has_node(coupling_function), 'Missing coupling function %s in the graph.' % coupling_function

        # Manipulate the coupling variables based on the architecture
        if conv_type == self.OPTIONS_CONVERGERS[0]:  # Jacobi
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)
        elif conv_type == self.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=False,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)
        elif conv_type == self.OPTIONS_ARCHITECTURES[2]:  # IDF
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output,
                                           system_converger=system_converger)

        return

    def connect_optimizer(self, optimizer, design_variable_nodes, objective_node, constraint_nodes, label='OPT'):
        """Method to automatically connect an optimizer w.r.t. the design variables, objective, and constraints.

        :param optimizer: name of the optimizer to be connected
        :type optimizer: basestring
        :type design_variable_nodes: list
        :param objective_node: node used as objective by the optimizer
        :type objective_node: basestring
        :param constraint_nodes: list of constraint nodes
        :type constraint_nodes: list
        :param label: optimizer label
        :type label: str
        :return: enriched MDAO data graph with connected optimizer
        :rtype: MdaoDataGraph
        """

        # Input assertions
        # Add optimizer block if it's not there
        if not self.has_node(optimizer):
            self.add_node(optimizer,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[1],
                          label=label,
                          instance=1,
                          settings={'algorithm': 'Dakota Quasi-Newton method',
                                    'maximum_iterations': 1000,
                                    'maximum_function_evaluations': 1000,
                                    'constraint_tolerance': 1e-4,
                                    'convergence_tolerance': 1e-4,
                                    'apply_scaling': True})
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(objective_node, basestring)
        assert self.has_node(objective_node), 'Objective node %s is missing in the graph.' % objective_node
        assert isinstance(constraint_nodes, list)
        for con_var in constraint_nodes:
            assert self.has_node(con_var), 'Constraint variable %s is missing in the graph.' % con_var

        # Add attributes to the optimizer block
        self.nodes[optimizer]['design_variables'] = dict()
        for des_var in design_variable_nodes:
            self.nodes[optimizer]['design_variables'][des_var] = dict()
            if 'upper_bound' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['upper_bound'] = self.nodes[des_var]['upper_bound']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['upper_bound'] = None
            if 'lower_bound' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['lower_bound'] = self.nodes[des_var]['lower_bound']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['lower_bound'] = None
            if 'nominal_value' in self.nodes[des_var]:
                self.nodes[optimizer]['design_variables'][des_var]['nominal_value'] = \
                    self.nodes[des_var]['nominal_value']
            else:
                self.nodes[optimizer]['design_variables'][des_var]['nominal_value'] = None
        self.nodes[optimizer]['objective_variable'] = [objective_node]
        self.nodes[optimizer]['constraint_variables'] = dict()
        for con_var in constraint_nodes:
            self.nodes[optimizer]['constraint_variables'][con_var] = dict()
            if 'upper_bound' in self.nodes[con_var]:
                self.nodes[optimizer]['constraint_variables'][con_var]['upper_bound'] = \
                    self.nodes[con_var]['upper_bound']
            else:
                self.nodes[optimizer]['constraint_variables'][con_var]['upper_bound'] = None
            if 'lower_bound' in self.nodes[con_var]:
                self.nodes[optimizer]['constraint_variables'][con_var]['lower_bound'] = \
                    self.nodes[con_var]['lower_bound']
            else:
                self.nodes[optimizer]['constraint_variables'][con_var]['lower_bound'] = None

        # Manipulate the graph based on the architecture
        # Connect design variables to the optimizer
        pre_opt_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        fin_des_vars = []
        ini_guess_nodes = []
        for des_var in design_variable_nodes:
            # Create initial guess design variable
            ini_guess_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[3])
            ini_guess_nodes.append(ini_guess_node)
            # If des_var comes from pre-des-var function, then reconnect (remove previous connection, connect to guess)
            des_var_sources = self.get_sources(des_var)
            if des_var_sources:
                pre_des_var_func = list(set(des_var_sources).intersection(pre_opt_funcs))[0]
                if pre_des_var_func:
                    self.remove_edge(pre_des_var_func, des_var)
                    self.add_edge(pre_des_var_func, ini_guess_node)
            # Connect initial guess design variable to optimizer
            self.add_edge(ini_guess_node, optimizer)
            # Connect design variable as output from optimizer
            self.add_edge(optimizer, des_var)
            # Create final design variable
            fin_value_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[4])
            fin_des_vars.append(fin_value_node)
            # Connect final design variable as output from optimizer
            self.add_edge(optimizer, fin_value_node)
        # Connect objective and constraint nodes to the optimizer
        fin_obj = None
        fin_cnstrnts = []
        for var in [objective_node] + constraint_nodes:
            # Connect regular variable version to optimizer
            self.add_edge(var, optimizer)
            # Create a final value copy and connect it as output of the associated functions
            fin_value_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[5])
            if fin_obj is not None:
                fin_cnstrnts.append(fin_value_node)
            fin_obj = fin_value_node
            self.copy_edge([self.get_sources(var)[0], var], [self.get_sources(var)[0], fin_value_node])
        # If the graph contains consistency constraint variables, then connect these to the optimizer as well
        consconcs_nodes = self.find_all_nodes(category='variable',
                                              attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_VARS[6]])
        # Add consistency constraints as constraints in the graph
        for node in consconcs_nodes:
            rel_node = self.nodes[node]['related_to_schema_node']
            # Add design variables to optimizer attributes
            self.nodes[optimizer]['design_variables'][rel_node] = dict()
            if 'upper_bound' in self.nodes[rel_node]:
                self.nodes[optimizer]['design_variables'][rel_node]['upper_bound'] = self.nodes[rel_node]['upper_bound']
            else:
                self.nodes[optimizer]['design_variables'][rel_node]['upper_bound'] = None
            if 'lower_bound' in self.nodes[rel_node]:
                self.nodes[optimizer]['design_variables'][rel_node]['lower_bound'] = self.nodes[rel_node]['lower_bound']
            else:
                self.nodes[optimizer]['design_variables'][rel_node]['lower_bound'] = None
            self.add_edge(node, optimizer)

        return fin_des_vars, fin_obj, fin_cnstrnts, ini_guess_nodes

    def connect_doe_block(self, doe_block, design_variable_nodes, qoi_nodes, label='DOE'):
        """Method to automatically connect an doe_block w.r.t. the design variables, objective, and constraints.

        :param doe_block: name of the doe_block to be connected
        :type doe_block: basestring
        :param design_variable_nodes: list of design variables
        :type design_variable_nodes: list
        :param qoi_nodes: list of constraint nodes
        :type qoi_nodes: list
        :return: enriched MDAO data graph with connected doe_block
        :rtype: MdaoDataGraph
        """

        # Input assertions
        # Add DOE block if it's not there
        if not self.has_node(doe_block):
            self.add_node(doe_block,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[3],
                          label=label,
                          instance=1,
                          settings=self.graph['problem_formulation']['doe_settings'])
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(qoi_nodes, list)
        for qoi_var in qoi_nodes:
            assert self.has_node(qoi_var), 'Q.O.I. variable %s is missing in the graph.' % qoi_var

        # Add attributes to the doe block
        self.nodes[doe_block]['design_variables'] = dict()
        for des_var in design_variable_nodes:
            self.nodes[doe_block]['design_variables'][des_var] = dict()
            if 'upper_bound' in self.nodes[des_var]:
                self.nodes[doe_block]['design_variables'][des_var]['upper_bound'] = self.nodes[des_var]['upper_bound']
            else:
                self.nodes[doe_block]['design_variables'][des_var]['upper_bound'] = None
            if 'lower_bound' in self.nodes[des_var]:
                self.nodes[doe_block]['design_variables'][des_var]['lower_bound'] = self.nodes[des_var]['lower_bound']
            else:
                self.nodes[doe_block]['design_variables'][des_var]['lower_bound'] = None
            if 'nominal_value' in self.nodes[des_var]:
                self.nodes[doe_block]['design_variables'][des_var]['nominal_value'] = self.nodes[des_var][
                    'nominal_value']
            else:
                self.nodes[doe_block]['design_variables'][des_var]['nominal_value'] = None
            if 'samples' in self.nodes[des_var]:
                self.nodes[doe_block]['design_variables'][des_var]['samples'] = self.nodes[des_var]['samples']
            else:
                self.nodes[doe_block]['design_variables'][des_var]['samples'] = None
        self.nodes[doe_block]['quantities_of_interest'] = qoi_nodes

        # For the custom design table, add the table with values to the settings
        if 'doe_settings' in self.graph['problem_formulation']:
            if 'doe_method' in self.graph['problem_formulation']['doe_settings']:
                if self.graph['problem_formulation']['doe_settings']['doe_method'] == 'Custom design table':
                    n_samples = len(self.nodes[doe_block]['design_variables'][design_variable_nodes[-1]]['samples'])
                    doe_table = []
                    for idj in range(n_samples):
                        doe_table.append([])
                        for des_var in design_variable_nodes:
                            doe_table[idj].append(self.nodes[des_var]['samples'][idj])
                    self.graph['problem_formulation']['doe_settings']['doe_table'] = doe_table
                    self.graph['problem_formulation']['doe_settings']['doe_table_order'] = design_variable_nodes

        # Manipulate the graph based on the architecture
        # Connect design variables to the doe_block
        pre_doe_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        inps = []
        for des_var in design_variable_nodes:
            # Create DOE input samples
            doe_input_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[7])
            inps.append(doe_input_node)
            # If des_var comes from pre-des-var function then remove this connection (DOE uses separate list of samples)
            des_var_sources = self.get_sources(des_var)
            pre_des_var_funcs = list(set(des_var_sources).intersection(pre_doe_funcs))
            if pre_des_var_funcs:
                pre_des_var_func = pre_des_var_funcs[0]
                self.remove_edge(pre_des_var_func, des_var)
                # If des_var has become a hole, remove it
                if self.node_is_hole(des_var):
                    self.add_edge(pre_des_var_func, doe_input_node)
            # Connect DOE input samples to doe_block
            self.add_edge(doe_input_node, doe_block)
            # Connect design variable as output from doe_block
            self.add_edge(doe_block, des_var)
        # Connect QOI nodes to the doe_block
        outs = []
        for var in qoi_nodes:
            # Connect regular variable version to doe_block
            self.add_edge(var, doe_block)
            # Create a DOE output samples node and connect it as output of the DOE
            doe_output_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[8])
            outs.append(doe_output_node)
            self.add_edge(doe_block, doe_output_node)

        return inps, outs

    def connect_surrogate_model_builder(self, sm_builder, input_x_data, input_y_data, label=None):
        """Method to connect a surrogate model builder node in the MDG. The surrogate model builder takes input data
        (generally from a DOE) and gives the definition of a surrogate model as output.

        :param sm_builder: new function node
        :type sm_builder: basestring
        :param input_x_data: list of nodes for which results were obtained (x-axis)
        :type input_x_data: list
        :param input_y_data: list of nodes with analysis results (y-axis)
        :type input_y_data: list
        :param label: label of the new function node
        :type label: basestring
        :return: output node with surrogate model definition
        :rtype: basestring
        """

        # Input assertions
        self.assert_node_exists_not(sm_builder)
        self.assert_node_exists(input_x_data)
        self.assert_node_exists(input_y_data)

        # Set label
        if label is None:
            label = str(sm_builder)

        # Add the surrogate model builder
        self.add_node(sm_builder,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[11],  # Surrogate model builder
                      label=label,
                      instance=1,
                      metadata=dict(input_x_data=[], input_y_data=[]))

        # Add the data for building as input to the builder
        for input_x_entry in input_x_data:
            self.add_edge(input_x_entry, sm_builder)
            self.nodes[sm_builder]['metadata']['input_x_data'].append(input_x_entry)
        for input_y_entry in input_y_data:
            self.add_edge(input_y_entry, sm_builder)
            self.nodes[sm_builder]['metadata']['input_y_data'].append(input_y_entry)

        # Add the surrogate model definition as output of the block
        output_node = '/{}/surrogateModels/{}/definition'.format(self.get_schema_root_name(input_x_entry[0]),
                                                                 label.replace('-', ''))
        assert not self.has_node(output_node), 'The node {} already exists.'.format(output_node)
        self.add_node(output_node, category='variable', instance=1, label='def{}'.format(label.replace('-', '')))
        self.add_edge(sm_builder, output_node)
        return output_node

    def connect_surrogate_model(self, sm, def_node, sm_inputs, sm_out_originals, label=None):
        """Method to connect a surrogate to the right nodes in the MDG.

        :param sm: new function node of surrogate model
        :type sm: basestring
        :param def_node: surrogate model definition node
        :type def_node: basestring
        :param sm_inputs: inputs of the surrogate model
        :type sm_inputs: list
        :param sm_out_originals: original outputs of the analysis box for which a surrogate model was created
        :type sm_out_originals: list
        :param label: label of the new function node
        :type label: basestring
        :return: output of the surrogate model (value approximated)
        :rtype: list
        """

        # Input assertions
        assert not self.has_node(sm), 'Node {} already exists in the graph.'.format(sm)
        assert self.has_node(def_node), 'Node {} is missing in the graph.'.format(def_node)

        # Set label
        if label is None:
            label = str(sm)

        # Add the surrogate model
        self.add_node(sm,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[12],  # Surrogate model
                      label=label,
                      instance=1)

        # Connect the surrogate model
        # Connect model definition as input
        self.add_edge(def_node, sm)

        # Connect the model inputs
        for sm_input in sm_inputs:
            self.add_edge(sm_input, sm)

        # Connect model results as output
        node_apprs = []
        for sm_out_or in sm_out_originals:
            node_appr = self.copy_node_as(sm_out_or, self.ARCHITECTURE_ROLES_VARS[10])
            self.add_edge(sm, node_appr)
            node_apprs.append(node_appr)

        return node_apprs

    def connect_boundary_determinator(self, bd, inputs, bounds, label=None):
        """Method to connect a boundary determinator method for building surrogate models. This boundary determinator is
        used in architectures like BLISS-2000 to adjust bounds for different cycles.

        :param bd: new function node
        :type bd: basestring
        :param inputs: inputs of the function
        :type inputs: list
        :param bounds: bounds output of the function
        :type bounds: list
        :param label: label of the new function node
        :type label: basestring
        :return:
        :rtype:
        """

        # Input assertions
        self.assert_node_exists_not(bd)
        self.assert_node_exists(bounds)

        # Set label
        if label is None:
            label = str(bd)

        # Add the surrogate model
        self.add_node(bd,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[10],  # Surrogate model boundary determinator
                      label=label,
                      instance=1)

        # Connect boundary determination inputs
        for input in inputs:
            self.add_edge(input, bd)

        # Connect the surrogate model boundary determinator output
        for bound in bounds:
            self.add_edge(bd, bound)

        return

    def manipulate_coupling_nodes(self, func_order, remove_feedback, remove_feedforward, converger=None,
                                  include_couplings_as_final_output=False, system_converger=False):
        """Method to manipulate the coupling nodes in a data graph in order to remove unwanted feedback/feedforward.

        :param func_order: the order of the functions to be analyzed
        :type func_order: list
        :param remove_feedback: setting on whether feedback coupling should be removed
        :type remove_feedback: bool
        :param remove_feedforward: setting on whether feedforward coupling should be removed
        :type remove_feedforward: bool
        :param converger: setting on whether the couplings should be linked to a converger
        :type converger: basestring or None
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        :param system_converger: converger is a system converger
        :type system_converger: bool
        """

        # Get all the relevant couplings
        if remove_feedback and remove_feedforward:
            direction = "both"
        elif remove_feedback and not remove_feedforward:
            direction = "backward"
        elif not remove_feedback and remove_feedforward:
            direction = "forward"
        else:
            raise IOError("Invalid settings on feedback and feedforward specific.")
        couplings = self.get_direct_coupling_nodes(func_order, direction=direction, print_couplings=False)

        # Manipulate the coupling nodes accordingly
        idx = 0
        for coupling in couplings:
            if system_converger and 'part_id' in self.nodes[coupling[0]] and 'part_id' in self.nodes[coupling[1]]:
                # Do not manipulate nodes if they are in the same partition
                if self.nodes[coupling[0]]['part_id'] == self.nodes[coupling[1]]['part_id']:
                    continue
                # Do not manipulate nodes if the partitions are solved in sequence
                if 'sequence_partitions' in self.graph['problem_formulation']:
                    skip_coupling = False
                    for sequence in self.graph['problem_formulation']['sequence_partitions']:
                        if self.nodes[coupling[0]]['part_id'] in sequence:
                            idx = sequence.index(self.nodes[coupling[0]]['part_id'])
                            if self.nodes[coupling[1]]['part_id'] in sequence[idx:]:
                                skip_coupling = True
                    if skip_coupling:
                        continue
            # Create initial guess coupling variable node
            ini_guess_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[0])
            # If there is no converger node, then just add an initial guess of the coupled node
            if converger is None:
                # Connect initial guess as input to coupled function
                self.add_edge(ini_guess_node, coupling[1])
            # If there is a converger node, then connect it accordingly
            elif self.nodes[converger]['architecture_role'] == self.ARCHITECTURE_ROLES_FUNS[2]:
                # Connect initial guess as input to the converger
                self.add_edge(ini_guess_node, converger)
                # Create coupling copy variable (coming from converger) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.copy_edge((coupling[2], coupling[1]), (coupling_copy_node, coupling[1]))
                # Connect original coupling node to the converger
                self.add_edge(coupling[2], converger)
            # If the converger node is an optimizer (IDF), then connect it accordingly
            elif converger == self.OPTIMIZER_STRING:
                idx += 1
                # Connect initial guess as input to the optimizer
                self.add_edge(ini_guess_node, converger)
                # Create coupling copy variable (coming from converger/optimizer) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.copy_edge((coupling[2], coupling[1]), (coupling_copy_node, coupling[1]))
                # Connect original and copied coupling node to the consistency constraint function
                self.add_edge(coupling[2], self.CONSCONS_STRING, equation_label='y{}'.format(idx))
                self.add_edge(coupling_copy_node, self.CONSCONS_STRING, equation_label='y{}c'.format(idx))
                # Make original coupling node a design variable
                self.mark_as_design_variable(coupling[2])
                # Create consistency constraint variables for each coupling and make them output of the function
                consistency_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[6])
                self.mark_as_constraint(consistency_node, '==', 0.0)
                self.add_edge(self.CONSCONS_STRING, consistency_node)
                self.add_equation((self.CONSCONS_STRING, consistency_node), 'y{}-y{}c'.format(idx, idx), 'Python')
                if 'consistency_nodes' in self.nodes[self.CONSCONS_STRING]:
                    self.nodes[self.CONSCONS_STRING]['consistency_nodes'].append(consistency_node)
                else:
                    self.nodes[self.CONSCONS_STRING]['consistency_nodes'] = [consistency_node]
            # Remove coupling edge between coupling variable -> function
            self.remove_edge(coupling[2], coupling[1])
            # If required, create final coupling variable node and let it come from the coupled function
            if converger and ('problem_role' in self.nodes[coupling[2]] or include_couplings_as_final_output):
                final_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[1])
                self.copy_edge([coupling[0], coupling[2]], [coupling[0], final_node])
                keep_original_coupling_node = False
            elif not converger and ('problem_role' in self.nodes[coupling[2]] or include_couplings_as_final_output):
                keep_original_coupling_node = True
            else:
                keep_original_coupling_node = False
            # Remove original coupling node if it has become an output
            if self.node_is_output(coupling[2]) and not keep_original_coupling_node:
                self.remove_node(coupling[2])

        return

    def create_mpg(self, name='MPG'):
        """Function to automatically create a MPG based on an MDG.

        :param name: name for the MPG graph
        :type name: basestring
        :return: unconnected MDG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """
        from graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(self, name=name)
        node_list = list(mpg.nodes)
        for node in node_list:
            if 'category' not in mpg.nodes[node]:
                raise AssertionError('category attribute missing for node: {}.'.format(node))
            elif mpg.nodes[node]['category'] == 'variable':
                mpg.remove_node(node)
            elif mpg.nodes[node]['category'] not in ['variable', 'function']:
                raise AssertionError('Node {} has invalid category attribute: {}.'.format(node,
                                                                                          mpg.nodes[node]['category']))
        mpg._add_diagonal_positions()
        return mpg

    def get_mpg(self, name='MPG'):
        """Create the MDAO process graph for a given FPG.

        :param name: name of the new graph
        :type name: basestring
        :return: MDAO process graph
        :rtype: MdaoProcessGraph
        """

        # Start-up checks
        logger.info('Composing MPG...')
        assert isinstance(name, basestring)
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        mdg = self.copy_as(MdaoDataGraph, as_view=True)

        # Local variables
        coor = mdg.COORDINATOR_STRING
        mdao_arch = mdg.graph['problem_formulation']['mdao_architecture']

        # Get the monolithic function ordering from the MDG and assign function lists accordingly.
        mg_function_ordering = mdg.graph['mg_function_ordering']
        if mdg.FUNCTION_ROLES[0] in mg_function_ordering:
            pre_functions = mg_function_ordering[mdg.FUNCTION_ROLES[0]]
        elif mdg.FUNCTION_ROLES[3] in mg_function_ordering:
            pre_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[3]]
            post_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[4]]
        coup_functions = mg_function_ordering[mdg.FUNCTION_ROLES[1]]
        post_functions = mg_function_ordering[mdg.FUNCTION_ROLES[2]]

        # Set up MDAO process graph
        mpg = mdg.create_mpg(name=name)

        # Make process step of the coordinator equal to zero
        mpg.nodes[coor]['process_step'] = 0

        # Add process edges for each architecture
        if mdao_arch == mdg.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            sequence = [coor] + pre_functions + coup_functions + post_functions
            mpg.add_process(sequence, 0, mdg, end_in_iterative_node=coor)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            conv = mdg.CONVERGER_STRING
            sequence = [coor] + pre_functions + [conv]
            mpg.add_process(sequence, 0, mdg)
            sequence2 = [conv] + coup_functions
            mpg.add_process(sequence2, mpg.nodes[sequence[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            if post_functions:
                sequence3 = [conv] + post_functions
                mpg.add_process(sequence3, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=coor)
            else:
                mpg.connect_nested_iterators(coor, conv)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[2]:  # IDF
            opt = mdg.OPTIMIZER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[3]:  # MDF
            opt = mdg.OPTIMIZER_STRING
            conv = mdg.CONVERGER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + [conv]
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg)
            sequence3 = [conv] + coup_functions
            mpg.add_process(sequence3, mpg.nodes[sequence2[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            sequence4 = [conv] + post_functions
            mpg.add_process(sequence4, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = mdg.OPTIMIZER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = mdg.DOE_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=doe)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = mdg.DOE_STRING
            conv = mdg.CONVERGER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + [conv]
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg)
            sequence3 = [conv] + coup_functions
            mpg.add_process(sequence3, mpg.nodes[sequence2[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            if post_functions:
                sequence4 = [conv] + post_functions
                mpg.add_process(sequence4, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=doe)
            else:
                mpg.connect_nested_iterators(doe, conv)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[7]:

            # Input checks
            assert 'partitions' in mdg.graph['problem_formulation'], 'Graph is not partitioned.'
            assert 'system_architecture' in mdg.graph['problem_formulation'], 'No architecture selected for ' \
                                                                              'distributed convergence.'

            # Load extra variables from fpg
            partitions = mdg.graph['problem_formulation']['partitions']
            system_arch = mdg.graph['problem_formulation']['system_architecture']

            if system_arch == 'unconverged-MDA':
                sequence1 = [coor] + pre_functions
                sequence2 = post_functions
                mpg.add_process_partitions(sequence1, partitions, sequence2, 0, mdg, end_in_iterative_node=coor)
            elif system_arch == 'converged-MDA':
                conv = mdg.CONVERGER_STRING
                sequence1 = [coor] + pre_functions + [conv]
                mpg.add_process(sequence1, 0, mdg)
                mpg.add_process_partitions([conv], partitions, [], mpg.nodes[conv]['process_step'], mdg,
                                           end_in_iterative_node=conv)
                sequence2 = [conv] + post_functions
                mpg.add_process(sequence2, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=coor)
            elif system_arch == 'IDF':
                opt = mdg.OPTIMIZER_STRING
                sequence1 = [coor] + pre_desvars_funcs + [opt]
                mpg.add_process(sequence1, 0, mdg)
                sequence2 = [opt] + post_desvars_funcs
                sequence3 = post_functions
                mpg.add_process_partitions(sequence2, partitions, sequence3, mpg.nodes[opt]['process_step'], mdg,
                                           end_in_iterative_node=opt)
                mpg.connect_nested_iterators(coor, opt)
            elif system_arch == 'MDF':
                opt = mdg.OPTIMIZER_STRING
                conv = mdg.CONVERGER_STRING
                sequence1 = [coor] + pre_desvars_funcs + [opt]
                mpg.add_process(sequence1, 0, mdg)
                sequence2 = [opt] + post_desvars_funcs + [conv]
                mpg.add_process(sequence2, mpg.nodes[opt]['process_step'], mdg)
                mpg.add_process_partitions([conv], partitions, [], mpg.nodes[conv]['process_step'], mdg,
                                           end_in_iterative_node=conv)
                sequence3 = [conv] + post_functions
                mpg.add_process(sequence3, mpg.nodes[conv]['converger_step'], mdg, end_in_iterative_node=opt)
                mpg.connect_nested_iterators(coor, opt)
            elif system_arch == 'unconverged-OPT':
                opt = mdg.OPTIMIZER_STRING
                sequence1 = [coor] + pre_desvars_funcs + [opt]
                mpg.add_process(sequence1, 0, mdg)
                sequence2 = [opt] + post_desvars_funcs
                sequence3 = post_functions
                mpg.add_process_partitions(sequence2, partitions, sequence3, mpg.nodes[opt]['process_step'], mdg,
                                           end_in_iterative_node=opt)
                mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[8]:  # CO
            distr_function_ordering = mdg.graph['distr_function_ordering']
            n_groups = len(distr_function_ordering[1])
            sys_opt, sub_opts = self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sequence1 = [coor] + distr_function_ordering[0][self.FUNCTION_ROLES[3]] + [sys_opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [sys_opt] + distr_function_ordering[0][self.FUNCTION_ROLES[2]]
            mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=sys_opt)
            for idx, subgroup in enumerate(distr_function_ordering[1]):
                sequence3 = [sys_opt, sub_opts[idx]]
                mpg.connect_nested_iterators(sys_opt, sub_opts[idx], direction='master->slave')
                sequence4 = [sub_opts[idx]] + subgroup[self.FUNCTION_ROLES[4]] + subgroup[self.FUNCTION_ROLES[1]] + \
                             subgroup[self.FUNCTION_ROLES[2]]
                mpg.add_process(sequence4, mpg.nodes[sequence3[-1]]['process_step'], mdg,
                                end_in_iterative_node=sub_opts[idx])
                mpg.connect_nested_iterators(sys_opt, sub_opts[idx])
            mpg.connect_nested_iterators(coor, sys_opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[9]:  # BLISS-2000
            distr_function_ordering = mdg.graph['distr_function_ordering']
            n_groups = len(distr_function_ordering[1])
            sys_opt, sys_conv, _, sub_smbds, sub_does, sub_opts, sub_smbs = \
                self.get_architecture_node_ids(mdao_arch, number_of_groups=n_groups)
            sequence1 = [coor] + distr_function_ordering[0][self.FUNCTION_ROLES[3]] + [sys_conv]
            mpg.add_process(sequence1, 0, mdg)
            for idx, subgroup in enumerate(distr_function_ordering[1]):
                sequence2 = [sys_conv] + subgroup[self.FUNCTION_ROLES[3]] + [sub_smbds[idx]] + [sub_does[idx]] + \
                            [sub_opts[idx]] + subgroup[self.FUNCTION_ROLES[4]] + subgroup[self.FUNCTION_ROLES[1]] + \
                            subgroup[self.FUNCTION_ROLES[2]]
                mpg.add_process(sequence2, mpg.nodes[sequence1[-1]]['process_step'], mdg,
                                end_in_iterative_node=sub_opts[idx])
                mpg.connect_nested_iterators(sub_does[idx], sub_opts[idx])
                sequence3 = [sub_does[idx]] + [sub_smbs[idx]] + [sys_opt]
                mpg.add_process(sequence3, mpg.nodes[sub_does[idx]]['converger_step'], mdg)
            sequence4 = [sys_opt] + distr_function_ordering[0][self.FUNCTION_ROLES[4]] + \
                        distr_function_ordering[0][self.FUNCTION_ROLES[1]] + \
                        distr_function_ordering[0][self.FUNCTION_ROLES[2]]
            mpg.add_process(sequence4, mpg.nodes[sequence3[-1]]['process_step'], mdg,
                            end_in_iterative_node=sequence4[0])
            mpg.connect_nested_iterators(sys_conv, sys_opt)
            mpg.connect_nested_iterators(coor, sys_conv)

        mpg.graph['process_hierarchy'] = mpg.get_process_hierarchy()

        logger.info('Composed MPG.')

        return mpg
