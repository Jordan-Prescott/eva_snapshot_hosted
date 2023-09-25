class Node:
    def __init__(
            self, name, start_node, node_type, priority, say, condition_transition, handoff_queue, condition_sms
    ) -> None:
        """ Nodes are building blocks of Flows/ FAQs they make up the conversation design within them. Each node can be
        1 of 5 different types in the PolyAI platform as the user interacts with the AI the conversation is passed to
        each node.

        :param name: Name of node often related to action/ purpose e.g. ActivitiesTicketsAffirm.
        :param start_node: Entry point to conversation, although flows can have multiple start nodes here we define one.
        :param node_type: 1 of 5 types: Interactive, Informational, Scripting, Transfer, End Node. NOT TO BE CONFUSED
        NODES IN OUTPUT.
        :param priority: Level of priority a flow has the higher, the more likely to be triggered.
        :param say: Utterance that EVA will speak to the user.
        :param condition_transition: Condition of transition based upon what the user says next will determine the next
        node the conversation will transition to.
        :param handoff_queue: Destination extension number/ external DID where call will be transferred to.
        :param condition_sms: Condition of SMS based upon what the user says next will determine the contents
        of the SMS sent.
        """

        self.name = name
        self.start_node = start_node
        self.node_type = node_type
        self.priority = priority
        self.say = say
        self.condition_transition = condition_transition
        self.handoff_queue = handoff_queue
        self.condition_sms = condition_sms


class Flow:
    def __init__(
            self, name, nodes: list[Node]
    ) -> None:
        """Usually a defined topic of conversation such as Airport or Coffee built up of nodes that makes up the
        conversational design.

        :param name: Flow name.
        :param nodes: List of the nodes that make up the flow.
        """

        self.name = name
        self.nodes = nodes


class Variant:
    def __init__(
            self, variant_id, handoff=None, sms=None, flows=None
    ) -> None:
        """Hosted inside a Project (Brand) a Variant is a single hotel within the project.

        :param variant_id: Unique ID of Variant.
        :param handoff: All handoff locations for a single variant.
        :param sms: All SMS content messages for a single variant.
        :param flows: A list of all ACTIVE FLOWS that are built within the variant.
        """

        self.variant_id = variant_id
        self.handoff = handoff if handoff else {}
        self.sms = sms if sms else {}
        self.flows = flows if flows else []
