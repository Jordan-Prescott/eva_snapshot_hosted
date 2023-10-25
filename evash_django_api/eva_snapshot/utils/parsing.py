import ast
import logging
import re
import graphviz

from eva_snapshot.utils.store.data_entities import Node, Flow

LOGGER = logging.getLogger("EVASnapshot v2")
DEFAULT_CONDITION = "_DEFAULT_CONDITION"


def flow_module(flow_name, ast_mod_raw: ast.Module, file_in_list: list, files_not_needed) -> Flow:
    """Parses ast module of files NOT in files_not_needed returning a formatted Flow object
    with a list of Node objects.

    :param flow_name: Flow name
    :param ast_mod_raw: ast module object of flow python file
    :param file_in_list: Flow python as a list by line
    :param files_not_needed: List of files that should not be parsed
    """
    if flow_name not in files_not_needed:  # Used to parse only files needed
        nodes = []
        name = flow_name
        start_node = False
        start_node_flag = False

        for b in ast_mod_raw.body:
            if isinstance(b, ast.ClassDef):
                node_type = None
                priority = ""
                say = ""
                condition_transition = {}
                handoff_queue = {}
                condition_sms = {}

                for class_body in b.body:
                    if isinstance(class_body, ast.Assign):
                        """
                        Gets the node_type, priority and start_node if priority assigned. This is looking at the variables
                        assigned under each class definition.

                        NOTE: start_node is assumed if the class has a priority (conversation entry point).
                        """
                        if class_body.targets[0].id == "node_type":
                            node_type = class_body.value.value
                        if class_body.targets[0].id == "priority":
                            if not start_node_flag:
                                start_node = True
                                start_node_flag = True  # flag start node found RULE: 1 per flow
                            priority = file_in_list[class_body.value.lineno - 1] \
                                .split("=")[-1].strip(" ").strip("\n")

                    if isinstance(class_body, ast.FunctionDef):
                        """
                        Gets handoff_queue and condition_sms if assigned in the condition method.

                        NOTE: Sometimes these variables are defined in this method especially is the flow is only made up of
                        one node.
                        """
                        if class_body.name == "condition": # Node Method
                            for transition_body in class_body.body:
                                if isinstance(transition_body, ast.If):
                                    for i in transition_body.body:
                                        if isinstance(i, ast.Assign):
                                            target = i.targets[0]
                                            if "attr" in target._fields:
                                                if target.attr == "handoff_queue_id":
                                                    handoff_queue[
                                                        file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                    ] = i.value.value
                                                if target.attr == "sms_content_key":
                                                    condition_sms[
                                                        file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                    ] = i.value.value

                                if isinstance(transition_body, ast.Assign):
                                    target = transition_body.targets[0]
                                    if "attr" in target._fields:
                                        if transition_body.targets[0].attr == "handoff_queue_id":
                                            handoff_queue[DEFAULT_CONDITION] = transition_body.value.value
                                        if transition_body.targets[0].attr == "sms_content_key":
                                            condition_sms[DEFAULT_CONDITION] = transition_body.value.value

                        if class_body.name == "say": # Node Method
                            """
                            Gets utterance key from node.
                            
                            NOTE: Assuming that the node says one thing. If Repeat its better for output to have just 
                            one.
                            """
                            say = class_body.body[0].value.value

                        if class_body.name == "transition":  # Node Method
                            """
                            If return get the condition and destination node of the return.
                            If assign get the handoff_queue or condition_sms
                            """
                            for transition_body in class_body.body:
                                if isinstance(transition_body, ast.If):
                                    for i in transition_body.body:
                                        if isinstance(i, ast.Return):
                                            try:
                                                condition_transition[
                                                    file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                ] = i.value.value
                                            except AttributeError as e: # If other logic between condition and return
                                                LOGGER.error(e)
                                                condition_transition[
                                                    file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                ] = i.value.dims[0].n
                                        if isinstance(i, ast.Assign):
                                            target = i.targets[0]
                                            if "attr" in target._fields:
                                                if target.attr == "handoff_queue_id":
                                                    try:
                                                        handoff_queue[
                                                            file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                        ] = i.value.value
                                                    except AttributeError:
                                                        handoff_queue[
                                                            file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                        ] = i.value.args[1].value                              

                                                if target.attr == "sms_content_key":
                                                    condition_sms[
                                                        file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                    ] = i.value.value
                                if isinstance(transition_body, ast.Return):
                                    try:
                                        condition_transition[
                                            file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                        ] = transition_body.value.value
                                    except AttributeError as e:
                                        LOGGER.error(e)
                                        condition_transition[
                                            file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                        ] = transition_body.value.dims[0].n


                                if isinstance(transition_body, ast.Assign):
                                    target = transition_body.targets[0]
                                    if "attr" in target._fields:
                                        if transition_body.targets[0].attr == "handoff_queue_id":
                                            try:
                                                handoff_queue[
                                                    file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                ] = transition_body.value.value
                                            except AttributeError as e:
                                                LOGGER.error(e)
                                                handoff_queue[
                                                    file_in_list[transition_body.lineno - 1].strip(" ").strip("\n")
                                                ] = transition_body.value.args[1].value

                                        if transition_body.targets[0].attr == "sms_content_key":
                                            condition_sms[
                                                transition_body.targets[0].attr
                                            ] = transition_body.value.value

                nodes.append(Node(
                    b.name,
                    start_node,
                    node_type,
                    priority,
                    say,
                    condition_transition,
                    handoff_queue,
                    condition_sms
                ))
                start_node = False
        LOGGER.info(f"{flow_name} parsed.")
        return Flow(flow_name, nodes)
    else:
        LOGGER.info(f"{flow_name} found.")


