from ast import And
import re

class JSONLogicParser:

    def __init__(self) -> None:
        pass

    def is_logic_gate(self, variable):
        if type(variable) is not str:
            return False # operator must be string value

        logic_gates = ['and']

        if (variable in logic_gates):
            return True
        
        return False

    def is_operator(self, variable):
        if type(variable) is not str:
            return False # operator must be string value
        
        # TODO: when the operator isn't defined here, it results in expression evaluation error. Should handle that case
        operators = ['<', '>', '<=', '>=', '=', '!=', '/', '+', '-'] 

        if (variable in operators):
            return True
        
        return False
    
    def is_function(self, variable):
        if type(variable) is not str:
            return False # function must be string value
        
        function_names = ['min', 'within', 'multiply']

        if (variable in function_names):
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
            # if function then could be more than 2 branches/children
            result = ''
            for child_node in child_nodes[0]:
                result = result + ',' + self.inorderTraversal(child_node)
            result = str.lstrip(result, ',') # remove first comma
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
        current_node = list(root.keys())[0]

        # if current node is NOT an operator/function/logic_gate then root was an edge leaf/node
        # therefore, do processing for edge leaf
        if not self.is_operator(current_node) and not self.is_function(current_node) and not self.is_logic_gate(current_node):  
            return self.parseLeafNode(root)

        return self.parseBranchNode(root)

    """
    Wrapper method used to convey the purpose of doing the INORDER traversal
    :param jsonExpressionTree: Dictionary that results from reading an expression tree represented in JSON
    :return: a String expression representation
    """
    def convertJSONExpressionTreeToString(self, jsonExpressionTree):
        # TODO: case when unexpected format/structture?
        return self.inorderTraversal(jsonExpressionTree)
    
    @staticmethod
    def replaceStringPlaceholdersWithValues(string_with_placeholders, runtime_values):
        placeholder_regex = '[_a-zA-Z]+\.[_a-zA-Z]+' # i.e. second_candle.length
        placeholder_candle_regex = '[_a-zA-Z]+\.'    # i.e. second_candle
        placeholder_property_regex = '\.[_a-zA-Z]+'  # i.e. length

        runtime_string = string_with_placeholders # reset for current segment/frame iteration

        runtime_value_placeholders = re.findall(placeholder_regex, string_with_placeholders)


        for value_placeholder in runtime_value_placeholders:
            object_identifier = re.search(placeholder_candle_regex, value_placeholder).group(0).replace('.', '')
            property_identifier = re.search(placeholder_property_regex, value_placeholder).group(0).replace('.', '')

            runtime_value = str(runtime_values[object_identifier][property_identifier])

            runtime_string = runtime_string.replace(value_placeholder, runtime_value)
    
        return runtime_string
    
    def within(value, first_boundary_value, second_boundary_value):
        if (second_boundary_value > first_boundary_value): # if the range is positive
            return eval(value + ' > ' + first_boundary_value + ' and ' + value + ' < ' + second_boundary_value) #TODO: eval() bad

        # otherwise it's a negative range so the test for the codnition is different
        return eval(value + ' < ' + first_boundary_value + ' and ' + value + ' > ' + second_boundary_value) #TODO: eval() bad

    def multiply(value, multiplier):
        return float(value) * float(multiplier)


    # Replaces method references within an expression string
    # with their return/resolved/evaluated values.
    # ASSUMES EVERY METHOD HAS 3 PARAMETERS. TODO: Make better! might need to delegate based on param count
    def resolveCustomFunctionsInRuntimeExpression(expression_str):
        # for each custom function
        # retrieve each occurence and its parameters from the given expression
        # resolve each occurence
        # plug result into expression
        custom_functions = ["within", "multiply"]
        new_expression_str = expression_str

        #function_parameter_regex = "([0-9\.a-z]*)"
        function_parameter_regex = "((-*[A-Z0-9]|\.)*(,|\)))"
        custom_function_regex_template = "PLACEHOLDER\(-*[0-9\,\.]*\)"
        custom_function_regex_runtime = custom_function_regex_template

        for function_name in custom_functions: 
            custom_function_regex_runtime = custom_function_regex_template.replace("PLACEHOLDER", function_name)
            for function_call_regex_match in re.findall(custom_function_regex_runtime, expression_str):
                # Get dynamic reference to current method so we can execute it dynamically
                method = getattr(globals()["JSONLogicParser"], function_name)

                # Extract parameters to pass into the method
                param_regex_matches = re.findall(function_parameter_regex, function_call_regex_match)
                param_value_list = []
                for i in range(len(param_regex_matches)): # could be any number of parameters therefore base on regex match length
                    param_value_list.append(param_regex_matches[i][0].rstrip(",)")) # The regex pat results in trailing , or )

                # At the moment there is only 2-3 params. Need to refactor when new methods added.
                if len(param_value_list) == 2:
                    function_call_result = method(param_value_list[0], param_value_list[1]) # ASSUME 3 PARAMS FOR CUSTOM FUNCTIONS
                else: # will be 3
                    function_call_result = method(param_value_list[0], param_value_list[1], param_value_list[1]) # ASSUME 3 PARAMS FOR CUSTOM FUNCTIONS

                #function_call_result = method(first_parameter, second_parameter, third_parameter) # ASSUME 3 PARAMS FOR CUSTOM FUNCTIONS
                # plug result into the expression string
                new_expression_str = new_expression_str.replace(function_call_regex_match, str(function_call_result))

        return new_expression_str

