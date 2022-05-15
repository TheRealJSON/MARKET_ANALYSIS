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
        
        function_names = ['min', 'within']

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

    
    def convertJSONExpressionTreeToString(self, jsonExpressionTree):
        # TODO: case when unexpected format/structture?
        return self.inorderTraversal(jsonExpressionTree)
    
    @staticmethod
    def replaceStringPlaceholdersWithValues(string_with_placeholders, runtime_values):
        placeholder_regex = '[_a-zA-Z]+\.[_a-zA-Z]+' # i.e. second_candle.length
        placeholder_candle_regex = '[_a-zA-Z]+\.'
        placeholder_property_regex = '\.[_a-zA-Z]+'

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

    # Replaces method references within an expression string
    # with their return/resolved/evaluated values.
    # ASSUMES EVERY METHOD HAS 3 PARAMETERS. TODO: Make better! might need to delegate based on param count
    def resolveCustomFunctionsInRuntimeExpression(expression_str):
        # for each custom function
        # retrieve each occurence and its parameters from the given expression
        # resolve each occurence
        # plug result into expression
        custom_functions = ["within"]
        new_expression_str = expression_str

        #function_parameter_regex = "([0-9\.a-z]*)"
        function_parameter_regex = "(([A-Z0-9]|\.)*(,|\)))"
        custom_function_regex_template = "PLACEHOLDER\([0-9\,\.]*\)"
        custom_function_regex_runtime = custom_function_regex_template

        for function_name in custom_functions: 
            custom_function_regex_runtime = custom_function_regex_template.replace("PLACEHOLDER", function_name)
            for function_call_regex_match in re.findall(custom_function_regex_runtime, expression_str):
                # Get dynamic reference to current method
                method = getattr(globals()["JSONLogicParser"], function_name)
                
                # Extract parameters to pass into the method - ASSUME 3 PARAMETERS
                param_regex_matches = re.findall(function_parameter_regex, function_call_regex_match)
                first_parameter = param_regex_matches[0][0].rstrip(",)") # The regex pat results in trailing , or )
                second_parameter = param_regex_matches[1][0].rstrip(",)")# The regex pat results in trailing , or )
                third_parameter = param_regex_matches[2][0].rstrip(",)") # The regex pat results in trailing , or )

                print(function_call_regex_match)
                print("1st: " + first_parameter)
                print("2st: " + second_parameter)
                print("3st: " + third_parameter)

                #for parameter_regex_match in re.findall(function_parameter_regex, function_call_regex_match):
                #    print('woiiii')
                #    print (parameter_regex_match[0])
        
                function_call_result = method(first_parameter, second_parameter, third_parameter) # ASSUME 3 PARAMS FOR CUSTOM FUNCTIONS
                print("FINISHED calling method")
                # plug result into the expression string
                new_expression_str = new_expression_str.replace(function_call_regex_match, str(function_call_result))

        return new_expression_str