class UniverseGraphVizModule:
    def __init__(self) -> None:
        """

        """

        self.graphs = []
        self.universe = graphviz.Digraph()

    def build_universe(self, output_dir) -> None:
        """Loops through self.graphs (dot Graphs) and adds all to single view creating single universe
        view of all virtual agent understands.

        :param output_dir: Location the generated file will be outputted.
        :return: None
        """

        for graph in self.graphs:
            self.universe.subgraph(graph)

        self.universe.render(directory=output_dir,
                             filename="06 - EVA UNIVERSE",
                             format="svg",
                             cleanup=True).replace('\\', '/')


class GraphvizModule:
    def __init__(self, flow: Flow, output_dir, data_store) -> None:
        """Takes in Flow object which references data in data_store and using these two objects it parses the flow
        to generate a graphviz object. That object is then rendered using the graphviz package to generate a single flow
        graph in the svg format and stored in the output_dir passed into the class.

        :param flow: Complete Flow object used to generate graphviz graph.
        :param output_dir: Location where each rendered graph will be stored.
        :param data_store: Contains details such as SMS content and Utterances used and referenced in Flow object. Data
        pulled from store when referenced in flow.
        """

        self.convert_all_intents_matched_re = re.compile(
            "if context\.all_intents_triggered\((.*)\)"
        )
        self.convert_any_intents_matched_re = re.compile(
            "if context\.any_intents_triggered\((.*)\)"
        )
        self.convert_if_intents_matched_re = re.compile(
            "if \"(.*)\" in intents:" or "if \"(.*)\" in context.intents:"
        )
        self.flow_node = {
            'shape': 'box',
            'style': 'filled',
            'margin': '0.2',
            'color': '#01162a',
            'fontname': 'Arial',
            'fontcolor': 'white'}
        self.interactive_node = {
            'shape': 'Mrecord',
            'penwidth': '2',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#594d6b',
            'color': '#292037'}
        self.info_node = {
            'shape': 'Mrecord',
            'penwidth': '2',
            # 'margin': '0.2',
            'width': '2',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#9d6fb8',
            'color': '#6E4E81',
        }
        self.script_node = {
            'shape': 'Mrecord',
            'penwidth': '2',
            'width': '2',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#b37196',
            'color': '#7B4F68'
        }
        self.transfer_node = {
            'shape': 'Mrecord',
            'penwidth': '2',
            'width': '2',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#c87273',
            'color': '#c87273'
        }
        self.sms_node = {
            'shape': 'Mrecord',
            'penwidth': '2',
            'width': '2',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#c87273',
            'color': '#844B4C'
        }

        """
        This node is not actually part of the PolyAI platform this is to indicate the next flow/ node that is 
        not inside the current flow. For example main.AnythingElse is being passed back to main and EVA will ask
        'Is there anything else I can help with?' this node is to show that in the flow it has now moved on and out 
        of this flow.
        """
        self.move_on_node = {
            'shape': 'box',
            'style': 'filled',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'fillcolor': '#ffbc52',
            'color': '#ffbc52'
        }
        self.node_mapping = {
            'interactive': self.interactive_node,
            'information': self.info_node,
            'scripting': self.script_node,
            'transfer': self.transfer_node,
            'sms_node': self.sms_node,
            'move_on': self.move_on_node
        }
        self.dot = graphviz.Digraph()
        self.dot.attr(name=f"cluster_{flow.name}", label=flow.name, fontname='Arial',
                      fontcolor='white', rankdir="TB")

        def _text_formatter(text):
            result_string = text.replace("{", "").replace("}", "")
            return re.sub("(.{35})", "\\1\\\\n", result_string, 0, re.DOTALL)

        def _title_formatter(title):
            return re.sub(r"(\w)([A-Z])", r"\1\2", title)

        # build nodes
        self.dot.node(f"{flow.name}_flow_node", flow.name, self.flow_node)
        for node in flow.nodes:
            node.name = _title_formatter(node.name)
            node_built_flag = False

            node_label = node.name  # Node ID: Needs to be in first position
            if node.say:  # If agent speaks get utterance and format for output.
                try:
                    utt = data_store.utterance_dict.get(node.say.split(".")[1], "")
                except KeyError as e:
                    LOGGER.error(e)
                    utt = False

                if not utt:
                    LOGGER.error(f"Failed to find utterance: {node.say}")
                    formatted_utt = f"[ERROR] FAILED TO FIND UTTERANCE: {node.say}"
                else:
                    try:
                        utt = utt["text"][f'if variant == "{data_store.variant.variant_id}"']   
                    except KeyError:
                        utt = utt["text"]["default"]
                    formatted_utt = _text_formatter(utt)
                node_label += " | " + formatted_utt

            if node.condition_sms:  # If node sends SMS display setting content and make child node with sms content
                # Parent Nodes: Current node
                try:
                    self.dot.node(f"{flow.name}_{node.name}", "{" + node.name + " | SMS Content: " +
                                  node.condition_sms['sms_content_key'] + "}", self.node_mapping[node.node_type])
                    node_built_flag = True
                except KeyError as e:
                    LOGGER.error(e)
                    pass  # Node has multiple conditions and sends direct to transfer node

                # Child Nodes: SMS node displaying the content
                for value in node.condition_sms.values():
                    child_label = _title_formatter(value)

                    try:
                        sms_content = data_store.variant.sms[value]
                    except KeyError:
                        sms_content = False
                    if not sms_content:
                        LOGGER.error(f"Failed to find sms: {value}")
                        formatted_sms = f"[ERROR] FAILED TO FIND SMS: {value}"
                    else:
                        formatted_sms = _text_formatter(sms_content)
                    child_label += " | " + formatted_sms

                    self.dot.node(f"{flow.name}_send_sms_{value}", "{" + child_label + "}", self.node_mapping['sms_node'])
                    node_built_flag = True

            if node.handoff_queue:  # If node hands off create current node and node with handoff queue and number

                # Parent Node: Current node
                node_label = node.name
                if node.say:
                    node_label += " | " + formatted_utt

                if node.start_node:
                    self.dot.node(f"{flow.name}_start_node", "{" + node_label + "}", self.node_mapping[node.node_type])
                else:
                    self.dot.node(f"{flow.name}_{node.name}", "{" + node_label + "}", self.node_mapping[node.node_type])
                    node_built_flag = True

                # Child Nodes: Node displaying handoff queue and number
                for value in node.handoff_queue.values():
                    child_label = _title_formatter(value)

                    try:
                        try:
                            transfer_num = data_store.variant.handoff[value]["internal_extension"]
                        except KeyError:
                            LOGGER.error(f"Internal_extension not found: {value}")
                            transfer_num = data_store.variant.handoff[value]["external_number"]
                    except KeyError:
                        LOGGER.error(f"External_extension not found: {value}")
                        transfer_num = False

                    if not transfer_num:
                        LOGGER.error(f"Failed to find handoff: {value}")
                        transfer_num = f"[ERROR] FAILED TO FIND HANDOFF: {value}"
                    else:
                        child_label += " | " + transfer_num

                    self.dot.node(f"{flow.name}_transfer_to_{value}", "{" + child_label + "}", self.node_mapping['transfer'])
                    node_built_flag = True

            if node.condition_transition:  # If node passes to node outside of current flow or global nodes create
                for value in node.condition_transition.values():
                    if "main." in value:  # Moves back to main
                        next_node = _title_formatter(value.split(".")[1])
                        self.dot.node(f"{flow.name}_move_onto_{next_node}", next_node, self.node_mapping['move_on'])
                    elif value == 'send_sms.StartNode' or value == 'handoff.DirectHandoffNode':
                        break
                    elif f"{flow.name}." not in value:  # Moves to another flow
                        self.dot.node(f"{flow.name}_move_onto_{value}", value, self.node_mapping['move_on'])

            if node.start_node:  # If start_node not created above capture here.
                self.dot.node(f"{flow.name}_start_node", "{" + node_label + "}", self.node_mapping[node.node_type])
            elif not node_built_flag:  # If note start node and node not built above capture here.
                self.dot.node(f"{flow.name}_{node.name}", "{" + node_label + "}", self.node_mapping[node.node_type])
        LOGGER.info("Nodes built")

        # build edges
        self.dot.edge(f"{flow.name}_flow_node", f"{flow.name}_start_node")
        for node in flow.nodes:
            edge_built_flag = False

            edge_label = ""
            if node.condition_sms:  # If node sends SMS connected current node and SMS node
                for value in node.condition_sms.values():
                    self.dot.edge(f"{flow.name}_{node.name}", f"{flow.name}_send_sms_{value}")

            if node.handoff_queue:  # If node hands off connect current node to transfer node
                for value in node.handoff_queue.values():
                    if node.start_node:
                        self.dot.edge(f"{flow.name}_start_node", f"{flow.name}_transfer_to_{value}")
                        edge_built_flag = True
                    else:
                        self.dot.edge(f"{flow.name}_{node.name}", f"{flow.name}_transfer_to_{value}")

            if node.condition_transition:  # If node transitions to another node connect current node with other nodes
                for key, value in node.condition_transition.items():
                    if "main." in value:  # Moves back to Main
                        next_node = _title_formatter(value.split(".")[1])
                        if node.start_node:
                            self.dot.edge(f"{flow.name}_start_node", f"{flow.name}_move_onto_{next_node}")
                        else:
                            self.dot.edge(f"{flow.name}_{node.name}", f"{flow.name}_move_onto_{next_node}")
                    elif value == "send_sms.StartNode" or value == "handoff.DirectHandoffNode":
                        break
                    elif f"{flow.name}." not in value:  # Moves to another flow
                        if node.start_node:
                            self.dot.edge(f"{flow.name}_start_node", f"{flow.name}_move_onto_{value}")
                        else:
                            self.dot.edge(f"{flow.name}_{node.name}", f"{flow.name}_move_onto_{value}")

                    else:
                        # if match_int := self.convert_any_intents_matched_re.findall(
                        #     key
                        # ):
                        #     edge_label = match_int[0]
                        # elif match_int := self.convert_any_intents_matched_re.findall(
                        #     key
                        # ):
                        #     edge_label = match_int[0]
                        # elif match_int := self.convert_any_intents_matched_re.findall(
                        #     key
                        # ):
                        #     edge_label = match_int[0]

                        if node.start_node:  # If start node connect to next node. Used for Flow Node -> Start Node
                            node_formatted = _title_formatter(value.split(".")[1])
                            self.dot.edge(f"{flow.name}_start_node", f"{flow.name}_{node_formatted}")
                        elif not edge_built_flag:  # If edge not built above capture here
                            node_formatted = _title_formatter(value.split(".")[1])
                            self.dot.edge(f"{flow.name}_{node.name}", f"{flow.name}_{node_formatted}")
        LOGGER.info("Edges built")

        self.dot.render(directory=output_dir, filename=flow.name, format="svg", cleanup=True).replace('\\', '/')
        LOGGER.info(f"RENDERED: {flow.name}")
