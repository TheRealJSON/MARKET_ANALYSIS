import re

class JSONLogicParser:
    def __init__(self) -> None:
        self.logic_gates = ['and']
        self.operators = ['<', '>', '<=', '>=', '==', '!=', '/', '+']
        self.function_names = ['min']

    def is_logic_gate(self, variable):
        if type(variable) is not str:
            return False # operator must be string value

        if (variable in self.logic_gates):
            return True
        
        return False

    def is_operator(self, variable):
        if type(variable) is not str:
            return False # operator must be string value
        
        if (variable in self.operators):
            return True
        
        return False
    
    def is_function(self, variable):
        if type(variable) is not str:
            return False # function must be string value
        
        if (variable in self.function_names):
            return True
        
        return False
    
    def parseLeafNode(self, leafNode):
        result = ''
        operand = ''

        first_key = list(leafNode.keys())[0]

        if first_key == 'var': # if it's a ending leaf / operand
            operand = leafNode['property']
            result = leafNode['var'] + '.' 
        
        if first_key == 'val':
            operand = leafNode['val']
        
        return result + str(operand)
    
    def parseBranchNode(self, branchNode):
        result = []
        current_node_value = list(branchNode.keys())[0] # use of Dictionary {} for Branches necessitates storage of value inside key
        child_nodes = list(branchNode.values())

        if self.is_operator(current_node_value): # if node requires inorder parsing 
            result = '(' + self.inorderTraversal(child_nodes[0][0])
            result = str(result) + ' ' + str(current_node_value) + ' '
            result = result + self.inorderTraversal(child_nodes[0][1]) + ')'
        elif self.is_function(current_node_value): # if node requires function-version of preorder parsing
            result = self.inorderTraversal(child_nodes[0][0])
            result = result + ',' + self.inorderTraversal(child_nodes[0][1])
            result = str(current_node_value) + '(' + result + ') '
        elif self.is_logic_gate(current_node_value): # if node requires in-order parsing with >2 child nodes
            result = '('
            for child_node in child_nodes[0]:
                result = result + self.inorderTraversal(child_node)
                result = str(result) + ' ' + str(current_node_value) + ' '
            
            result = result.strip().rsplit(' ', 1)[0] # remove trailing [current_node_value] (probably a 'and')
            result = result + ')'

        return result

    def inorderTraversal(self, root):
        result = []
        current_node = list(root.keys())[0]

        # if current node is NOT an operator then root was an edge leaf/node
        # therefore, do processing for edge leaf
        if not self.is_operator(current_node) and not self.is_function(current_node) and not self.is_logic_gate(current_node):  
            return self.parseLeafNode(root)

        result = self.parseBranchNode(root)

        return result
    
    """
    Wrapper method used to convey the purpose of doing the INORDER traversal

    :param jsonExpressionTree: Dictionary that results from reading an expression tree represented in JSON
    :return: a String expression representation
    """
    def convertJSONExpressionTreeToString(self, jsonExpressionTree):
        print(type(jsonExpressionTree))
        # TODO: case when unexpected format/structture?
        return self.inorderTraversal(jsonExpressionTree)
    
    @staticmethod
    def replaceStringPlaceholdersWithValues(string_with_placeholders, runtime_values):
        placeholder_regex = '[_a-zA-Z]+\.[_a-zA-Z]+' # i.e. second_candle.length
        placeholder_candle_regex = '[_a-zA-Z]+\.'    # i.e. second_candle
        placeholder_property_regex = '\.[_a-zA-Z]+'  # i.e. length

        runtime_string = string_with_placeholders 

        runtime_value_placeholders = re.findall(placeholder_regex, string_with_placeholders)

        for property_placeholder in runtime_value_placeholders:
            object_identifier = re.search(placeholder_candle_regex, property_placeholder).group(0).replace('.', '')
            property_identifier = re.search(placeholder_property_regex, property_placeholder).group(0).replace('.', '')

            runtime_value = str(runtime_values[object_identifier][property_identifier])

            runtime_string = runtime_string.replace(property_placeholder, runtime_value)
    
        return runtime_string